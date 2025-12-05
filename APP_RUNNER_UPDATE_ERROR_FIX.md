# App Runner Update Error - Troubleshooting Guide

## Error: "Failed to update service_track_one"

This error can occur for several reasons. Here are the most common causes and solutions:

## Solution 1: Service State Issue

The service might be in a state that doesn't allow updates.

### Steps:

1. **Check Service Status:**

   - Go to App Runner Console → `service_track_one`
   - Check if status is "Create failed" or "Update failed"
   - If so, you may need to rebuild instead of update

2. **Try Rebuild Instead:**
   - Click "Rebuild" button (orange button at top)
   - This will recreate the service with current configuration
   - Wait for rebuild to complete

## Solution 2: Web ACL Error

The Web ACL error might be blocking the update.

### Steps:

1. **Ignore Web ACL Error (if not using WAF):**

   - The Web ACL error is often a warning, not a blocker
   - If you're not using AWS WAF, you can ignore it
   - Try the update again

2. **If Using WAF:**
   - Go to AWS WAF Console
   - Check if Web ACL exists for App Runner
   - Verify IAM permissions for App Runner to access WAF

## Solution 3: Environment Variable Validation

Some environment variables might have invalid values.

### Check These:

1. **DATABASE_URL Format:**

   ```
   ✅ Correct: postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
   ❌ Wrong: postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow (extra spaces)
   ```

2. **Special Characters in Passwords:**

   - If your database password has special characters, URL-encode them:
   - `@` becomes `%40`
   - `#` becomes `%23`
   - `%` becomes `%25`
   - `&` becomes `%26`
   - `=` becomes `%3D`
   - `+` becomes `%2B`
   - `?` becomes `%3F`

3. **GOOGLE_REDIRECT_URI:**
   - Your current value: `http://localhost:8001/auth/google/callback`
   - This should be your App Runner URL for production:
   - `https://9cqn6rispm.us-west-2.awsapprunner.com/auth/google/callback`
   - Or keep localhost if only for development

## Solution 4: Delete and Recreate Service

If updates keep failing, delete and recreate:

### Steps:

1. **Delete Current Service:**

   - Go to App Runner Console → `service_track_one`
   - Click "Actions" → "Delete service"
   - Confirm deletion

2. **Create New Service:**
   - Click "Create service"
   - Use same configuration
   - Set all environment variables correctly
   - Create service

## Solution 5: Check CloudWatch Logs

Check detailed error messages:

1. **Go to CloudWatch:**
   - App Runner Console → Logs → "View in CloudWatch"
   - Look for specific error messages
   - Check for validation errors

## Solution 6: Update Configuration Step by Step

Instead of updating all at once, try updating one variable at a time:

1. **Update DATABASE_URL first:**

   - Save and wait for deployment
   - If successful, continue with next variable

2. **Then update other variables:**
   - Update one at a time
   - This helps identify which variable causes the issue

## Quick Fix Checklist

- [ ] Service status allows updates (not in failed state)
- [ ] DATABASE_URL is correctly formatted (no extra spaces)
- [ ] Database password is URL-encoded if it has special characters
- [ ] All required environment variables are set
- [ ] GOOGLE_REDIRECT_URI points to correct URL
- [ ] Try "Rebuild" instead of "Update"
- [ ] Check CloudWatch logs for specific errors

## Recommended Environment Variables

Here's a clean set of environment variables to use:

```
DATABASE_URL=postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
SECRET_KEY=jsdcuewyfd7q63r26gdweadhwvdiquohqdi73t76mnyt4132xzoikj
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_CLIENT_ID=129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://9cqn6rispm.us-west-2.awsapprunner.com/auth/google/callback
HUGGINGFACE_API_KEY=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
PYTHONUNBUFFERED=1
```

## Next Steps

1. **Try Rebuild First:**

   - Click "Rebuild" button
   - This often resolves update issues

2. **If Rebuild Fails:**

   - Check CloudWatch logs for specific error
   - Verify DATABASE_URL format
   - Ensure database is accessible from App Runner

3. **If Still Failing:**
   - Delete service and recreate
   - Set environment variables during creation
   - This avoids update state issues
