# Supabase Setup Guide

Complete guide to set up Supabase cloud database for your Fraud Detection System.

---

## Step 1: Create Supabase Account & Project

1. **Sign up for Supabase**
   - Go to [supabase.com](https://supabase.com)
   - Click "Start your project" or "Sign In"
   - Sign up with GitHub, Google, or email

2. **Create a new project**
   - Click "New Project"
   - Choose your organization (or create one)
   - Fill in project details:
     - **Name**: `fraud-detection` (or any name you prefer)
     - **Database Password**: Create a strong password (save this!)
     - **Region**: Choose closest to you
   - Click "Create new project"
   - Wait 2-3 minutes for setup to complete

---

## Step 2: Get Your API Credentials

1. Go to **Project Settings** (gear icon in sidebar)
2. Click on **API** section
3. You'll find:
   - **Project URL** → Copy this as `SUPABASE_URL`
   - **Project API keys** → Copy **`anon public`** key as `SUPABASE_KEY`

**Example:**
```
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...
```

> ⚠️ **Important**: Use the `anon public` key, NOT the `service_role secret` key!

---

## Step 3: Add Credentials to .env File

1. Open the `.env` file in your project root
2. Replace the placeholders:

```env
# Replace these values with your actual Supabase credentials
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_public_key_here
```

---

## Step 4: Run SQL Schema Script

1. In your Supabase dashboard, go to **SQL Editor** (in the sidebar)
2. Click **"New query"**
3. Open the file `database/supabase_schema.sql` from this project
4. **Copy all the SQL code** from that file
5. **Paste it** into the SQL Editor
6. Click **"Run"** (or press `Ctrl+Enter`)

You should see: ✅ Success. No rows returned

---

## Step 5: Verify Database Setup

1. In Supabase dashboard, go to **Table Editor** (in sidebar)
2. You should see 2 tables:
   - ✅ `transactions`
   - ✅ `flagged_transactions`

3. You can also run this query in SQL Editor to verify:
```sql
SELECT * FROM fraud_statistics;
```
It should return a row with all zeros (since no transactions yet).

---

## Step 6: Install Supabase Python Client

In your project directory, run:

```bash
pip install supabase
```

Or if you've updated `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Step 7: Test the Connection (Optional)

Create a test file `test_supabase.py`:

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Test query
result = supabase.table('transactions').select("*").limit(5).execute()
print(f"✅ Connected! Transactions count: {len(result.data)}")
```

Run it:
```bash
python test_supabase.py
```

---

## Troubleshooting

### Error: "relation does not exist"
- You haven't run the SQL schema script yet
- Go back to Step 4 and run the SQL script

### Error: "Invalid API key"
- Check that you copied the **anon public** key, not the service_role key
- Make sure there are no extra spaces in your `.env` file

### Error: "Could not connect to Supabase"
- Verify your `SUPABASE_URL` is correct (should include `https://`)
- Check your internet connection

### RLS Policy Issues
- Make sure you ran the entire SQL script (including the RLS policies section)
- In Supabase dashboard, go to **Authentication** → **Policies** to verify

---

## What's Next?

Once setup is complete, your Fraud Detection System will:
- ✅ Automatically log every transaction to Supabase
- ✅ Flag high-risk transactions (BLOCK/REVIEW)
- ✅ Show transaction history in the Streamlit dashboard
- ✅ Calculate fraud rate statistics

You're ready to proceed with the backend integration! 🚀
