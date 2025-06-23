# Email and Name Scraper

A Python web scraper that extracts email addresses and associated names from web pages.

## Features

- Extracts email addresses from any web page
- Attempts to find names associated with emails
- Supports multiple output formats (CSV, JSON, Excel)
- Respectful scraping with configurable delays
- Smart detection of contact sections and team pages
- Command-line interface and library usage

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Basic usage:
```bash
python email_scraper.py https://example.com/contact
```

Scrape multiple pages:
```bash
python email_scraper.py https://example.com/contact https://example.com/team https://example.com/about
```

Advanced options:
```bash
python email_scraper.py https://example.com/contact \
    --delay 2 \
    --output json \
    --filename my_results
```

### Command Line Options

- `urls`: One or more URLs to scrape (required)
- `--delay`: Delay between requests in seconds (default: 1)
- `--output`: Output format - csv, json, or excel (default: csv)
- `--filename`: Output filename without extension (default: scraped_emails)

### Library Usage

```python
from email_scraper import EmailNameScraper

# Create scraper instance
scraper = EmailNameScraper(delay=1)

# Scrape a single page
result = scraper.scrape_page("https://example.com/contact")

# Scrape multiple pages
urls = ["https://example.com/contact", "https://example.com/team"]
results = scraper.scrape_multiple_pages(urls)

# Save results
scraper.save_results(results, 'csv', 'my_results')
```

## How It Works

The scraper uses several strategies to find emails and names:

1. **Email Detection**: Uses regex patterns to find valid email addresses
2. **Contact Section Detection**: Looks for common contact-related HTML elements
3. **Name Association**: Searches for names near email addresses using:
   - Context windows around emails
   - Common name patterns (First Last, First M. Last, etc.)
   - Contact section analysis

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

### Scrape multiple pages with custom settings:
```bash
python email_scraper.py \
    https://company.com/contact \
    https://company.com/team \
    https://company.com/about \
    --delay 3 \
    --output excel \
    --filename company_contacts
```

### Use as a library:
```python
from email_scraper import EmailNameScraper

scraper = EmailNameScraper()
results = scraper.scrape_page("https://example.com/contact")

for item in results['data']:
    print(f"Email: {item['email']}, Name: {item['name']}")
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