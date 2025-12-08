# 🗄️ Setup Local Database Connection

## ✅ What I Did

I created a `.env` file in `TrackerWorkflow_API/` with local database configuration.

## 🔧 Step 1: Update Your Local PostgreSQL Password

The `.env` file I created uses:

```
DATABASE_URL=postgresql://postgres:123@localhost:5432/TrackerWorkflow
```

**If your local PostgreSQL password is NOT `123`, update it:**

1. Open `TrackerWorkflow_API/.env`
2. Change `123` to your actual PostgreSQL password:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/TrackerWorkflow
   ```

## 🗄️ Step 2: Make Sure PostgreSQL is Running Locally

### Check if PostgreSQL is installed:

**Windows:**

```powershell
# Check if PostgreSQL service is running
Get-Service -Name postgresql*

# Or check if psql is available
psql --version
```

**If PostgreSQL is NOT installed:**

1. **Download PostgreSQL:**

   - Go to: https://www.postgresql.org/download/windows/
   - Download and install PostgreSQL 14 or 15
   - During installation, remember the password you set for the `postgres` user

2. **After installation, update `.env` with your password**

### Check if PostgreSQL is running:

**Windows:**

```powershell
# Check service status
Get-Service -Name postgresql*

# Start service if not running
Start-Service -Name postgresql-x64-14  # Replace with your version
```

## 🗄️ Step 3: Create Local Database (if it doesn't exist)

If you don't have a `TrackerWorkflow` database locally:

**Option A: Using psql (Command Line)**

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE "TrackerWorkflow";

# Exit
\q
```

**Option B: Using pgAdmin**

1. Open pgAdmin
2. Connect to your local PostgreSQL server (usually `localhost`)
3. Right-click "Databases" → "Create" → "Database"
4. Name: `TrackerWorkflow`
5. Click "Save"

## 🚀 Step 4: Initialize Database Tables

Once the database exists, create the tables:

```powershell
cd TrackerWorkflow_API

# Activate virtual environment (if using one)
.\venv\Scripts\activate

# Run database initialization
python init_db.py
```

Or if you have a setup script:

```powershell
python setup_db.py
```

## ✅ Step 5: Test Local Connection

Test if the connection works:

```powershell
python test_connection.py
```

You should see:

```
✅ Successfully connected to database!
```

## 🔄 Step 6: Run Your Backend Locally

Now start your backend:

```powershell
# Make sure you're in TrackerWorkflow_API directory
cd TrackerWorkflow_API

# Activate virtual environment
.\venv\Scripts\activate

# Start the server
uvicorn main:app --reload --port 8001
```

You should see:

```
🔗 Connecting to database: postgresql://postgres:123@localhost:5432/TrackerWorkflow
INFO:     Uvicorn running on http://127.0.0.1:8001
```

## 🔀 Switching Between Local and Hosted Database

### Use Local Database (Current Setup)

The `.env` file is set to use local database. Just make sure:

- ✅ `.env` file exists with `DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/TrackerWorkflow`
- ✅ PostgreSQL is running locally
- ✅ `TrackerWorkflow` database exists locally

### Use Hosted RDS Database

To switch back to RDS, either:

**Option 1: Comment out DATABASE_URL in .env**

```env
# DATABASE_URL=postgresql://postgres:123@localhost:5432/TrackerWorkflow
```

Then the code will use the fallback settings in `config.py` (which point to RDS).

**Option 2: Update .env to use RDS**

```env
DATABASE_URL=postgresql://postgres:w1p.z|qj9VV!b|OiPaaRn|4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

## 🐛 Troubleshooting

### Error: "could not connect to server"

**Solution:**

- Make sure PostgreSQL service is running
- Check if port 5432 is correct
- Verify password in `.env` matches your PostgreSQL password

### Error: "database 'TrackerWorkflow' does not exist"

**Solution:**

- Create the database (see Step 3 above)
- Or change database name in `.env` to an existing database

### Error: "password authentication failed"

**Solution:**

- Update password in `.env` file
- Make sure you're using the correct username (usually `postgres`)

### Error: "connection refused"

**Solution:**

- PostgreSQL service might not be running
- Check firewall settings
- Verify PostgreSQL is listening on port 5432

## 📝 Quick Reference

**Local Database Connection:**

```
postgresql://postgres:YOUR_PASSWORD@localhost:5432/TrackerWorkflow
```

**Hosted RDS Connection:**

```
postgresql://postgres:w1p.z|qj9VV!b|OiPaaRn|4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

---

**Next Steps:**

1. Update `.env` with your local PostgreSQL password
2. Make sure PostgreSQL is running
3. Create `TrackerWorkflow` database if needed
4. Run `python init_db.py` to create tables
5. Start backend: `uvicorn main:app --reload --port 8001`
6. Test login from frontend!
