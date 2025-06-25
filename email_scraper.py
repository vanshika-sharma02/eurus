#!/usr/bin/env python3
"""
Web Email and Name Scraper
Extracts email addresses and associated names from web pages.
"""

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Tuple, Set
import json

class EmailNameScraper:
    def __init__(self, delay=1):
        """
        Initialize the scraper with optional delay between requests.
        
        Args:
            delay (int): Delay in seconds between requests to be respectful to servers
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Email regex pattern
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Name patterns - common formats for names near emails
        self.name_patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last
            r'([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)',  # First M. Last
            r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Middle Last
            r'([A-Z]{2,}\s+[A-Z][a-z]+)',  # FIRST Last or similar
        ]
    
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract email addresses from text."""
        emails = set()
        matches = self.email_pattern.findall(text)
        for match in matches:
            emails.add(match.lower())
        return emails
    
    def find_names_near_email(self, text: str, email: str, context_window: int = 100) -> List[str]:
        """
        Find potential names near an email address in the text.
        
        Args:
            text (str): The text to search in
            email (str): The email address to find names near
            context_window (int): Number of characters to look around the email
        
        Returns:
            List[str]: List of potential names found near the email
        """
        names = []
        
        # Find the position of the email in the text
        email_pos = text.lower().find(email.lower())
        if email_pos == -1:
            return names
        
        # Extract context around the email
        start = max(0, email_pos - context_window)
        end = min(len(text), email_pos + len(email) + context_window)
        context = text[start:end]
        
        # Look for name patterns in the context
        for pattern in self.name_patterns:
            matches = re.findall(pattern, context)
            names.extend(matches)
        
        return list(set(names))  # Remove duplicates
    
    def extract_from_contact_sections(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Extract emails and names from common contact sections.
        
        Returns:
            List[Tuple[str, str]]: List of (email, name) tuples
        """
        results = []
        
        # Common selectors for contact information
        contact_selectors = [
            '[class*="contact"]',
            '[class*="staff"]',
            '[class*="team"]',
            '[class*="member"]',
            '[class*="employee"]',
            '[id*="contact"]',
            '[id*="staff"]',
            '[id*="team"]',
        ]
        
        for selector in contact_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text()
                emails = self.extract_emails_from_text(text)
                
                for email in emails:
                    names = self.find_names_near_email(text, email)
                    if names:
                        for name in names[:1]:  # Take the first/best name
                            results.append((email, name))
                    else:
                        results.append((email, ""))
        
        return results
    
    def scrape_page(self, url: str) -> Dict:
        """
        Scrape a single page for emails and names.
        
        Args:
            url (str): URL of the page to scrape
            
        Returns:
            Dict: Dictionary containing scraped data
        """
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get all text content
            text = soup.get_text()
            
            # Extract all emails
            all_emails = self.extract_emails_from_text(text)
            
            # Try to find names associated with emails
            email_name_pairs = []
            
            # First, try to extract from contact sections
            contact_pairs = self.extract_from_contact_sections(soup)
            email_name_pairs.extend(contact_pairs)
            
            # For remaining emails, try to find names in the general text
            found_emails = {pair[0] for pair in email_name_pairs}
            remaining_emails = all_emails - found_emails
            
            for email in remaining_emails:
                names = self.find_names_near_email(text, email)
                if names:
                    email_name_pairs.append((email, names[0]))
                else:
                    email_name_pairs.append((email, ""))
            
            # Remove duplicates while preserving order
            seen = set()
            unique_pairs = []
            for email, name in email_name_pairs:
                if email not in seen:
                    unique_pairs.append((email, name))
                    seen.add(email)
            
            result = {
                'url': url,
                'emails_found': len(unique_pairs),
                'data': [{'email': email, 'name': name} for email, name in unique_pairs],
                'status': 'success'
            }
            
            print(f"Found {len(unique_pairs)} emails on {url}")
            
            time.sleep(self.delay)  # Be respectful to the server
            
            return result
            
        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'emails_found': 0,
                'data': [],
                'status': f'error: {str(e)}'
            }
    
    def scrape_multiple_pages(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple pages.
        
        Args:
            urls (List[str]): List of URLs to scrape
            
        Returns:
            List[Dict]: List of results for each page
        """
        results = []
        for url in urls:
            result = self.scrape_page(url)
            results.append(result)
        
        return results
    
    def save_results(self, results: List[Dict], output_format: str = 'csv', filename: str = 'scraped_emails'):
        """
        Save results to file.
        
        Args:
            results (List[Dict]): Results from scraping
            output_format (str): 'csv', 'json', or 'excel'
            filename (str): Base filename (extension will be added)
        """
        # Flatten the data
        all_data = []
        for result in results:
            url = result['url']
            status = result['status']
            for item in result['data']:
                all_data.append({
                    'url': url,
                    'email': item['email'],
                    'name': item['name'],
                    'status': status
                })
        
        if not all_data:
            print("No data to save.")
            return
        
        if output_format.lower() == 'csv':
            df = pd.DataFrame(all_data)
            df.to_csv(f'{filename}.csv', index=False)
            print(f"Results saved to {filename}.csv")
        
        elif output_format.lower() == 'json':
            with open(f'{filename}.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {filename}.json")
        
        elif output_format.lower() == 'excel':
            df = pd.DataFrame(all_data)
            df.to_excel(f'{filename}.xlsx', index=False)
            print(f"Results saved to {filename}.xlsx")

def main():
    parser = argparse.ArgumentParser(description='Scrape emails and names from web pages')
    parser.add_argument('urls', nargs='+', help='URLs to scrape')
    parser.add_argument('--delay', type=int, default=1, help='Delay between requests in seconds')
    parser.add_argument('--output', choices=['csv', 'json', 'excel'], default='csv', help='Output format')
    parser.add_argument('--filename', default='scraped_emails', help='Output filename (without extension)')
    
    args = parser.parse_args()
    
    scraper = EmailNameScraper(delay=args.delay)
    
    print(f"Starting to scrape {len(args.urls)} page(s)...")
    results = scraper.scrape_multiple_pages(args.urls)
    
    # Print summary
    total_emails = sum(result['emails_found'] for result in results)
    successful_pages = sum(1 for result in results if result['status'] == 'success')
    
    print(f"\n=== SCRAPING SUMMARY ===")
    print(f"Pages processed: {len(args.urls)}")
    print(f"Successful pages: {successful_pages}")
    print(f"Total emails found: {total_emails}")
    
    # Show results
    for result in results:
        print(f"\n{result['url']}: {result['emails_found']} emails ({result['status']})")
        for item in result['data'][:5]:  # Show first 5 emails
            name_part = f" - {item['name']}" if item['name'] else ""
            print(f"  {item['email']}{name_part}")
        if len(result['data']) > 5:
            print(f"  ... and {len(result['data']) - 5} more")
    
    # Save results
    scraper.save_results(results, args.output, args.filename)

if __name__ == "__main__":
    main()