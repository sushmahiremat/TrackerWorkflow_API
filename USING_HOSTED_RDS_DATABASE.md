# Using Hosted RDS Database - Complete Guide

## How Database Changes Work

### When You Change Data in pgAdmin

1. **pgAdmin connects to RDS:**

   - pgAdmin connects directly to your RDS database over the internet
   - Connection string: `trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432`

2. **Changes are immediate:**

   - When you change a password (or any data) in pgAdmin and save/commit
   - The change is **immediately written** to the RDS database
   - The database is **persistent** - changes are saved permanently

3. **No sync needed:**
   - RDS is your **single source of truth**
   - pgAdmin is just a tool to view/edit the database
   - Your application (App Runner) reads from the same database
   - Changes in pgAdmin are immediately available to your application

## How Your Application Uses the Hosted Database

### Current Setup

Your RDS database:

- **Endpoint:** `trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com`
- **Port:** `5432`
- **Database:** `TrackerWorkflow`
- **Username:** `postgres`
- **Password:** (the one you set when creating RDS)

### Connection Flow

```
pgAdmin → RDS Database (trackerworkflow-db)
   ↓
   Changes saved immediately
   ↓
App Runner → Reads from same RDS Database
```

## Step-by-Step: Using Hosted RDS with Your Application

### Step 1: Get Your RDS Connection Details

From your RDS console (you already have these):

- **Endpoint:** `trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com`
- **Port:** `5432`
- **Database:** `TrackerWorkflow`
- **Username:** `postgres`
- **Password:** (the master password you set)

### Step 2: Update App Runner Environment Variables

Your App Runner backend service needs to connect to RDS:

1. **Go to App Runner Console:**

   - Service: `service_track` (your backend)
   - Configuration tab
   - Click "Edit"

2. **Update DATABASE_URL:**

   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
   ```

   Replace `YOUR_PASSWORD` with your actual RDS master password.

3. **Save and Rebuild:**
   - Click "Save changes"
   - Or click "Rebuild" button
   - Wait for deployment

### Step 3: Verify Connection

After updating, check App Runner logs:

- Should see: "✅ Using DATABASE_URL from environment"
- Should see: "🔗 Connecting to database: postgresql://postgres:...@trackerworkflow-db..."
- Should see: "✅ Database tables created/verified successfully"

## How Changes Propagate

### Example: Changing User Password

1. **In pgAdmin:**

   ```sql
   UPDATE users SET password = 'new_hashed_password' WHERE email = 'user@example.com';
   ```

2. **What happens:**

   - Change is **immediately saved** to RDS
   - RDS persists the change to disk
   - Change is **permanent** (survives restarts)

3. **In your application:**
   - Next time user tries to login
   - App Runner reads from RDS
   - Gets the **updated password** from RDS
   - Authentication uses the new password

### Data Flow Diagram

```
┌─────────────┐
│   pgAdmin   │  ← You edit data here
└──────┬──────┘
       │ SQL UPDATE/INSERT/DELETE
       ↓
┌─────────────────────────────────────┐
│   RDS Database (trackerworkflow-db) │  ← Single source of truth
│   - PostgreSQL                      │
│   - Persistent storage              │
└──────┬──────────────────────────────┘
       │
       │ Application reads/writes
       ↓
┌─────────────┐
│ App Runner   │  ← Your FastAPI backend
│ (Backend)    │     reads from RDS
└─────────────┘
```

## Connecting to RDS from Different Tools

### 1. pgAdmin (What you're using)

**Connection Settings:**

- **Host:** `trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com`
- **Port:** `5432`
- **Database:** `TrackerWorkflow`
- **Username:** `postgres`
- **Password:** Your RDS master password

### 2. Your Application (App Runner)

**Environment Variable:**

```
DATABASE_URL=postgresql://postgres:PASSWORD@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

### 3. Local Development

**Option A: Connect to RDS directly**

```python
# In your .env file
DATABASE_URL=postgresql://postgres:PASSWORD@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

**Option B: Use local database for development**

```python
# In your .env file (local)
DATABASE_URL=postgresql://postgres:123@localhost:5432/TrackerWorkflow
```

## Important Notes

### 1. Single Source of Truth

- **RDS is the database** - all data lives there
- pgAdmin is just a **viewer/editor**
- Your application reads/writes to RDS
- All changes are **immediate and permanent**

### 2. No Sync Needed

- Changes in pgAdmin → **immediately in RDS**
- Changes via your app → **immediately in RDS**
- Both read/write to the **same database**
- No synchronization needed

### 3. Password Changes

When you change a user password in pgAdmin:

- The change is **saved to RDS immediately**
- Your application will use the new password on next login
- No restart needed
- No sync needed

### 4. Data Persistence

- RDS automatically backs up your database
- Data survives:
  - Application restarts
  - App Runner redeployments
  - Server reboots
  - Region failures (if using Multi-AZ)

## Security Best Practices

### 1. Use Strong Passwords

- RDS master password should be strong
- User passwords should be hashed (bcrypt) - your app does this

### 2. Limit Access

- Only allow necessary IPs in security group
- Use IAM database authentication if possible
- Don't expose RDS publicly unless needed

### 3. Use Environment Variables

- Never hardcode passwords in code
- Use App Runner environment variables
- Use AWS Secrets Manager for sensitive values

## Troubleshooting

### Can't Connect from App Runner?

1. **Check Security Group:**

   - RDS security group must allow inbound on port 5432
   - Source should be App Runner's IP range or `0.0.0.0/0`

2. **Check DATABASE_URL:**

   - Verify password is correct
   - Verify endpoint is correct
   - Check for typos

3. **Check RDS Status:**
   - RDS must be "Available"
   - Check RDS console for any issues

### Changes Not Reflecting?

1. **Commit transactions:**

   - In pgAdmin, make sure to commit changes
   - Some tools require explicit commit

2. **Check connection:**

   - Verify you're connected to the right database
   - Check you're editing the right table

3. **Check application:**
   - App Runner might be caching
   - Restart App Runner service if needed

## Quick Reference

### RDS Connection String Format

```
postgresql://[username]:[password]@[endpoint]:[port]/[database]
```

### Your Current RDS Details

```
Endpoint: trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com
Port: 5432
Database: TrackerWorkflow
Username: postgres
Password: (your RDS master password)
```

### Complete Connection String

```
postgresql://postgres:YOUR_PASSWORD@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

## Summary

1. **RDS is your database** - all data lives there permanently
2. **pgAdmin is a tool** - to view/edit the database
3. **Changes are immediate** - no sync needed
4. **Your app reads from RDS** - same database, same data
5. **Update App Runner** - set DATABASE_URL to point to RDS
6. **That's it!** - everything uses the same hosted database
