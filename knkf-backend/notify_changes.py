import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import SupabaseDatabase
from scraper import KNKFScraper
from difflib import unified_diff
from typing import List, Dict

# --- CONFIG ---
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", GMAIL_USER)

# --- CHANGE DETECTION ---
def compare_competitions(old: List[Dict], new: List[Dict]):
    def comp_key(c):
        return f"{c.get('name','')}|{c.get('start_date','')}"
    old_map = {comp_key(c): c for c in old}
    new_map = {comp_key(c): c for c in new}

    added = [c for k, c in new_map.items() if k not in old_map]
    removed = [c for k, c in old_map.items() if k not in new_map]
    updated = []
    for k, c in new_map.items():
        if k in old_map:
            changes = {}
            for field in c:
                if field in old_map[k] and c[field] != old_map[k][field]:
                    changes[field] = {'old': old_map[k][field], 'new': c[field]}
            if changes:
                updated.append({'key': k, 'name': c.get('name',''), 'changes': changes})
    return added, removed, updated

# --- EMAIL SENDING ---
def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

# --- MAIN ---
def main():
    db = SupabaseDatabase()
    old_comps = db.get_all_competitions()
    scraper = KNKFScraper()
    new_comps = scraper.scrape_competitions()

    added, removed, updated = compare_competitions(old_comps, new_comps)
    if not (added or removed or updated):
        print("No changes detected.")
        return

    # Format detailed change report
    lines = []
    if added:
        lines.append(f"New competitions ({len(added)}):")
        for c in added:
            lines.append(f"- {c['name']} ({c['start_date']} - {c['end_date']}) @ {c['location']}")
    if removed:
        lines.append(f"\nRemoved competitions ({len(removed)}):")
        for c in removed:
            lines.append(f"- {c['name']} ({c['start_date']} - {c['end_date']}) @ {c['location']}")
            if 'id' in c:
                db.delete_competition(c['id'])
    if updated:
        lines.append(f"\nUpdated competitions ({len(updated)}):")
        for u in updated:
            lines.append(f"- {u['name']} (ID: {u['id']})")
            for field, change in u['changes'].items():
                lines.append(f"    {field}: '{change['old']}' → '{change['new']}'")
    body = '\n'.join(lines)

    subject = f"KNKF Competition Changes Detected ({len(added)} new, {len(removed)} removed, {len(updated)} updated)"
    send_email(subject, body)
    db.bulk_upsert_competitions(new_comps)
    print("Change notification sent and database updated.")

if __name__ == "__main__":
    main()
