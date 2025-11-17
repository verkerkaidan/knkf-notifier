#!/usr/bin/env python3
"""
KNKF Powerlifting Competition Scraper

This script scrapes powerlifting competitions from the KNKF website
and extracts relevant information such as competition names, dates,
locations, and organizations.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from dateutil import parser
import json
import re
from typing import List, Dict, Optional
import logging
from database import SupabaseDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KNKFScraper:
    """Scraper for KNKF powerlifting competitions"""
    
    def __init__(self):
        self.base_url = "https://knkf-sectiepowerliften.nl"
        self.calendar_url = f"{self.base_url}/kalender/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        try:
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(date_str.strip(), fmt).date()
                except ValueError:
                    continue
            
            # Try using dateutil parser as fallback
            return parser.parse(date_str.strip()).date()
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            return None
    
    def extract_competitions_from_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract competitions from the calendar table"""
        competitions = []
        
        # Look for the main calendar table
        calendar_table = soup.find('table', {'id': 'calendar'})
        
        if not calendar_table:
            logger.warning("Could not find calendar table")
            return competitions
        
        # Get table body
        tbody = calendar_table.find('tbody')
        if not tbody:
            logger.warning("Could not find table body")
            return competitions
        
        # Process each row
        rows = tbody.find_all('tr')
        logger.info(f"Found {len(rows)} rows in calendar table")
        
        for row in rows:
            competition = self.parse_competition_row_new(row)
            if competition:
                competitions.append(competition)
        
        return competitions
    
    def parse_competition_row_new(self, row) -> Optional[Dict]:
        """Parse a competition from a table row using the new structure"""
        try:
            cells = row.find_all('td')
            if len(cells) < 6:  # Expected: Date, Name, Location, Organization, Status, Capacity
                return None
            
            competition = {
                'name': '',
                'location': '',
                'organization': '',
                'status': '',
                'capacity': '',
                'start_date': None,
                'end_date': None,
                'url': None,
                'qualification_required': False,
                'competition_type': ''
            }
            
            # Parse date cell (first column)
            date_cell = cells[0]
            date_text = date_cell.get_text(strip=True)
            dates = self.extract_dates_from_text(date_text)
            if dates:
                competition['start_date'] = dates[0].isoformat()
                competition['end_date'] = dates[-1].isoformat() if len(dates) > 1 else dates[0].isoformat()
            
            # Parse name cell (second column)
            name_cell = cells[1]
            
            # Try to get competition name from link first
            name_link = name_cell.find('a')
            if name_link:
                name_text = name_link.get_text(strip=True)
                href = name_link.get('href')
                
                # Skip links that are not actual competitions (like qualification requirements)
                if href and '/kalender/' in href and 'kwalificatie-eisen' not in href:
                    competition['name'] = name_text
                    competition['url'] = href if href.startswith('http') else f"{self.base_url}{href}"
            
            # If no valid link found, try to extract name from plain text
            if not competition['name']:
                # Get the raw text and split into lines for better parsing
                cell_html = str(name_cell)
                lines = name_cell.get_text().split('\n')
                
                # The first line (before any <br> or labels) is usually the competition name
                potential_name = lines[0].strip() if lines else ""
                
                # Clean up the name by removing only unwanted descriptive text patterns
                # Be careful not to remove important parts of competition names
                import re
                
                # Remove long descriptive text that comes after the main name
                # Be careful with patterns - don't remove competition names that contain these words
                patterns_to_remove = [
                    r'\s+Sectievergadering.*$',
                    r'\s+Inclusief.*$', 
                    r'\s+Exacte.*$',
                    r'\s+Maximaal\s+\d+\s+teams.*$',  # More specific pattern for team descriptions
                    r'\s+Meer info.*$'
                ]
                
                for pattern in patterns_to_remove:
                    potential_name = re.sub(pattern, '', potential_name, flags=re.IGNORECASE)
                
                # Remove common label words only if they appear at the end or standalone
                # Don't remove them if they're part of the actual competition name
                label_words = ['👑 Kwalificatie vereist']
                for label in label_words:
                    potential_name = potential_name.replace(label, '').strip()
                
                # Additional cleanup: remove extra whitespace
                potential_name = ' '.join(potential_name.split())
                
                # If we have a reasonable name, use it
                if potential_name and len(potential_name) > 3:
                    competition['name'] = potential_name
            
            # Extract competition type from labels
            labels = name_cell.find_all('span', class_='label')
            for label in labels:
                label_text = label.get_text(strip=True)
                if 'Classic' in label_text:
                    competition['competition_type'] = 'Classic'
                elif 'Equipped' in label_text:
                    competition['competition_type'] = 'Equipped'
                elif 'Powerliften' in label_text:
                    if not competition['competition_type']:  # Don't overwrite Classic/Equipped
                        competition['competition_type'] = 'Powerlifting'
                elif 'Beginner' in label_text:
                    competition['competition_type'] = 'Beginner'
                elif 'Kwalificatie vereist' in label_text or '👑' in label_text:
                    competition['qualification_required'] = True
            
            # Parse location (third column)
            competition['location'] = cells[2].get_text(strip=True)
            
            # Parse organization (fourth column)
            competition['organization'] = cells[3].get_text(strip=True)
            
            # Parse status (fifth column)
            competition['status'] = cells[4].get_text(strip=True)
            
            # Parse capacity (sixth column)
            competition['capacity'] = cells[5].get_text(strip=True)
            
            # Filter out non-competition entries like Sectievergaderingen (section meetings)
            if competition['name']:
                name_lower = competition['name'].lower()
                excluded_terms = ['sectievergadering', 'bestuursvergadering', 'algemene ledenvergadering']
                if any(term in name_lower for term in excluded_terms):
                    return None
            
            return competition if competition['name'] else None
            
        except Exception as e:
            logger.warning(f"Error parsing competition row: {e}")
            return None
    
    def parse_competition_from_link(self, link_element) -> Optional[Dict]:
        """Parse competition information from a competition link"""
        try:
            href = link_element.get('href', '')
            name = link_element.get_text(strip=True)
            
            if not name or len(name) < 3:
                return None
            
            # Skip navigation links and other non-competition links
            if any(skip in name.lower() for skip in ['home', 'nieuws', 'contact', 'privacy', 'kalender']):
                return None
            
            competition = {
                'name': name,
                'location': '',
                'organization': '',
                'status': '',
                'capacity': '',
                'start_date': None,
                'end_date': None,
                'url': href if href.startswith('http') else f"{self.base_url}{href}",
                'qualification_required': False,
                'competition_type': ''
            }
            
            # Try to find additional information in the surrounding elements
            parent = link_element.parent
            if parent:
                parent_text = parent.get_text()
                
                # Look for qualification requirements
                if 'KWALIFICATIE VEREIST' in parent_text or '👑' in parent_text:
                    competition['qualification_required'] = True
                
                # Determine competition type
                if 'CLASSIC' in parent_text.upper():
                    competition['competition_type'] = 'Classic'
                elif 'EQUIPPED' in parent_text.upper():
                    competition['competition_type'] = 'Equipped'
                elif 'POWERLIFTEN' in parent_text.upper():
                    competition['competition_type'] = 'Powerlifting'
                
                # Extract dates
                dates = self.extract_dates_from_text(parent_text)
                if dates:
                    competition['start_date'] = dates[0].isoformat()
                    competition['end_date'] = dates[-1].isoformat() if len(dates) > 1 else dates[0].isoformat()
                
                # Try to extract location and organization from surrounding text
                # Look for common Dutch city names
                dutch_cities = ['Amsterdam', 'Rotterdam', 'Utrecht', 'Den Haag', 'Eindhoven', 
                               'Tilburg', 'Groningen', 'Leiden', 'Haarlem', 'Almere', 
                               'Breda', 'Nijmegen', 'Enschede', 'Apeldoorn']
                
                for city in dutch_cities:
                    if city in parent_text:
                        competition['location'] = city
                        break
            
            return competition
            
        except Exception as e:
            logger.warning(f"Error parsing competition from link: {e}")
            return None
    
    def extract_dates_from_text(self, text: str) -> List[date]:
        """Extract dates from text using regex patterns"""
        dates = []
        
        # Pattern for YYYY-MM-DD format
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        matches = re.findall(date_pattern, text)
        
        for match in matches:
            parsed_date = self.parse_date(match)
            if parsed_date:
                dates.append(parsed_date)
        
        return dates
    
    def extract_competitions_from_content(self, soup: BeautifulSoup) -> List[Dict]:
        """Alternative method to extract competitions from page content"""
        competitions = []
        
        # Look for specific patterns in the page content
        # This method tries to parse the content structure we saw in the webpage
        
        # Find all divs or sections that might contain competition info
        content_sections = soup.find_all(['div', 'section', 'article'])
        
        for section in content_sections:
            text_content = section.get_text()
            
            # Look for competition patterns
            if any(keyword in text_content.lower() for keyword in ['nsk', 'powerliften', 'wedstrijd']):
                competition = self.parse_competition_from_text(section)
                if competition:
                    competitions.append(competition)
        
        return competitions
    
    def parse_competition_from_text(self, element) -> Optional[Dict]:
        """Parse competition information from a text element"""
        try:
            text = element.get_text(strip=True)
            
            # Skip if not relevant
            if len(text) < 10 or not any(keyword in text.lower() for keyword in ['powerliften', 'wedstrijd']):
                return None
            
            competition = {
                'name': '',
                'location': '',
                'organization': '',
                'status': 'Unknown',
                'capacity': '',
                'start_date': None,
                'end_date': None,
                'url': None,
                'qualification_required': False,
                'competition_type': '',
                'raw_text': text[:200]  # Keep some raw text for debugging
            }
            
            # Try to extract name from links
            links = element.find_all('a')
            if links:
                competition['name'] = links[0].get_text(strip=True)
                href = links[0].get('href')
                if href:
                    competition['url'] = href if href.startswith('http') else f"{self.base_url}{href}"
            
            # Extract dates
            dates = self.extract_dates_from_text(text)
            if dates:
                competition['start_date'] = dates[0].isoformat()
                competition['end_date'] = dates[-1].isoformat() if len(dates) > 1 else dates[0].isoformat()
            
            # Check for qualification requirements
            if 'KWALIFICATIE VEREIST' in text or '👑' in text:
                competition['qualification_required'] = True
            
            # Determine competition type
            if 'CLASSIC' in text.upper():
                competition['competition_type'] = 'Classic'
            elif 'POWERLIFTEN' in text.upper():
                competition['competition_type'] = 'Equipped'
            
            # Extract location and organization with regex
            # This is a simplified approach - might need refinement
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and not competition['location'] and len(line) < 50:
                    # Potential location
                    if any(city in line for city in ['Amsterdam', 'Rotterdam', 'Utrecht', 'Den Haag', 'Eindhoven', 'Tilburg', 'Groningen', 'Leiden']):
                        competition['location'] = line
                        break
            
            return competition if competition['name'] else None
            
        except Exception as e:
            logger.warning(f"Error parsing competition from text: {e}")
            return None
    
    def get_competition_details(self, competition: Dict) -> Dict:
        """Fetch detailed information from a competition's individual page"""
        if not competition.get('url'):
            return competition
        
        try:
            soup = self.fetch_page(competition['url'])
            if not soup:
                return competition
            
            # Try to extract more detailed information
            content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main'])
            
            if content:
                text = content.get_text()
                
                # Look for additional details like organization, dates, etc.
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for i, line in enumerate(lines):
                    # Look for organization information
                    if 'organisatie' in line.lower() and i + 1 < len(lines):
                        competition['organization'] = lines[i + 1]
                    
                    # Look for location information
                    if 'locatie' in line.lower() and i + 1 < len(lines):
                        competition['location'] = lines[i + 1]
                    
                    # Look for status information
                    if 'status' in line.lower() and i + 1 < len(lines):
                        competition['status'] = lines[i + 1]
            
        except Exception as e:
            logger.warning(f"Error fetching details for {competition.get('name', 'Unknown')}: {e}")
        
        return competition
    
    def scrape_competitions(self) -> List[Dict]:
        """Main method to scrape all competitions"""
        logger.info("Starting KNKF competition scraping...")
        
        soup = self.fetch_page(self.calendar_url)
        if not soup:
            logger.error("Failed to fetch the calendar page")
            return []
        
        # Extract competitions from the main calendar table
        competitions = self.extract_competitions_from_table(soup)
        
        # Filter out invalid competitions
        valid_competitions = []
        for comp in competitions:
            if comp.get('name') and len(comp.get('name', '').strip()) > 2:
                valid_competitions.append(comp)
        
        logger.info(f"Found {len(valid_competitions)} valid competitions")
        return valid_competitions
    
    def save_to_json(self, competitions: List[Dict], filename: str = "knkf_competitions.json"):
        """Save competitions to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'scraped_at': datetime.now().isoformat(),
                    'source_url': self.calendar_url,
                    'total_competitions': len(competitions),
                    'competitions': competitions
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(competitions)} competitions to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def save_to_database(self, competitions: List[Dict]) -> int:
        """Save competitions to Supabase database"""
        try:
            db = SupabaseDatabase()
            return db.bulk_upsert_competitions(competitions)
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return 0


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KNKF Powerlifting Competition Scraper')
    parser.add_argument('--output', '-o', default='knkf_competitions.json', 
                       help='Output JSON filename (default: knkf_competitions.json)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--show-all', '-a', action='store_true', 
                       help='Show all competitions in summary (default: first 5)')
    parser.add_argument('--database', '-d', action='store_true', 
                       help='Save to Supabase database (requires .env file with credentials)')
    parser.add_argument('--no-json', action='store_true', 
                       help='Skip saving to JSON file')
    
    args = parser.parse_args()
    
    if not args.verbose:
        # Reduce logging noise
        logging.getLogger().setLevel(logging.WARNING)
    
    scraper = KNKFScraper()
    
    # Scrape competitions
    competitions = scraper.scrape_competitions()
    
    if competitions:
        # Save to JSON (unless disabled)
        if not args.no_json:
            scraper.save_to_json(competitions, args.output)
        
        # Save to database (if requested)
        db_count = 0
        if args.database:
            try:
                db_count = scraper.save_to_database(competitions)
            except Exception as e:
                print(f"❌ Database error: {e}")
                print("Make sure you have:")
                print("1. Created a .env file with SUPABASE_URL and SUPABASE_KEY")
                print("2. Created the competitions table in Supabase")
        
        # Print summary
        print(f"\n🏋️‍♀️ KNKF Powerlifting Competition Summary")
        print(f"=" * 50)
        print(f"📅 Total competitions found: {len(competitions)}")
        if not args.no_json:
            print(f"💾 Saved to JSON: {args.output}")
        if args.database:
            print(f"🗃️  Saved to database: {db_count}/{len(competitions)} competitions")
        print(f"🌐 Source: {scraper.calendar_url}")
        
        # Show competitions
        show_count = len(competitions) if args.show_all else min(5, len(competitions))
        
        for i, comp in enumerate(competitions[:show_count], 1):
            print(f"\n{i}. 🏆 {comp['name']}")
            if comp['start_date'] and comp['end_date']:
                if comp['start_date'] == comp['end_date']:
                    print(f"   📅 Date: {comp['start_date']}")
                else:
                    print(f"   📅 Dates: {comp['start_date']} to {comp['end_date']}")
            if comp['location']:
                print(f"   📍 Location: {comp['location']}")
            if comp['organization']:
                print(f"   🏢 Organization: {comp['organization']}")
            if comp['competition_type']:
                print(f"   🎯 Type: {comp['competition_type']}")
            if comp['status']:
                print(f"   ✅ Status: {comp['status']}")
            if comp['qualification_required']:
                print(f"   👑 Qualification Required: Yes")
            if comp['url']:
                print(f"   🔗 More info: {comp['url']}")
        
        if len(competitions) > show_count:
            remaining = len(competitions) - show_count
            print(f"\n... and {remaining} more competition{'s' if remaining > 1 else ''}")
            print(f"Use --show-all to see all competitions")
        
        print(f"\n✨ Scraping completed successfully!")
        
    else:
        print("❌ No competitions found. The website structure might have changed.")
        print("Please check the website manually or report this issue.")


if __name__ == "__main__":
    main()
