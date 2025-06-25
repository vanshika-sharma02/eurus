# Email and Name Scraper

A Python web scraper that extracts email addresses and associated names from web pages.

## Features

- **Email Extraction**: Finds email addresses from any web page
- **Name Association**: Attempts to find names associated with emails
- **Website Crawling**: Automatically discovers and scrapes multiple pages from a website
- **Smart Link Following**: Prioritizes contact, team, and staff pages
- **Robots.txt Compliance**: Respects website crawling policies
- **Multiple Output Formats**: Supports CSV, JSON, and Excel
- **Respectful Scraping**: Configurable delays and depth limits
- **Domain Filtering**: Stays within the same domain when crawling
- **Command-line Interface**: Easy-to-use CLI with many options
- **Library Usage**: Can be imported and used in your own scripts

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

**Basic single-page scraping:**
```bash
python email_scraper.py https://example.com/contact
```

**Scrape multiple specific pages:**
```bash
python email_scraper.py https://example.com/contact https://example.com/team https://example.com/about
```

**Website crawling (NEW!):**
```bash
python email_scraper.py https://example.com --crawl --max-depth 3 --max-pages 20
```

**Advanced crawling options:**
```bash
python email_scraper.py https://company.com \
    --crawl \
    --max-depth 2 \
    --max-pages 50 \
    --delay 3 \
    --output json \
    --filename company_crawl
```

### Command Line Options

**Basic Options:**
- `urls`: One or more URLs to scrape (required)
- `--delay`: Delay between requests in seconds (default: 1)
- `--output`: Output format - csv, json, or excel (default: csv)
- `--filename`: Output filename without extension (default: scraped_emails)

**Crawling Options:**
- `--crawl`: Enable website crawling to automatically discover more pages
- `--max-depth`: Maximum crawling depth from starting URLs (default: 2)
- `--max-pages`: Maximum pages to scrape per domain (default: 50)
- `--ignore-robots`: Ignore robots.txt restrictions (use responsibly)

### Library Usage

**Basic scraping:**
```python
from email_scraper import EmailNameScraper

# Create scraper instance
scraper = EmailNameScraper(delay=1)

# Scrape a single page
result = scraper.scrape_page("https://example.com/contact")

# Scrape multiple specific pages
urls = ["https://example.com/contact", "https://example.com/team"]
results = scraper.scrape_multiple_pages(urls)

# Save results
scraper.save_results(results, 'csv', 'my_results')
```

**Website crawling:**
```python
from email_scraper import EmailNameScraper

# Create crawler with custom settings
crawler = EmailNameScraper(
    delay=2,              # 2 second delay between requests
    max_depth=3,          # Crawl up to 3 levels deep
    max_pages=100,        # Maximum 100 pages per domain
    respect_robots=True   # Respect robots.txt
)

# Crawl website starting from homepage
results = crawler.crawl_website(["https://company.com"])

# Save all discovered emails
crawler.save_results(results, 'json', 'company_emails')
```

## How It Works

The scraper uses several strategies to find emails and names:

1. **Email Detection**: Uses regex patterns to find valid email addresses
2. **Contact Section Detection**: Looks for common contact-related HTML elements
3. **Name Association**: Searches for names near email addresses using:
   - Context windows around emails
   - Common name patterns (First Last, First M. Last, etc.)
   - Contact section analysis
4. **Website Crawling**: When enabled, automatically discovers more pages by:
   - Extracting all links from each page
   - Prioritizing contact, team, staff, and directory pages
   - Following links within the same domain only
   - Respecting depth and page limits
   - Checking robots.txt before accessing pages

## Output Formats

### CSV Format
```
url,email,name,status
https://example.com/contact,john@example.com,John Smith,success
https://example.com/contact,jane@example.com,Jane Doe,success
```

### JSON Format
```json
[
  {
    "url": "https://example.com/contact",
    "emails_found": 2,
    "data": [
      {"email": "john@example.com", "name": "John Smith"},
      {"email": "jane@example.com", "name": "Jane Doe"}
    ],
    "status": "success"
  }
]
```

## Examples

### Scrape a company's contact page:
```bash
python email_scraper.py https://company.com/contact
```

### Crawl an entire website:
```bash
python email_scraper.py https://company.com --crawl --max-depth 3 --max-pages 25
```

### Scrape multiple specific pages:
```bash
python email_scraper.py \
    https://company.com/contact \
    https://company.com/team \
    https://company.com/about \
    --delay 3 \
    --output excel \
    --filename company_contacts
```

### Advanced crawling with custom settings:
```bash
python email_scraper.py https://university.edu \
    --crawl \
    --max-depth 2 \
    --max-pages 100 \
    --delay 2 \
    --output json \
    --filename university_emails
```

### Use as a library for single page:
```python
from email_scraper import EmailNameScraper

scraper = EmailNameScraper()
results = scraper.scrape_page("https://example.com/contact")

for item in results['data']:
    print(f"Email: {item['email']}, Name: {item['name']}")
```

### Use as a library for website crawling:
```python
from email_scraper import EmailNameScraper

crawler = EmailNameScraper(max_depth=2, max_pages=20)
results = crawler.crawl_website(["https://company.com"])

total_emails = sum(r['emails_found'] for r in results)
print(f"Found {total_emails} emails across {len(results)} pages")
```

## Best Practices

1. **Be Respectful**: Use appropriate delays between requests
2. **Check robots.txt**: Respect website scraping policies
3. **Rate Limiting**: Don't overwhelm servers with too many requests
4. **Legal Compliance**: Ensure you have permission to scrape the websites
5. **Data Privacy**: Handle extracted email addresses responsibly

## Limitations

- Name detection is heuristic-based and may not always be accurate
- Some websites may block automated requests
- JavaScript-rendered content is not supported (consider using Selenium for such cases)
- The accuracy depends on the structure and content of the target websites

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is provided as-is for educational and legitimate business purposes.