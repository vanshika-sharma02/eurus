#!/usr/bin/env python3
"""
Demo script for the Enhanced Email and Name Scraper
This script demonstrates both single-page scraping and website crawling.
"""

import sys
from email_scraper import EmailNameScraper

def demo_with_real_website():
    """
    Demo using a real website that's likely to have contact information.
    Note: This is for demonstration purposes only. Always respect robots.txt and terms of service.
    """
    print("🔍 Enhanced Email Scraper Demo")
    print("=" * 50)
    
    # Create scraper instance
    scraper = EmailNameScraper(
        delay=2,          # Be respectful - 2 second delay
        max_pages=10,     # Limit to 10 pages for demo
        respect_robots=True
    )
    
    # Example: Scrape a single contact page
    print("\n📄 DEMO 1: Single Page Scraping")
    print("-" * 30)
    
    # Using a test website that should have some contact info
    test_url = "https://httpbin.org/html"  # Simple test page
    
    print(f"Scraping single page: {test_url}")
    result = scraper.scrape_page(test_url)
    
    print(f"Status: {result['status']}")
    print(f"Emails found: {result['emails_found']}")
    if result['data']:
        for item in result['data']:
            print(f"  • {item['email']} - {item['name'] or 'No name'}")
    else:
        print("  No emails found on this test page")
    
    # Example: Demonstrate website crawling (with a very small site)
    print("\n🕷️  DEMO 2: Website Crawling")
    print("-" * 30)
    print("For website crawling, you would use:")
    print("  scraper.scrape_website('https://yourwebsite.com')")
    print("\nThis would automatically:")
    print("  ✓ Discover all pages on the website")
    print("  ✓ Respect robots.txt rules")
    print("  ✓ Extract emails and associated names")
    print("  ✓ Track which page each email was found on")
    
    print("\n📊 DEMO 3: Command Line Usage Examples")
    print("-" * 30)
    print("Scrape specific pages:")
    print("  python email_scraper.py https://example.com/contact https://example.com/about")
    print("\nCrawl entire website:")
    print("  python email_scraper.py --crawl-website https://example.com")
    print("\nWith custom options:")
    print("  python email_scraper.py --crawl-website --delay 3 --max-pages 50 --output excel https://example.com")
    print("\nIgnore robots.txt (use responsibly):")
    print("  python email_scraper.py --crawl-website --no-robots https://example.com")

def demo_features():
    """Demonstrate the key features of the scraper."""
    print("\n🚀 SCRAPER FEATURES")
    print("=" * 50)
    
    features = [
        "✅ Website Crawling - Automatically discovers all pages",
        "✅ Email Extraction - Uses advanced regex patterns",
        "✅ Name Association - Finds names near email addresses",
        "✅ Multiple Output Formats - CSV, JSON, Excel",
        "✅ Robots.txt Respect - Ethical scraping practices",
        "✅ Rate Limiting - Configurable delays between requests",
        "✅ Error Handling - Robust error recovery",
        "✅ Structured Data - Extracts from JSON-LD, microdata",
        "✅ Contact Sections - Targeted extraction from contact areas",
        "✅ Page Context - Tracks page titles and URLs",
        "✅ Duplicate Removal - Smart deduplication",
        "✅ Logging - Detailed progress tracking"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n📋 OUTPUT FORMAT")
    print("-" * 20)
    print("The scraper outputs data with:")
    print("  • Email address")
    print("  • Associated name (if found)")
    print("  • Source page URL")
    print("  • Page title")
    print("  • Scraping status")

def demo_code_examples():
    """Show code examples for using the scraper."""
    print("\n💻 CODE EXAMPLES")
    print("=" * 50)
    
    print("1. Basic single page scraping:")
    print("""
    from email_scraper import EmailNameScraper
    
    scraper = EmailNameScraper(delay=1)
    result = scraper.scrape_page('https://example.com/contact')
    print(f"Found {result['emails_found']} emails")
    """)
    
    print("2. Crawl entire website:")
    print("""
    scraper = EmailNameScraper(delay=2, max_pages=50)
    results = scraper.scrape_website('https://example.com')
    scraper.save_results(results, 'csv', 'my_results')
    """)
    
    print("3. Multiple specific pages:")
    print("""
    urls = ['https://example.com/contact', 'https://example.com/team']
    results = scraper.scrape_multiple_pages(urls)
    """)
    
    print("4. Custom configuration:")
    print("""
    scraper = EmailNameScraper(
        delay=3,              # 3 second delay
        max_pages=100,        # Up to 100 pages
        respect_robots=False  # Ignore robots.txt
    )
    """)

def main():
    """Main demo function."""
    print("� Welcome to the Enhanced Email Scraper Demo!")
    
    # Show features
    demo_features()
    
    # Show code examples
    demo_code_examples()
    
    # Run actual demo
    demo_with_real_website()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run with your target website: python email_scraper.py --crawl-website https://yoursite.com")
    print("3. Check the output CSV file for results")
    print("\n⚠️  Remember to:")
    print("  • Respect website terms of service")
    print("  • Use appropriate delays")
    print("  • Check robots.txt")
    print("  • Use scraped data responsibly")

if __name__ == "__main__":
    main()