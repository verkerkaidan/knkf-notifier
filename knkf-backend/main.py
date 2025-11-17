"""
main.py: Orchestrates scraping, comparison, notification, and Supabase update for KNKF competitions.
"""

from scraper import KNKFScraper
from database import SupabaseDatabase
from notify_changes import compare_competitions, send_email


def main():
    # 1. Scrape latest competitions
    scraper = KNKFScraper()
    scraped_competitions = scraper.scrape_competitions()

    # 2. Fetch competitions from Supabase
    db = SupabaseDatabase()
    supabase_competitions = db.get_all_competitions()

    # 3. Compare competitions
    added, removed, updated = compare_competitions(supabase_competitions, scraped_competitions)

    # 4. If changes, send notification
    if added or removed or updated:
        lines = []
        if added:
            lines.append("Added competitions:")
            for c in added:
                lines.append(f"- {c.get('name','')} ({c.get('start_date','')})")
        if removed:
            lines.append("\nRemoved competitions:")
            for c in removed:
                lines.append(f"- {c.get('name','')} ({c.get('start_date','')})")
        if updated:
            lines.append("\nUpdated competitions:")
            for u in updated:
                lines.append(f"- {u['name']}:")
                for field, change in u['changes'].items():
                    lines.append(f"    {field}: {change['old']} -> {change['new']}")
        body = '\n'.join(lines)
        subject = "KNKF Competition Changes Detected"
        # send_email(subject, body)  # Disabled for deployment
        print("Changes detected, notification sent.")
    else:
        print("No changes detected.")

    # 5. Replace all competitions in the database with the newly scraped ones
    all_db_comps = db.get_all_competitions()
    for comp in all_db_comps:
        if 'id' in comp:
            db.delete_competition(comp['id'])
    db.bulk_upsert_competitions(scraped_competitions)
    print("Database replaced with newly scraped competitions.")


if __name__ == "__main__":
    main()
