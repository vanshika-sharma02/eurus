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
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from typing import List, Dict, Tuple, Set
import json
from collections import deque

class EmailNameScraper:
    def __init__(self, delay=1, max_depth=2, max_pages=50, respect_robots=True):
        """
        Initialize the scraper with crawling capabilities.
        
        Args:
            delay (int): Delay in seconds between requests to be respectful to servers
            max_depth (int): Maximum depth to crawl from starting URLs
            max_pages (int): Maximum number of pages to scrape per domain
            respect_robots (bool): Whether to respect robots.txt
        """
        self.delay = delay
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        
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
        
        # Crawling state
        self.visited_urls = set()
        self.robots_cache = {}
        
        # Link patterns that are likely to contain emails
        self.priority_link_patterns = [
            r'contact', r'about', r'team', r'staff', r'directory', 
            r'people', r'faculty', r'employees', r'management'
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
    
    def check_robots_txt(self, url: str) -> bool:
        """
        Check if URL is allowed according to robots.txt
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if allowed, False if disallowed
        """
        if not self.respect_robots:
            return True
            
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if base_url not in self.robots_cache:
            try:
                robots_url = urljoin(base_url, '/robots.txt')
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[base_url] = rp
            except Exception:
                # If we can't read robots.txt, assume it's allowed
                self.robots_cache[base_url] = None
        
        rp = self.robots_cache[base_url]
        if rp is None:
            return True
            
        return rp.can_fetch(self.session.headers.get('User-Agent', '*'), url)
    
    def normalize_url(self, url: str, base_url: str) -> str:
        """
        Normalize and clean URL
        
        Args:
            url (str): URL to normalize
            base_url (str): Base URL for relative links
            
        Returns:
            str: Normalized URL
        """
        # Convert relative URLs to absolute
        full_url = urljoin(base_url, url)
        
        # Parse and rebuild URL to normalize it
        parsed = urlparse(full_url)
        
        # Remove fragments and common tracking parameters
        query_parts = []
        if parsed.query:
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    # Skip common tracking parameters
                    if key.lower() not in ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid']:
                        query_parts.append(param)
        
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path.rstrip('/') or '/',
            parsed.params,
            '&'.join(query_parts),
            ''  # Remove fragment
        ))
        
        return normalized
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are from the same domain
        
        Args:
            url1 (str): First URL
            url2 (str): Second URL
            
        Returns:
            bool: True if same domain
        """
        domain1 = urlparse(url1).netloc.lower()
        domain2 = urlparse(url2).netloc.lower()
        
        # Remove www. for comparison
        domain1 = domain1.replace('www.', '')
        domain2 = domain2.replace('www.', '')
        
        return domain1 == domain2
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all valid links from a page
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            base_url (str): Base URL of the page
            
        Returns:
            List[str]: List of normalized URLs
        """
        links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue
                
            # Skip mailto, tel, javascript, etc.
            if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue
                
            # Normalize the URL
            try:
                normalized_url = self.normalize_url(href, base_url)
                
                # Only include HTTP/HTTPS links
                if normalized_url.startswith(('http://', 'https://')):
                    # Only include links from the same domain
                    if self.is_same_domain(normalized_url, base_url):
                        links.append(normalized_url)
            except Exception:
                continue
        
        return list(set(links))  # Remove duplicates
    
    def filter_priority_links(self, links: List[str]) -> Tuple[List[str], List[str]]:
        """
        Separate priority links (likely to contain contacts) from regular links
        
        Args:
            links (List[str]): List of all links
            
        Returns:
            Tuple[List[str], List[str]]: (priority_links, regular_links)
        """
        priority_links = []
        regular_links = []
        
        for link in links:
            link_lower = link.lower()
            is_priority = any(pattern in link_lower for pattern in self.priority_link_patterns)
            
            if is_priority:
                priority_links.append(link)
            else:
                regular_links.append(link)
        
        return priority_links, regular_links
    
    def crawl_website(self, start_urls: List[str]) -> List[Dict]:
        """
        Crawl website starting from given URLs, following links to find more pages
        
        Args:
            start_urls (List[str]): Starting URLs to crawl from
            
        Returns:
            List[Dict]: Results from all crawled pages
        """
        all_results = []
        
        # Group URLs by domain to respect per-domain limits
        domain_urls = {}
        for url in start_urls:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            if domain not in domain_urls:
                domain_urls[domain] = []
            domain_urls[domain].append(url)
        
        for domain, urls in domain_urls.items():
            print(f"\n🌐 Crawling domain: {domain}")
            
            # Initialize crawling queue with (url, depth)
            crawl_queue = deque([(url, 0) for url in urls])
            domain_visited = set()
            domain_results = []
            pages_scraped = 0
            
            while crawl_queue and pages_scraped < self.max_pages:
                current_url, depth = crawl_queue.popleft()
                
                # Skip if already visited or depth exceeded
                if current_url in domain_visited or depth > self.max_depth:
                    continue
                
                # Check robots.txt
                if not self.check_robots_txt(current_url):
                    print(f"  ⚠️  Skipping {current_url} (blocked by robots.txt)")
                    continue
                
                domain_visited.add(current_url)
                pages_scraped += 1
                
                print(f"  📄 Scraping [{pages_scraped}/{self.max_pages}] (depth {depth}): {current_url}")
                
                # Scrape the current page
                result = self.scrape_page(current_url)
                domain_results.append(result)
                
                # If we haven't reached max depth, extract links for next level
                if depth < self.max_depth and result['status'] == 'success':
                    try:
                        response = self.session.get(current_url, timeout=10)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract all links
                        links = self.extract_links(soup, current_url)
                        
                        # Prioritize certain types of links
                        priority_links, regular_links = self.filter_priority_links(links)
                        
                        # Add priority links first
                        for link in priority_links:
                            if link not in domain_visited:
                                crawl_queue.appendleft((link, depth + 1))  # Add to front for priority
                        
                        # Add regular links
                        for link in regular_links[:10]:  # Limit regular links to prevent explosion
                            if link not in domain_visited:
                                crawl_queue.append((link, depth + 1))
                        
                        print(f"    🔗 Found {len(priority_links)} priority links, {len(regular_links)} regular links")
                        
                    except Exception as e:
                        print(f"    ⚠️  Error extracting links: {e}")
                
                # Small delay between requests
                time.sleep(self.delay)
            
            all_results.extend(domain_results)
            print(f"  ✅ Completed domain {domain}: {pages_scraped} pages, {sum(r['emails_found'] for r in domain_results)} emails")
        
        return all_results
    
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
    
    # Crawling options
    parser.add_argument('--crawl', action='store_true', help='Enable crawling to follow links and discover more pages')
    parser.add_argument('--max-depth', type=int, default=2, help='Maximum crawling depth (default: 2)')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum pages to scrape per domain (default: 50)')
    parser.add_argument('--ignore-robots', action='store_true', help='Ignore robots.txt restrictions')
    
    args = parser.parse_args()
    
    # Create scraper with crawling parameters
    scraper = EmailNameScraper(
        delay=args.delay,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        respect_robots=not args.ignore_robots
    )
    
    if args.crawl:
        print(f"🕷️  Starting to crawl from {len(args.urls)} starting URL(s)...")
        print(f"   Max depth: {args.max_depth}")
        print(f"   Max pages per domain: {args.max_pages}")
        print(f"   Respect robots.txt: {not args.ignore_robots}")
        print(f"   Delay between requests: {args.delay} seconds")
        results = scraper.crawl_website(args.urls)
    else:
        print(f"📄 Starting to scrape {len(args.urls)} specific page(s)...")
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