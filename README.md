# KNKF Notifier

Get notified when new powerlifting competitions are added to the KNKF calendar.

I'm a powerlifter, and the Dutch powerlifting federation (KNKF) publishes its competition calendar on its website but offers no mailing list or any other way to be told when a new competition appears. That meant checking the page by hand and still missing competitions that filled up quickly. So I built something that does the checking for me.

## What it does

- **Scrapes** the national powerlifting calendar at [knkf-sectiepowerliften.nl](https://knkf-sectiepowerliften.nl/kalender/): dates, names, locations, organisers, competition type (Classic, Equipped, Beginner), qualification requirements and status.
- **Detects changes** by comparing the scraped list with what is stored in Supabase: new, removed and updated competitions (with the old and new value of every changed field).
- **Sends an email** summarising those changes through Gmail SMTP, only when something changed.
- **Runs on a schedule** with a GitHub Actions workflow (`.github/workflows/notify-changes.yml`) that runs once a day at midnight UTC, or on demand.
- **Shows the calendar** in a small web frontend where competitions can be filtered by type, qualification requirement and upcoming dates.

## Tech stack

| Part | Technology |
|---|---|
| Scraper and notifier | Python (requests, BeautifulSoup, lxml) |
| Database | Supabase (PostgreSQL) |
| Email | Gmail SMTP |
| Scheduling | GitHub Actions |
| API | FastAPI, with a rate limit and optional API key |
| Frontend | Next.js 16, React 19, Tailwind CSS 4, TanStack React Query |

## Project structure

```
knkf-backend/
├── scraper.py          Scrapes the KNKF calendar
├── database.py         Supabase access
├── notify_changes.py   Diffs old vs. new and emails the changes
├── main.py             Scrape, compare, notify and update in one run
├── api.py              FastAPI app (/, /health, /api/scrape)
└── .env.example
knkf-frontend/          Next.js app that reads competitions from Supabase
.github/workflows/      Scheduled notification job
DEPLOYMENT.md           Deploying the API (Railway/Render/Fly.io) and frontend (Vercel)
```

More detail is in `knkf-backend/README.md`, `knkf-backend/SUPABASE_SETUP.md` and `knkf-frontend/SECURITY.md`.

## How to run

**Requirements:** Python 3.11+, Node.js 20+ for the frontend, and a free [Supabase](https://supabase.com) project.

### 1. Set up the database

Create a Supabase project and a `competitions` table, following `knkf-backend/SUPABASE_SETUP.md`.

### 2. Run the scraper and notifier

```bash
git clone https://github.com/verkerkaidan/knkf-notifier.git
cd knkf-notifier/knkf-backend
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your `SUPABASE_URL` and `SUPABASE_KEY`. To get emails, also set `GMAIL_USER`, `GMAIL_PASS` (a Gmail app password) and optionally `RECIPIENT_EMAIL`. Then:

```bash
python scraper.py --verbose      # scrape and save to JSON
python scraper.py --database     # scrape and save to Supabase
python notify_changes.py         # detect changes and send the email
```

### 3. Run it daily on GitHub Actions

Fork the repository and add these as repository secrets: `SUPABASE_URL`, `SUPABASE_KEY`, `API_KEY`, `COMPETITIONS_TABLE`, `GMAIL_USER`, `GMAIL_PASS` and `RECIPIENT_EMAIL`. The workflow in `.github/workflows/notify-changes.yml` then runs daily.

### 4. Run the API (optional)

```bash
cd knkf-backend
pip install -r requirements-api.txt
uvicorn api:app --reload
```

### 5. Run the frontend

```bash
cd knkf-frontend
npm install
npm run dev
```

The frontend needs `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `knkf-frontend/.env.local`. See `DEPLOYMENT.md` for the full list.
