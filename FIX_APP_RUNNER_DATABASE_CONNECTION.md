# Fix App Runner Database Connection Error

## Problem

You're getting these errors when trying to login:
1. **Password authentication failed** for user "postgres"
2. **No pg_hba.conf entry** for host "54.70.103.169" (App Runner's IP)

## Root Causes

1. **Wrong password in App Runner's DATABASE_URL** - The password in the environment variable doesn't match your RDS master password
2. **RDS Security Group** - Not allowing connections from App Runner's IP addresses

## Solution: Two-Step Fix

### Step 1: Fix RDS Security Group (Allow App Runner Access)

The error `no pg_hba.conf entry for host "54.70.103.169"` means RDS security group is blocking App Runner.

1. **Go to AWS RDS Console:**
   - https://console.aws.amazon.com/rds/
   - Region: `us-west-2`
   - Click on your database: `trackerworkflow-db`

2. **Go to Connectivity & Security tab:**
   - Find "VPC security groups"
   - Click on the security group name (e.g., `sg-xxxxx`)

3. **Edit Inbound Rules:**
   - Click "Edit inbound rules"
   - Click "Add rule"
   - **Type:** PostgreSQL
   - **Port:** 5432
   - **Source:** `0.0.0.0/0` (allows all IPs - for App Runner which has dynamic IPs)
     - OR restrict to App Runner's VPC if you know it
   - **Description:** "Allow App Runner access"
   - Click "Save rules"

4. **Verify Public Accessibility:**
   - In RDS Console → Your database → Connectivity & security
   - Make sure "Publicly accessible" is set to **Yes**
   - If not, you'll need to modify the database (takes 5-10 minutes)

### Step 2: Update DATABASE_URL in App Runner (Correct Password)

The password in App Runner's environment variable is wrong. You need to set the correct RDS master password.

#### Option A: If You Know the Correct Password

1. **Go to App Runner Console:**
   - https://console.aws.amazon.com/apprunner
   - Region: `us-west-2`
   - Click on your service: `service_track_one` or `9cqn6rispm` (check your service name)

2. **Go to Configuration:**
   - Click "Configuration" tab
   - Click "Edit" button

3. **Update DATABASE_URL:**
   - Scroll to "Environment variables"
   - Find `DATABASE_URL` (or add it if missing)
   - **Name:** `DATABASE_URL`
   - **Value:** 
     ```
     postgresql://postgres:YOUR_CORRECT_PASSWORD@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
     ```
   - Replace `YOUR_CORRECT_PASSWORD` with your actual RDS master password
   - **Important:** URL-encode special characters in password:
     - `|` becomes `%7C`
     - `!` becomes `%21`
     - `@` becomes `%40`
     - `#` becomes `%23`
     - `$` becomes `%24`
     - `%` becomes `%25`
     - `&` becomes `%26`
     - `*` becomes `%2A`
     - `(` becomes `%28`
     - `)` becomes `%29`
     - `+` becomes `%2B`
     - `,` becomes `%2C`
     - `/` becomes `%2F`
     - `:` becomes `%3A`
     - `;` becomes `%3B`
     - `=` becomes `%3D`
     - `?` becomes `%3F`
     - `[` becomes `%5B`
     - `]` becomes `%5D`

4. **Example with URL-encoded password:**
   If your password is `w1p.z|qj9VV!b|OiPaaRn|4W.P69`, the URL-encoded version is:
   ```
   w1p.z%7Cqj9VV%21b%7COiPaaRn%7C4W.P69
   ```
   
   So the full DATABASE_URL would be:
   ```
   postgresql://postgres:w1p.z%7Cqj9VV%21b%7COiPaaRn%7C4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
   ```

5. **Save and Deploy:**
   - Click "Save changes"
   - App Runner will automatically redeploy (takes 5-10 minutes)

#### Option B: If You Don't Know the Password (Reset It)

1. **Reset RDS Master Password:**
   - Go to RDS Console → Your database
   - Click "Modify" button
   - Scroll to "Database authentication"
   - Click "Change master password"
   - Enter new password (remember it!)
   - Confirm new password
   - Choose "Apply immediately"
   - Click "Continue" → "Modify DB instance"
   - Wait 5-10 minutes for modification to complete

2. **Update App Runner with New Password:**
   - Follow Option A steps above
   - Use the new password you just set
   - Remember to URL-encode special characters

### Step 3: Verify Other Required Environment Variables

While you're in App Runner Configuration, make sure these are also set:

- `SECRET_KEY` = `uygduweydwudywugcgmjkiuytcxzszdsiutuytytrthfd` (or your own)
- `ALGORITHM` = `HS256` (optional, defaults to this)
- `ACCESS_TOKEN_EXPIRE_MINUTES` = `30` (optional, defaults to this)
- `GOOGLE_CLIENT_ID` = `129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com`
- `GOOGLE_CLIENT_SECRET` = `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`
- `GOOGLE_REDIRECT_URI` = `https://9cqn6rispm.us-west-2.awsapprunner.com/auth/google/callback`

## Quick URL Encoding Helper

If your password has special characters, use this Python command to encode it:

```python
from urllib.parse import quote_plus
password = "w1p.z|qj9VV!b|OiPaaRn|4W.P69"
encoded = quote_plus(password)
print(encoded)  # Output: w1p.z%7Cqj9VV%21b%7COiPaaRn%7C4W.P69
```

Or use an online tool: https://www.urlencoder.org/

## Verify the Fix

After updating:

1. **Wait for App Runner to redeploy** (5-10 minutes)
2. **Check App Runner Logs:**
   - Go to App Runner → Your service → Logs
   - Look for: `✅ Using DATABASE_URL from environment`
   - Look for: `✅ Database tables created/verified successfully`
   - Should NOT see connection errors

3. **Test Login:**
   - Try logging in from your frontend
   - Should work without database errors

## Troubleshooting

### Still Getting Password Error?

1. **Double-check the password:**
   - Make sure you're using the RDS master password (not a user password)
   - Verify password in RDS Console → Configuration → Database credentials
   - Try resetting the password again

2. **Check URL encoding:**
   - Special characters MUST be URL-encoded
   - Test the connection string locally first

3. **Verify DATABASE_URL format:**
   ```
   postgresql://[username]:[password]@[endpoint]:[port]/[database]
   ```
   - No spaces
   - All special characters in password are encoded
   - Endpoint is correct

### Still Getting pg_hba.conf Error?

1. **Check Security Group:**
   - Make sure inbound rule for port 5432 exists
   - Source should be `0.0.0.0/0` or App Runner's VPC

2. **Check Public Accessibility:**
   - RDS must be publicly accessible for App Runner
   - Go to RDS → Modify → Network & Security → Publicly accessible = Yes

3. **Check Network ACLs:**
   - VPC Network ACLs might be blocking
   - Check VPC Console → Network ACLs

## Summary Checklist

- [ ] RDS Security Group allows inbound on port 5432 from `0.0.0.0/0`
- [ ] RDS is publicly accessible
- [ ] DATABASE_URL in App Runner has correct password
- [ ] Password special characters are URL-encoded
- [ ] All other environment variables are set
- [ ] App Runner redeployed successfully
- [ ] Logs show successful database connection
- [ ] Login works from frontend

## Need Help?

If still having issues:
1. Check App Runner logs for specific error messages
2. Check RDS logs for connection attempts
3. Verify you can connect to RDS from pgAdmin (proves credentials work)
4. Test DATABASE_URL locally with Python before setting in App Runner

