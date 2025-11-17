# KNKF Powerlifting Competition Scraper

A Python web scraper for extracting powerlifting competition information from the KNKF (Koninklijke Nederlandse Krachtsport en Fitnessbond) website.

## Features

- 🏋️‍♀️ Scrapes all national powerlifting competitions from [knkf-sectiepowerliften.nl](https://knkf-sectiepowerliften.nl/kalender/)
- 📅 Extracts competition dates, names, locations, and organizations
- 🎯 Identifies competition types (Classic, Equipped, Beginner)
- 👑 Detects qualification requirements
- ✅ Shows competition status (Definitief, etc.)
- 💾 Saves data to JSON format
- �️ **NEW:** Supabase database integration
- �🖥️ User-friendly command-line interface
- 📊 Database management tools

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python scraper.py
```

This will scrape all competitions and save them to `knkf_competitions.json`.

### Command Line Options

```bash
# Save to a custom filename
python scraper.py --output my_competitions.json

# Show all competitions (not just first 5)
python scraper.py --show-all

# Verbose output (show detailed logging)
python scraper.py --verbose

# Save to Supabase database (requires setup)
python scraper.py --database

# Save to database only (skip JSON)
python scraper.py --database --no-json

# Get help
python scraper.py --help
```

### Database Management

```bash
# Show database schema for Supabase
python db_manager.py schema

# List all competitions from database
python db_manager.py list

# List upcoming competitions only
python db_manager.py list --upcoming

# List competitions by type
python db_manager.py list --type Classic

# Export database to JSON
python db_manager.py export --output exported_competitions.json
```

## Output Format

The scraper generates a JSON file with the following structure:

```json
{
  "scraped_at": "2025-11-04T21:45:20.105046",
  "source_url": "https://knkf-sectiepowerliften.nl/kalender/",
  "total_competitions": 4,
  "competitions": [
    {
      "name": "NSK Powerliften",
      "location": "Leiden",
      "organization": "LSKV Fortius",
      "status": "Definitief",
      "capacity": "-",
      "start_date": "2025-10-25",
      "end_date": "2025-10-26",
      "url": "https://knkf-sectiepowerliften.nl/kalender/2025/nsk/",
      "qualification_required": true,
      "competition_type": "Classic"
    }
  ]
}
```

## Data Fields

- **name**: Competition name
- **location**: City where the competition takes place
- **organization**: Organizing club or federation
- **status**: Planning status (Definitief, etc.)
- **capacity**: Maximum number of participants
- **start_date**: Competition start date (YYYY-MM-DD)
- **end_date**: Competition end date (YYYY-MM-DD)
- **url**: Link to competition details page
- **qualification_required**: Boolean indicating if qualification is needed
- **competition_type**: Type of competition (Classic, Equipped, Beginner, etc.)

## Examples

### Filter competitions by type
```python
import json

with open('knkf_competitions.json', 'r') as f:
    data = json.load(f)

# Get only Classic competitions
classic_comps = [c for c in data['competitions'] if c['competition_type'] == 'Classic']
print(f"Found {len(classic_comps)} Classic competitions")

# Get competitions that require qualification
qualified_comps = [c for c in data['competitions'] if c['qualification_required']]
print(f"Found {len(qualified_comps)} competitions requiring qualification")
```

### Get upcoming competitions
```python
from datetime import date
import json

with open('knkf_competitions.json', 'r') as f:
    data = json.load(f)

today = date.today().isoformat()
upcoming = [c for c in data['competitions'] 
           if c['start_date'] and c['start_date'] >= today]

print(f"Found {len(upcoming)} upcoming competitions")
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml
- python-dateutil
- supabase (for database integration)
- python-dotenv (for environment variables)

## Supabase Setup

For database integration, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed setup instructions.

## Notes

- The scraper respects the website's structure and uses appropriate delays
- Competition data is scraped from the main calendar table
- Individual competition pages are not scraped by default for performance reasons
- The scraper handles various date formats and competition types

## Troubleshooting

If you encounter issues:

1. **No competitions found**: The website structure may have changed. Check if the site is accessible.
2. **SSL warnings**: These are normal and don't affect functionality.
3. **Network errors**: Check your internet connection and try again.

## Contributing

Feel free to contribute by:
- Reporting bugs
- Suggesting improvements
- Adding new features
- Improving documentation

## Legal Notice

This scraper is for educational and personal use only. Please respect the website's terms of service and don't overload their servers with requests.