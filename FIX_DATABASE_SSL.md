# Fix Database Connection - SSL Required for RDS

## 🔍 Problem

After OAuth login, the `/me` endpoint returns 500 error:
```
password authentication failed for user "postgres"
no pg_hba.conf entry for host "54.70.103.169", user "postgres", database "TrackerWorkflow", no encryption
```

**Root Cause:** AWS RDS requires SSL connections, but the database connection wasn't configured with SSL.

## ✅ Solution Applied

### 1. **Updated `database.py`** - Added SSL Support
   - Added SSL mode for RDS connections
   - Automatically detects RDS endpoints and enables SSL

### 2. **Code Changes:**
   ```python
   # Add SSL for RDS if connecting to AWS RDS (not localhost)
   if "rds.amazonaws.com" in database_url or "amazonaws.com" in database_url:
       connect_args["sslmode"] = "require"  # Require SSL for RDS
   ```

## 🔧 Additional Steps Required

### Step 1: Verify DATABASE_URL in App Runner

1. **Go to AWS App Runner Console:**
   - Service: Your backend service
   - Configuration → Environment Variables

2. **Check DATABASE_URL:**
   ```
   DATABASE_URL=postgresql://postgres:w1p.z|qj9VV!b|OiPaaRn|4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
   ```

3. **Verify:**
   - Password is correct
   - Host is correct (RDS endpoint)
   - Database name is correct (`TrackerWorkflow`)

### Step 2: Check RDS Security Group

The error "no pg_hba.conf entry" might also indicate:
- RDS security group doesn't allow connections from App Runner

1. **Go to RDS Console:**
   - Find your database: `trackerworkflow-db`
   - Check Security Groups

2. **Verify Inbound Rules:**
   - Should allow PostgreSQL (port 5432) from:
     - App Runner security group, OR
     - App Runner IP ranges, OR
     - `0.0.0.0/0` (for testing, not recommended for production)

### Step 3: Rebuild and Deploy

After code changes:
1. Commit and push to GitHub
2. CodeBuild will rebuild backend
3. App Runner will auto-deploy
4. Test again

## 🧪 Testing

After deployment:

1. **Check Backend Logs:**
   - Should see: `✅ Using DATABASE_URL from environment`
   - Should NOT see: `password authentication failed`

2. **Test Login:**
   - Visit frontend login page
   - Click "Sign in with Google"
   - Should redirect and load user successfully
   - Should NOT see 500 error on `/me`

## 📋 Checklist

- [x] Code updated to add SSL for RDS
- [ ] DATABASE_URL verified in App Runner
- [ ] RDS Security Group allows App Runner connections
- [ ] Backend rebuilt and deployed
- [ ] Login tested and working
- [ ] `/me` endpoint returns user data (not 500)

## 🚨 If Still Getting Errors

### Check 1: Password
- Verify password in DATABASE_URL matches RDS master password
- Special characters in password might need URL encoding

### Check 2: RDS Security Group
- App Runner IP: `54.70.103.169` (from error)
- Add this IP or App Runner security group to RDS inbound rules

### Check 3: Database Name
- Verify database name is exactly `TrackerWorkflow` (case-sensitive)

### Check 4: SSL Certificate
- If `sslmode=require` doesn't work, try `sslmode=prefer`
- Or add SSL certificate path if required

## 💡 Alternative: Use RDS Proxy

For better connection management:
- Consider using AWS RDS Proxy
- Handles SSL automatically
- Better connection pooling
- More secure

