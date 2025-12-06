# Get RDS Password from AWS Secrets Manager

## Your Situation

You didn't set a password when creating the RDS database because AWS Secrets Manager was used. AWS auto-generated the password and stored it in Secrets Manager.

## How to Get the Password

### Step 1: Open Secrets Manager

1. **Go to AWS Secrets Manager Console:**
   - https://console.aws.amazon.com/secretsmanager/
   - Region: `us-west-2`

2. **Find Your Secret:**
   - Look for secret: `rds!db-6e53009e-d134-4515-878f-f1e7eb1aebda`
   - Or search for: `trackerworkflow-db`
   - Click on the secret

### Step 2: Retrieve the Secret Value

1. **On the Secret Details Page:**
   - You should see a section "Secret value"
   - Click the button: **"Retrieve secret value"**

2. **View the Password:**
   - The secret value will be displayed in JSON format
   - It will look like this:
     ```json
     {
       "username": "postgres",
       "password": "AUTO_GENERATED_PASSWORD_HERE",
       "engine": "postgres",
       "host": "trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com",
       "port": 5432,
       "dbname": "TrackerWorkflow"
     }
     ```

3. **Copy the Password:**
   - Copy the value from the `"password"` field
   - This is your database password!

### Step 3: Use the Password

#### For Local Development (.env file):

Update `TrackerWorkflow_API/.env`:

```env
DATABASE_URL=postgresql://postgres:PASTE_PASSWORD_HERE@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

#### For App Runner:

1. **Go to App Runner Console:**
   - Service: `service_track_one`
   - Configuration → Edit → Environment variables

2. **Update DATABASE_URL:**
   ```
   DATABASE_URL=postgresql://postgres:PASTE_PASSWORD_HERE@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
   ```

## Alternative: Use Secrets Manager Directly in App Runner

Instead of copying the password, you can reference the secret directly:

1. **In App Runner Environment Variables:**
   - Instead of setting `DATABASE_URL` directly
   - Use the secret ARN: `arn:aws:secretsmanager:us-west-2:290008131176:secret:rds!db-6e53009e-d134-4515-878f-f1e7eb1aebda-DdgJtL`

2. **Your application code needs to:**
   - Read from Secrets Manager
   - Parse the JSON
   - Build the connection string

## Quick Steps Summary

1. ✅ Go to Secrets Manager
2. ✅ Click on secret: `rds!db-6e53009e-d134-4515-878f-f1e7eb1aebda`
3. ✅ Click "Retrieve secret value"
4. ✅ Copy the `password` value from JSON
5. ✅ Use it in your `.env` file and App Runner

## Security Note

- The password is auto-generated and secure
- It's stored encrypted in Secrets Manager
- You can rotate it from Secrets Manager if needed
- Don't share or commit this password to version control

