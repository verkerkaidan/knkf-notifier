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

    # 4. If changes, send notification and update Supabase
    if added or removed or updated:
        # Format detailed change report
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
        send_email(subject, body)
        db.bulk_upsert_competitions(scraped_competitions)
        print("Changes detected, notification sent, and Supabase updated.")
    else:
        print("No changes detected.")


if __name__ == "__main__":
    main()
