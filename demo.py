#!/usr/bin/env python3
"""
Demo script showing how to use the Email and Name Scraper
"""

from email_scraper import EmailNameScraper
import json

def demo_scraper():
    """Demonstrate the email scraper functionality"""
    print("🔍 Email and Name Scraper Demo")
    print("=" * 50)
    
    # Create scraper instance
    scraper = EmailNameScraper(delay=2)  # Be respectful with 2-second delay
    
    # Example URLs that are safe to scrape
    demo_urls = [
        "https://httpbin.org/",  # Safe testing endpoint
    ]
    
    print(f"📄 Scraping {len(demo_urls)} page(s)...")
    print()
    
    # Scrape the pages
    results = scraper.scrape_multiple_pages(demo_urls)
    
    # Display results
    total_emails = 0
    for result in results:
        print(f"🌐 URL: {result['url']}")
        print(f"📊 Status: {result['status']}")
        print(f"📧 Emails found: {result['emails_found']}")
        
        if result['data']:
            print("📝 Results:")
            for item in result['data']:
                name_display = f" ({item['name']})" if item['name'] else " (no name found)"
                print(f"   • {item['email']}{name_display}")
        else:
            print("   No emails found on this page")
        
        total_emails += result['emails_found']
        print("-" * 50)
    
    print(f"🎯 Total emails found: {total_emails}")
    
    # Save results if any found
    if total_emails > 0:
        scraper.save_results(results, 'json', 'demo_results')
        print("💾 Results saved to demo_results.json")
    
    return results

def show_usage_examples():
    """Show usage examples"""
    print("\n🚀 Usage Examples:")
    print("=" * 50)
    
    print("1. Basic command line usage:")
    print("   python email_scraper.py https://example.com/contact")
    
    print("\n2. Multiple pages with custom settings:")
    print("   python email_scraper.py https://company.com/contact https://company.com/team \\")
    print("          --delay 3 --output csv --filename results")
    
    print("\n3. Library usage:")
    print("""
   from email_scraper import EmailNameScraper
   
   scraper = EmailNameScraper(delay=1)
   results = scraper.scrape_page("https://example.com/contact")
   
   for item in results['data']:
       print(f"Email: {item['email']}, Name: {item['name']}")
   """)
    
    print("\n⚠️  Important Notes:")
    print("- Always respect robots.txt and website terms of service")
    print("- Use appropriate delays between requests")
    print("- Ensure you have permission to scrape the websites")
    print("- Handle extracted data responsibly and in compliance with privacy laws")

if __name__ == "__main__":
    print("🎉 Welcome to the Email and Name Scraper!")
    print()
    
    # Run demo
    demo_scraper()
    
    # Show usage examples
    show_usage_examples()
    
    print("\n✅ Demo completed! The scraper is ready to use.")
    print("📖 Check README.md for detailed documentation.")