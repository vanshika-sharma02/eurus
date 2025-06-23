#!/usr/bin/env python3
"""
Example usage of the EmailNameScraper
"""

from email_scraper import EmailNameScraper

def main():
    # Create scraper instance
    scraper = EmailNameScraper(delay=1)
    
    # Example URLs to scrape (replace with actual URLs)
    urls = [
        "https://example.com/contact",
        "https://example.com/team",
        "https://example.com/about"
    ]
    
    print("=== Email and Name Scraper Example ===")
    print(f"Scraping {len(urls)} pages...\n")
    
    # Scrape the pages
    results = scraper.scrape_multiple_pages(urls)
    
    # Display results
    total_emails = 0
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        print(f"Emails found: {result['emails_found']}")
        
        if result['data']:
            print("Results:")
            for item in result['data']:
                name_display = f" ({item['name']})" if item['name'] else " (no name found)"
                print(f"  • {item['email']}{name_display}")
        
        total_emails += result['emails_found']
        print("-" * 50)
    
    print(f"Total emails found across all pages: {total_emails}")
    
    # Save results to CSV
    if total_emails > 0:
        scraper.save_results(results, 'csv', 'example_results')
        print("\nResults saved to example_results.csv")

if __name__ == "__main__":
    main()