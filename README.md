# Enhanced Email and Name Scraper 🕷️📧

A powerful Python web scraper that extracts email addresses and associated names from websites. It can scrape individual pages or crawl entire websites automatically.

## 🚀 Features

- **Website Crawling** - Automatically discovers and scrapes all pages on a website
- **Email Extraction** - Advanced regex patterns to find email addresses
- **Name Association** - Intelligently finds names associated with email addresses
- **Multiple Output Formats** - Save results as CSV, JSON, or Excel
- **Robots.txt Respect** - Ethical scraping that respects website robots.txt
- **Rate Limiting** - Configurable delays between requests
- **Error Handling** - Robust error recovery and logging
- **Structured Data Extraction** - Supports JSON-LD, microdata, and schema.org
- **Contact Section Detection** - Targeted extraction from contact areas
- **Page Context Tracking** - Records page titles and URLs for each email found
- **Smart Deduplication** - Removes duplicate emails while preserving data

## 📋 Output Data

For each email found, the scraper collects:
- Email address
- Associated name (if found)
- Source page URL
- Page title
- Scraping status

## 🛠️ Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Command Line Interface

#### Crawl Entire Website
```bash
# Basic website crawling
python email_scraper.py --crawl-website https://example.com

# With custom settings
python email_scraper.py --crawl-website --delay 2 --max-pages 50 --output excel https://example.com

# Ignore robots.txt (use responsibly)
python email_scraper.py --crawl-website --no-robots https://example.com
```

#### Scrape Specific Pages
```bash
# Single page
python email_scraper.py https://example.com/contact

# Multiple pages
python email_scraper.py https://example.com/contact https://example.com/team https://example.com/about

# With custom output format
python email_scraper.py --output json --filename my_results https://example.com/contact
```

#### Command Line Options
- `--crawl-website` - Crawl entire website instead of just provided URLs
- `--delay N` - Delay between requests in seconds (default: 1)
- `--max-pages N` - Maximum pages to crawl per website (default: 50)
- `--output FORMAT` - Output format: csv, json, or excel (default: csv)
- `--filename NAME` - Output filename without extension (default: scraped_emails)
- `--no-robots` - Ignore robots.txt (use responsibly)

### Python Library Usage

#### Basic Single Page Scraping
```python
from email_scraper import EmailNameScraper

# Create scraper instance
scraper = EmailNameScraper(delay=1)

# Scrape a single page
result = scraper.scrape_page('https://example.com/contact')

print(f"Found {result['emails_found']} emails")
for item in result['data']:
    print(f"Email: {item['email']}, Name: {item['name']}")
```

#### Website Crawling
```python
# Create scraper with custom settings
scraper = EmailNameScraper(
    delay=2,              # 2 second delay between requests
    max_pages=50,         # Crawl up to 50 pages
    respect_robots=True   # Respect robots.txt
)

# Crawl entire website
results = scraper.scrape_website('https://example.com')

# Save results
scraper.save_results(results, 'csv', 'website_emails')
```

#### Multiple Specific Pages
```python
# Scrape multiple specific pages
urls = [
    'https://example.com/contact',
    'https://example.com/team',
    'https://example.com/about'
]

results = scraper.scrape_multiple_pages(urls)

# Process results
for result in results:
    print(f"Page: {result['url']}")
    print(f"Title: {result['page_title']}")
    print(f"Emails: {result['emails_found']}")
```

## 🔧 Configuration Options

### EmailNameScraper Parameters

- `delay` (int): Seconds to wait between requests (default: 1)
- `max_pages` (int): Maximum pages to crawl per website (default: 50)
- `respect_robots` (bool): Whether to respect robots.txt (default: True)

### Smart Email-Name Association

The scraper uses multiple strategies to find names associated with emails:

1. **Structured Data** - Extracts from JSON-LD, microdata, and schema.org markup
2. **Contact Sections** - Searches in elements with contact-related classes/IDs
3. **Context Analysis** - Looks for names near email addresses in text
4. **Pattern Matching** - Uses regex patterns for common name formats

## 📊 Output Formats

### CSV Output
```csv
url,page_title,email,name,status
https://example.com/contact,Contact Us,john@example.com,John Smith,success
https://example.com/team,Our Team,jane@example.com,Jane Doe,success
```

### JSON Output
```json
[
  {
    "url": "https://example.com/contact",
    "page_title": "Contact Us",
    "emails_found": 2,
    "data": [
      {"email": "john@example.com", "name": "John Smith"},
      {"email": "info@example.com", "name": ""}
    ],
    "status": "success"
  }
]
```

## 🛡️ Ethical Usage Guidelines

**Always use this tool responsibly:**

1. **Respect robots.txt** - The scraper respects robots.txt by default
2. **Use appropriate delays** - Don't overwhelm servers with rapid requests
3. **Check terms of service** - Ensure you have permission to scrape
4. **Handle data responsibly** - Comply with privacy laws and regulations
5. **Be respectful** - Consider the impact on website performance

## 🚦 Rate Limiting & Performance

The scraper includes built-in rate limiting:
- Default 1-second delay between requests
- Configurable delays up to any duration
- Respects website robots.txt crawl delays
- Session reuse for better performance
- Timeout handling for stuck requests

## 🔍 How It Works

1. **URL Discovery** - Finds all links on the website (when crawling)
2. **Robots.txt Check** - Verifies permission to access each URL
3. **Content Extraction** - Downloads and parses HTML content
4. **Email Detection** - Uses regex patterns to find email addresses
5. **Name Association** - Searches for names near found emails
6. **Data Cleaning** - Removes duplicates and validates results
7. **Output Generation** - Saves results in chosen format

## 📁 File Structure

```
email-scraper/
├── email_scraper.py    # Main scraper class
├── example_usage.py    # Usage examples
├── demo.py            # Interactive demo
├── requirements.txt   # Dependencies
└── README.md         # This file
```

## 🔧 Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `pandas` - Data manipulation
- `openpyxl` - Excel file support

## 🎯 Example Output

```
=== SCRAPING SUMMARY ===
Pages processed: 15
Successful pages: 14
Total emails found: 23

https://example.com/contact (Contact Us): 5 emails (success)
  john.smith@example.com - John Smith
  jane.doe@example.com - Jane Doe
  info@example.com
  ... and 2 more

https://example.com/team (Our Team): 8 emails (success)
  alice@example.com - Alice Johnson
  bob@example.com - Bob Wilson
  charlie@example.com - Charlie Brown
  ... and 5 more
```

## 🚨 Common Issues & Solutions

**Issue: No emails found**
- Check if the website blocks automated requests
- Verify the website actually contains email addresses
- Try increasing the delay between requests

**Issue: Names not associated correctly**
- Names must be near emails in the page text
- The scraper looks for common name patterns
- Some websites may structure data differently

**Issue: Robots.txt blocking access**
- Use `--no-robots` flag (use responsibly)
- Check which pages are actually blocked
- Respect website preferences when possible

## 📄 License

This tool is for educational and legitimate business purposes only. Users are responsible for ensuring compliance with website terms of service and applicable laws.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the scraper!

---

**⚠️ Disclaimer**: This tool should only be used for legitimate purposes such as lead generation, market research, or data analysis where you have permission to access the data. Always respect website terms of service and applicable privacy laws.