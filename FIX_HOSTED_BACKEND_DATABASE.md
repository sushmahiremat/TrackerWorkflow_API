# Fix Hosted Backend Database Connection

## Problem

- ✅ Database `TrackerWorkflow` exists in RDS
- ✅ Tables exist (you can see them in pgAdmin)
- ❌ Login fails on hosted frontend ("Failed to fetch")
- ❌ Backend App Runner is not connecting to RDS

## Root Cause

The backend App Runner service doesn't have the `DATABASE_URL` environment variable set, so it's trying to connect to localhost instead of RDS.

## Solution: Set DATABASE_URL in App Runner

### Step 1: Get Your Database Connection String

From what we know:

- **Endpoint:** `trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com`
- **Port:** `5432`
- **Database:** `TrackerWorkflow`
- **Username:** `postgres`
- **Password:** `w1p.z|qj9W!b|OiPaaRn|4W.P69` (from Secrets Manager)

**Complete DATABASE_URL:**

```
postgresql://postgres:w1p.z|qj9W!b|OiPaaRn|4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

### Step 2: Set Environment Variable in App Runner Backend

1. **Go to App Runner Console:**

   - https://console.aws.amazon.com/apprunner
   - Service: `service_track_one` (your backend service)
   - Click on the service

2. **Go to Configuration:**

   - Click "Configuration" tab
   - Click "Edit" button

3. **Add/Update Environment Variables:**

   - Scroll down to "Environment variables" section
   - Click "Add environment variable" (if DATABASE_URL doesn't exist)
   - Or click "Edit" next to existing DATABASE_URL

4. **Set DATABASE_URL:**

   - **Name:** `DATABASE_URL`
   - **Value:** `postgresql://postgres:w1p.z|qj9W!b|OiPaaRn|4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow`
   - **Type:** Plaintext

5. **Also Verify These Variables Are Set:**

   - `SECRET_KEY` = `uygduweydwudywugcgmjkiuytcxzszdsiutuytytrthfd`
   - `GOOGLE_CLIENT_ID` = `129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com`
   - `GOOGLE_CLIENT_SECRET` = `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`
   - `GOOGLE_REDIRECT_URI` = `https://9uwp8ycrdq.us-east-1.awsapprunner.com/auth/google/callback`

6. **Save Changes:**
   - Click "Save changes" at the bottom
   - App Runner will automatically redeploy with new environment variables
   - Wait 3-5 minutes for deployment

### Step 3: Verify Backend Connection

1. **Check Backend Logs:**

   - App Runner → `service_track_one` → "Logs" tab
   - Look for:
     - `✅ Using DATABASE_URL from environment: postgresql://postgres:...`
     - `🔗 Connecting to database: postgresql://postgres:...@trackerworkflow-db...`
     - `✅ Database tables created/verified successfully`

2. **Test Backend API:**
   - Open: `https://9uwp8ycrdq.us-east-1.awsapprunner.com/docs`
   - Try the `/login` endpoint
   - Should work now

### Step 4: Test Frontend Login

1. **Clear Browser Cache:**

   - Press `Ctrl+Shift+Delete`
   - Clear cached files
   - Or use Incognito mode

2. **Open Frontend:**
   - `https://y55dfkjshm.us-west-2.awsapprunner.com/login`
   - Try logging in
   - Should work now!

## Why This Happens

1. **Local vs Hosted:**

   - Local backend reads from `.env` file
   - Hosted backend (App Runner) reads from environment variables
   - They are separate configurations

2. **Environment Variables Not Set:**
   - App Runner doesn't automatically read `.env` files
   - You must set environment variables in App Runner console
   - Without `DATABASE_URL`, backend tries to connect to localhost (which doesn't exist in App Runner)

## Quick Checklist

- [ ] Set `DATABASE_URL` in App Runner backend service
- [ ] Verified all other environment variables are set
- [ ] Saved changes and waited for deployment
- [ ] Checked backend logs for successful database connection
- [ ] Tested backend API at `/docs`
- [ ] Tested frontend login

## Expected Result

After setting `DATABASE_URL` in App Runner:

- ✅ Backend connects to RDS database
- ✅ Backend logs show successful connection
- ✅ Login works on hosted frontend
- ✅ All API endpoints work
- ✅ Google OAuth works

## Troubleshooting

### If Still Not Working:

1. **Check Backend Logs:**

   - Look for database connection errors
   - Check if `DATABASE_URL` is being read

2. **Verify RDS Security Group:**

   - RDS security group must allow inbound on port 5432
   - Source should be App Runner's IP range or `0.0.0.0/0`

3. **Check RDS Status:**

   - RDS must be "Available"
   - Check RDS console for any issues

4. **Verify Password:**
   - Make sure password is correct (from Secrets Manager)
   - Special characters in password might need URL encoding

## Password URL Encoding

If password has special characters, you might need to URL-encode them:

- `|` becomes `%7C`
- `!` becomes `%21`
- etc.

But try the password as-is first - PostgreSQL connection strings usually handle special characters correctly.
