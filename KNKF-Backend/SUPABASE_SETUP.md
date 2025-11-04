# Supabase Setup Guide

Follow these steps to set up Supabase integration for the KNKF Competition Scraper.

## 🏗️ **1. Create a Supabase Project**

1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Wait for the project to be set up (takes ~2 minutes)

## 🔑 **2. Get Your Credentials**

1. Go to your project dashboard
2. Click on **Settings** (gear icon in sidebar)
3. Click on **API** in the settings menu
4. Copy these two values:
   - **Project URL** (something like `https://xxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

## 📝 **3. Configure Local Environment**

1. In your local project, copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and replace the placeholder values:
   ```bash
   # Your actual Supabase project URL
   SUPABASE_URL=https://your-project-ref.supabase.co
   
   # Your actual Supabase anon key
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   # Optional: Custom table name (default: competitions)
   COMPETITIONS_TABLE=competitions
   ```

## 🗃️ **4. Create the Database Table**

1. In your Supabase dashboard, go to **SQL Editor**
2. Run this command to get the schema:
   ```bash
   python db_manager.py schema
   ```
3. Copy the SQL output and paste it into the Supabase SQL Editor
4. Click **Run** to create the table

## ✅ **5. Test the Connection**

Test that everything works:

```bash
# Test scraping and saving to database
python scraper.py --database --verbose

# List competitions from database
python db_manager.py list

# Export from database to JSON
python db_manager.py export
```

## 🚫 **Security Notes**

- **NEVER** commit your `.env` file to git
- The `.env` file is already in `.gitignore` 
- Only commit `.env.example` with placeholder values
- For production deployment, use environment variables or secure secret management

## 📊 **Usage Examples**

```bash
# Scrape and save to both JSON and database
python scraper.py --database --show-all

# Save only to database (skip JSON)
python scraper.py --database --no-json

# List upcoming competitions from database
python db_manager.py list --upcoming

# List competitions requiring qualification
python db_manager.py list --qualification

# Export all competitions to JSON
python db_manager.py export --output my_competitions.json
```

## 🛠️ **Troubleshooting**

### "Missing Supabase credentials" error:
- Make sure `.env` file exists in the project root
- Check that `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
- Verify there are no extra spaces or quotes around the values

### Database connection issues:
- Verify your Supabase project is running (not paused)
- Check that the anon key has the correct permissions
- Make sure the `competitions` table exists

### "Table doesn't exist" error:
- Run the SQL schema in your Supabase SQL Editor
- Make sure the table name matches `COMPETITIONS_TABLE` in your `.env`