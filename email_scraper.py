#!/usr/bin/env python3
"""
Web Email and Name Scraper with Website Crawling
Extracts email addresses and associated names from web pages and can crawl entire websites.
"""

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import time
from urllib.parse import urljoin, urlparse, urlencode
from urllib.robotparser import RobotFileParser
from typing import List, Dict, Tuple, Set
import json
from collections import deque
import logging

class EmailNameScraper:
    def __init__(self, delay=1, max_pages=50, respect_robots=True):
        """
        Initialize the scraper with optional delay between requests.
        
        Args:
            delay (int): Delay in seconds between requests to be respectful to servers
            max_pages (int): Maximum number of pages to crawl per website
            respect_robots (bool): Whether to respect robots.txt
        """
        self.delay = delay
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Email regex pattern - improved
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Name patterns - common formats for names near emails
        self.name_patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last
            r'([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)',  # First M. Last
            r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Middle Last
            r'([A-Z]{2,}\s+[A-Z][a-z]+)',  # FIRST Last or similar
            r'([A-Z][a-z]+\s+[A-Za-z]+\s+[A-Z][a-z]+)',  # First von Last, etc.
        ]
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and belongs to the same domain."""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            
            # Must be same domain
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # Skip certain file types
            skip_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi'}
            if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip mailto links
            if parsed.scheme == 'mailto':
                return False
                
            return True
        except:
            return False
    
    def get_robots_txt(self, base_url: str) -> RobotFileParser:
        """Get and parse robots.txt for the website."""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            robot_parser = RobotFileParser()
            robot_parser.set_url(robots_url)
            robot_parser.read()
            return robot_parser
        except:
            return None
    
    def can_fetch(self, robot_parser: RobotFileParser, url: str) -> bool:
        """Check if we can fetch the URL according to robots.txt."""
        if not self.respect_robots or not robot_parser:
            return True
        return robot_parser.can_fetch(self.session.headers.get('User-Agent', '*'), url)
    
    def discover_pages(self, base_url: str) -> Set[str]:
        """
        Discover all pages on a website by crawling through links.
        
        Args:
            base_url (str): The base URL of the website to crawl
            
        Returns:
            Set[str]: Set of discovered URLs
        """
        self.logger.info(f"Starting website crawl for: {base_url}")
        
        discovered_urls = set()
        urls_to_visit = deque([base_url])
        visited_urls = set()
        
        # Get robots.txt
        robot_parser = self.get_robots_txt(base_url)
        
        while urls_to_visit and len(discovered_urls) < self.max_pages:
            current_url = urls_to_visit.popleft()
            
            if current_url in visited_urls:
                continue
                
            if not self.can_fetch(robot_parser, current_url):
                self.logger.info(f"Robots.txt disallows: {current_url}")
                continue
            
            try:
                self.logger.info(f"Discovering links on: {current_url}")
                response = self.session.get(current_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                visited_urls.add(current_url)
                discovered_urls.add(current_url)
                
                # Find all links
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    
                    if (self.is_valid_url(full_url, base_url) and 
                        full_url not in visited_urls and 
                        full_url not in urls_to_visit):
                        urls_to_visit.append(full_url)
                
                time.sleep(self.delay)  # Be respectful
                
            except Exception as e:
                self.logger.warning(f"Error discovering links on {current_url}: {e}")
                continue
        
        self.logger.info(f"Discovered {len(discovered_urls)} pages")
        return discovered_urls
    
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract email addresses from text."""
        emails = set()
        matches = self.email_pattern.findall(text)
        for match in matches:
            # Basic email validation
            if '@' in match and '.' in match.split('@')[1]:
                emails.add(match.lower())
        return emails
    
    def find_names_near_email(self, text: str, email: str, context_window: int = 200) -> List[str]:
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
        
        # Clean up the context
        context = re.sub(r'\s+', ' ', context)  # Multiple spaces to single space
        
        # Look for name patterns in the context
        for pattern in self.name_patterns:
            matches = re.findall(pattern, context)
            for match in matches:
                # Basic validation - avoid common false positives
                if not any(word.lower() in ['email', 'contact', 'phone', 'address', 'website'] for word in match.split()):
                    names.append(match.strip())
        
        return list(set(names))  # Remove duplicates
    
    def extract_from_structured_data(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Extract emails and names from structured data (microdata, JSON-LD, etc.).
        
        Returns:
            List[Tuple[str, str]]: List of (email, name) tuples
        """
        results = []
        
        # Look for JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    email = data.get('email')
                    name = data.get('name')
                    if email and name:
                        results.append((email.lower(), name))
            except:
                continue
        
        return results
    
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
            '[class*="bio"]',
            '[class*="profile"]',
            '[id*="contact"]',
            '[id*="staff"]',
            '[id*="team"]',
            'address',
            '.vcard',
            '.h-card'
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
            self.logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get page title for context
            page_title = soup.title.string if soup.title else ""
            
            # Get all text content
            text = soup.get_text()
            
            # Extract all emails
            all_emails = self.extract_emails_from_text(text)
            
            # Try to find names associated with emails
            email_name_pairs = []
            
            # First, try structured data
            structured_pairs = self.extract_from_structured_data(soup)
            email_name_pairs.extend(structured_pairs)
            
            # Then, try to extract from contact sections
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
                'page_title': page_title.strip(),
                'emails_found': len(unique_pairs),
                'data': [{'email': email, 'name': name} for email, name in unique_pairs],
                'status': 'success'
            }
            
            self.logger.info(f"Found {len(unique_pairs)} emails on {url}")
            
            time.sleep(self.delay)  # Be respectful to the server
            
            return result
            
        except requests.RequestException as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'page_title': "",
                'emails_found': 0,
                'data': [],
                'status': f'error: {str(e)}'
            }
    
    def scrape_website(self, base_url: str) -> List[Dict]:
        """
        Scrape an entire website by discovering and scraping all pages.
        
        Args:
            base_url (str): The base URL of the website to scrape
            
        Returns:
            List[Dict]: List of results for each page
        """
        # Discover all pages
        discovered_urls = self.discover_pages(base_url)
        
        # Scrape each discovered page
        results = []
        for url in discovered_urls:
            result = self.scrape_page(url)
            results.append(result)
        
        return results
    
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
            page_title = result.get('page_title', '')
            status = result['status']
            for item in result['data']:
                all_data.append({
                    'url': url,
                    'page_title': page_title,
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
    parser = argparse.ArgumentParser(description='Scrape emails and names from web pages or entire websites')
    parser.add_argument('urls', nargs='+', help='URLs to scrape')
    parser.add_argument('--crawl-website', action='store_true', help='Crawl entire website(s) instead of just the provided URLs')
    parser.add_argument('--delay', type=int, default=1, help='Delay between requests in seconds')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum pages to crawl per website')
    parser.add_argument('--output', choices=['csv', 'json', 'excel'], default='csv', help='Output format')
    parser.add_argument('--filename', default='scraped_emails', help='Output filename (without extension)')
    parser.add_argument('--no-robots', action='store_true', help='Ignore robots.txt (use responsibly)')
    
    args = parser.parse_args()
    
    scraper = EmailNameScraper(
        delay=args.delay, 
        max_pages=args.max_pages,
        respect_robots=not args.no_robots
    )
    
    if args.crawl_website:
        print(f"Starting to crawl {len(args.urls)} website(s)...")
        all_results = []
        for url in args.urls:
            website_results = scraper.scrape_website(url)
            all_results.extend(website_results)
        results = all_results
    else:
        print(f"Starting to scrape {len(args.urls)} page(s)...")
        results = scraper.scrape_multiple_pages(args.urls)
    
    # Print summary
    total_emails = sum(result['emails_found'] for result in results)
    successful_pages = sum(1 for result in results if result['status'] == 'success')
    
    print(f"\n=== SCRAPING SUMMARY ===")
    print(f"Pages processed: {len(results)}")
    print(f"Successful pages: {successful_pages}")
    print(f"Total emails found: {total_emails}")
    
    # Show results
    for result in results:
        page_title = f" ({result.get('page_title', '')})" if result.get('page_title') else ""
        print(f"\n{result['url']}{page_title}: {result['emails_found']} emails ({result['status']})")
        for item in result['data'][:3]:  # Show first 3 emails
            name_part = f" - {item['name']}" if item['name'] else ""
            print(f"  {item['email']}{name_part}")
        if len(result['data']) > 3:
            print(f"  ... and {len(result['data']) - 3} more")
    
    # Save results
    scraper.save_results(results, args.output, args.filename)

if __name__ == "__main__":
    main()