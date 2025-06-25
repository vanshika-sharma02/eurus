#!/usr/bin/env python3
"""
Example usage of the EmailNameScraper
"""

from email_scraper import EmailNameScraper

def main():
    print("=== Email and Name Scraper Examples ===\n")
    
    # Example 1: Basic scraping of specific pages
    print("📄 Example 1: Scraping specific pages")
    print("-" * 40)
    
    # Create scraper instance
    scraper = EmailNameScraper(delay=1)
    
    # Example URLs to scrape (replace with actual URLs)
    urls = [
        "https://example.com/contact",
        "https://example.com/team"
    ]
    
    print(f"Scraping {len(urls)} specific pages...")
    results = scraper.scrape_multiple_pages(urls)
    
    # Display results
    total_emails = 0
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        print(f"Emails found: {result['emails_found']}")
        
        if result['data']:
            print("Results:")
            for item in result['data'][:3]:  # Show first 3
                name_display = f" ({item['name']})" if item['name'] else " (no name found)"
                print(f"  • {item['email']}{name_display}")
        
        total_emails += result['emails_found']
        print("-" * 40)
    
    print(f"Total emails from specific pages: {total_emails}")
    
    print("\n🕷️  Example 2: Website crawling")
    print("-" * 40)
    
    # Create crawler instance with specific settings
    crawler = EmailNameScraper(
        delay=2,           # 2 second delay between requests
        max_depth=2,       # Crawl up to 2 levels deep
        max_pages=10,      # Maximum 10 pages per domain
        respect_robots=True # Respect robots.txt
    )
    
    # Starting URLs for crawling
    start_urls = ["https://example.com"]
    
    print(f"Crawling from {len(start_urls)} starting URL(s)...")
    print("This will automatically discover and scrape related pages")
    
    # Note: This is commented out to avoid actually crawling in the example
    # Uncomment the line below to actually crawl
    # crawl_results = crawler.crawl_website(start_urls)
    
    print("(Crawling disabled in example - uncomment to enable)")
    
    # Example of what crawling output would look like
    print("\nCrawling would output something like:")
    print("🌐 Crawling domain: example.com")
    print("  📄 Scraping [1/10] (depth 0): https://example.com")
    print("    🔗 Found 3 priority links, 15 regular links")
    print("  📄 Scraping [2/10] (depth 1): https://example.com/contact")
    print("  📄 Scraping [3/10] (depth 1): https://example.com/about")
    print("  ✅ Completed domain example.com: 8 pages, 12 emails")
    
    # Save results if any found
    if total_emails > 0:
        scraper.save_results(results, 'csv', 'example_results')
        print("\nResults saved to example_results.csv")

if __name__ == "__main__":
    main()