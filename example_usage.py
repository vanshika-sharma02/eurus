#!/usr/bin/env python3
"""
Example usage of the EmailNameScraper with website crawling
"""

from email_scraper import EmailNameScraper

def example_single_page_scraping():
    """Example of scraping specific pages."""
    print("=== SINGLE PAGE SCRAPING EXAMPLE ===")
    
    # Create scraper instance
    scraper = EmailNameScraper(delay=1)
    
    # Example URLs to scrape (replace with actual URLs)
    urls = [
        "https://example.com/contact",
        "https://example.com/team",
        "https://example.com/about"
    ]
    
    print(f"Scraping {len(urls)} specific pages...\n")
    
    # Scrape the pages
    results = scraper.scrape_multiple_pages(urls)
    
    # Display results
    display_results(results)
    
    # Save results
    if any(result['emails_found'] > 0 for result in results):
        scraper.save_results(results, 'csv', 'single_page_results')
        print("\nResults saved to single_page_results.csv")

def example_website_crawling():
    """Example of crawling entire websites."""
    print("\n=== WEBSITE CRAWLING EXAMPLE ===")
    
    # Create scraper instance with custom settings
    scraper = EmailNameScraper(
        delay=2,           # 2 seconds between requests
        max_pages=20,      # Limit to 20 pages per website
        respect_robots=True # Respect robots.txt
    )
    
    # Base URL of website to crawl (replace with actual website)
    base_url = "https://example.com"
    
    print(f"Crawling entire website: {base_url}")
    print("This will discover and scrape all pages on the website...\n")
    
    # Crawl the entire website
    results = scraper.scrape_website(base_url)
    
    # Display results
    display_results(results)
    
    # Save results
    if any(result['emails_found'] > 0 for result in results):
        scraper.save_results(results, 'csv', 'website_crawl_results')
        print("\nResults saved to website_crawl_results.csv")

def display_results(results):
    """Helper function to display scraping results."""
    total_emails = 0
    unique_emails = set()
    
    for result in results:
        print(f"URL: {result['url']}")
        if result.get('page_title'):
            print(f"Page Title: {result['page_title']}")
        print(f"Status: {result['status']}")
        print(f"Emails found: {result['emails_found']}")
        
        if result['data']:
            print("Results:")
            for item in result['data']:
                name_display = f" ({item['name']})" if item['name'] else " (no name found)"
                print(f"  • {item['email']}{name_display}")
                unique_emails.add(item['email'])
        
        total_emails += result['emails_found']
        print("-" * 60)
    
    print(f"Total emails found across all pages: {total_emails}")
    print(f"Unique emails found: {len(unique_emails)}")

def main():
    """Run examples for both single page and website crawling."""
    print("Email and Name Scraper Examples")
    print("="*50)
    
    # Example 1: Single page scraping
    example_single_page_scraping()
    
    # Example 2: Website crawling
    example_website_crawling()
    
    print("\n" + "="*50)
    print("Examples completed!")
    print("\nTo use the scraper from command line:")
    print("  Single pages: python email_scraper.py https://example.com/contact https://example.com/about")
    print("  Crawl website: python email_scraper.py --crawl-website https://example.com")
    print("  With options: python email_scraper.py --crawl-website --delay 2 --max-pages 30 --output excel https://example.com")

if __name__ == "__main__":
    main()