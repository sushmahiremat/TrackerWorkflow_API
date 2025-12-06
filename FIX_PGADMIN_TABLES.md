# Fix: Can't See Tables in pgAdmin for RDS Database

## Problem

You connected pgAdmin to your RDS database, but you can't see the tables that exist in your local database.

## Root Cause

1. **Wrong Database Selected:** You're viewing `rdsadmin` database, but your application uses `TrackerWorkflow` database
2. **Tables Not Created Yet:** The tables might not exist in RDS yet (they need to be created)

## Solution

### Step 1: Switch to Correct Database in pgAdmin

1. **In pgAdmin Object Explorer (left pane):**
   - Expand `awsdb` server
   - Expand `Databases`
   - You should see:
     - `postgres` (default database)
     - `rdsadmin` (system database - you're currently here)
     - `TrackerWorkflow` (your application database - **this is what you need**)

2. **Click on `TrackerWorkflow` database:**
   - This is where your application tables should be
   - Expand it to see:
     - `Schemas`
     - `Tables` (your tables should be here)

### Step 2: Check if Tables Exist

1. **Expand `TrackerWorkflow` → `Schemas` → `public` → `Tables`:**
   - You should see tables like:
     - `users`
     - `projects`
     - `tasks`
     - `comments`
     - `attachments`
     - `notifications`
     - `teams`
     - `team_members`
     - `activities`

2. **If Tables Don't Exist:**
   - The tables haven't been created in RDS yet
   - Continue to Step 3

### Step 3: Create Tables in RDS

Your application creates tables automatically when it starts, but only if it can connect to the database. You have two options:

#### Option A: Let Application Create Tables (Recommended)

1. **Make sure your backend can connect to RDS:**
   - Update `.env` file with correct `DATABASE_URL`:
     ```env
     DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
     ```

2. **Start your backend:**
   ```bash
   cd TrackerWorkflow_API
   python main.py
   ```
   Or:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Check logs:**
   - You should see: `✅ Database tables created/verified successfully`
   - This means tables were created in RDS

4. **Refresh pgAdmin:**
   - Right-click on `Tables` in pgAdmin
   - Click "Refresh"
   - Tables should now appear

#### Option B: Create Tables Manually in pgAdmin

1. **In pgAdmin:**
   - Right-click on `TrackerWorkflow` database
   - Click "Query Tool"

2. **Run this SQL to create tables:**
   ```sql
   -- This will create all tables based on your models
   -- You can get the SQL from your application or run migrations
   ```

   **Better approach:** Use Option A (let the app create them)

### Step 4: Verify Connection

1. **Check pgAdmin Connection Settings:**
   - Right-click on `awsdb` server → "Properties"
   - Verify:
     - **Host:** `trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com`
     - **Port:** `5432`
     - **Database:** `TrackerWorkflow` (not `rdsadmin`)
     - **Username:** `postgres`
     - **Password:** (from Secrets Manager)

2. **Test Connection:**
   - Click "Save" if you made changes
   - Try connecting again

## Why This Happens

1. **Different Databases:**
   - Local database: `TrackerWorkflow` (on localhost)
   - RDS has multiple databases: `postgres`, `rdsadmin`, `TrackerWorkflow`
   - You were looking at `rdsadmin` (system database) instead of `TrackerWorkflow`

2. **Tables Not Created:**
   - RDS database starts empty
   - Tables need to be created (either by app or manually)
   - Your local database already has tables, but RDS doesn't yet

## Quick Checklist

- [ ] Connected to correct database: `TrackerWorkflow` (not `rdsadmin`)
- [ ] Expanded: `TrackerWorkflow` → `Schemas` → `public` → `Tables`
- [ ] If no tables: Started backend to create tables automatically
- [ ] Refreshed pgAdmin after tables are created
- [ ] Verified connection settings in pgAdmin

## Expected Result

After fixing:
- ✅ You see `TrackerWorkflow` database in pgAdmin
- ✅ Tables are visible under `Schemas` → `public` → `Tables`
- ✅ You can view/edit data in RDS
- ✅ Changes in pgAdmin reflect immediately in your app

## Important Notes

1. **RDS is Separate from Local:**
   - Local database and RDS are completely separate
   - Data doesn't automatically sync
   - You need to create tables in RDS

2. **Tables Auto-Create:**
   - Your app creates tables on startup (see `main.py` line 31)
   - Just need to connect with correct `DATABASE_URL`

3. **Data Migration:**
   - If you want to copy data from local to RDS, you'll need to export/import
   - Or recreate data through your application

