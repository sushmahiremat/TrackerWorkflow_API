# Config File Issues and Fixes

## Issues Found

### ❌ Issue 1: Database URL Hardcoded
- **Problem:** `database_url` is hardcoded to RDS, but `database.py` prioritizes `DATABASE_URL` environment variable
- **Result:** If `DATABASE_URL` env var is not set, it falls back to localhost (from individual settings)
- **Fix:** Changed to `Optional[str] = None` so it reads from environment variable first

### ❌ Issue 2: Google OAuth Credentials Empty
- **Problem:** `google_client_id` and `google_client_secret` are empty strings
- **Result:** Google OAuth will fail with 500 errors
- **Fix:** Added default `google_client_id` (you still need to set `google_client_secret`)

### ❌ Issue 3: Missing Google Redirect URI
- **Problem:** No `google_redirect_uri` setting
- **Result:** Google OAuth might not work correctly
- **Fix:** Added `google_redirect_uri` with your App Runner backend URL

## What You Need to Do

### For Local Development (.env file):

Create/update `.env` file in `TrackerWorkflow_API/`:

```env
# Database - Use RDS for production-like testing
DATABASE_URL=postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow

# Or use individual settings:
# DB_HOST=trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com
# DB_PORT=5432
# DB_NAME=TrackerWorkflow
# DB_USER=postgres
# DB_PASSWORD=123

# JWT
SECRET_KEY=uygduweydwudywugcgmjkiuytcxzszdsiutuytytrthfd
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth (REQUIRED)
GOOGLE_CLIENT_ID=129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8001/auth/google/callback
```

**Important:** Get `GOOGLE_CLIENT_SECRET` from:
1. Google Cloud Console: https://console.cloud.google.com/
2. APIs & Services → Credentials
3. Click on your OAuth 2.0 Client ID
4. Copy the "Client secret"

### For App Runner (Environment Variables):

Go to App Runner → `service_track_one` → Configuration → Edit → Environment variables:

```
DATABASE_URL=postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
SECRET_KEY=uygduweydwudywugcgmjkiuytcxzszdsiutuytytrthfd
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_CLIENT_ID=129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=https://9uwp8ycrdq.us-east-1.awsapprunner.com/auth/google/callback
```

## Why Your Terminal Shows Localhost

Your terminal shows:
```
⚠️  DATABASE_URL not found in environment, using fallback
🔗 Connecting to database: postgresql://postgres:123@localhost:5432/Trackerworkflow
```

This means:
1. Your `.env` file doesn't have `DATABASE_URL` set
2. Or the `.env` file isn't being loaded
3. So it's using the fallback (localhost from individual settings)

**Solution:** Create/update `.env` file with `DATABASE_URL` pointing to RDS.

## Quick Fix Checklist

- [ ] Updated `config.py` (already done)
- [ ] Created/updated `.env` file with `DATABASE_URL` pointing to RDS
- [ ] Added `GOOGLE_CLIENT_SECRET` to `.env` (get from Google Cloud Console)
- [ ] Set all environment variables in App Runner backend service
- [ ] Restarted local backend to load new `.env` values
- [ ] Rebuilt App Runner backend service (if you changed code)

## Expected Result

After fixing:
- ✅ Local backend connects to RDS (not localhost)
- ✅ Google OAuth works (no 500 errors)
- ✅ Backend logs show correct database connection
- ✅ All API endpoints work

