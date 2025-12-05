# App Runner Environment Variables Setup

## Problem

The App Runner service is failing to start because required environment variables are not set. The application needs database connection and authentication configuration.

## Required Environment Variables

Set these in App Runner Console → Configuration → Environment variables:

### Database Configuration

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

Or use individual settings:

```
DB_HOST=your-db-host.rds.amazonaws.com
DB_PORT=5432
DB_NAME=TrackerWorkflow
DB_USER=postgres
DB_PASSWORD=your-password
```

### JWT Configuration

```
SECRET_KEY=your-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Google OAuth (Optional)

```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## How to Set Environment Variables in App Runner

1. **Go to App Runner Console:**

   - Navigate to your service: `service_tracker`
   - Click on the "Configuration" tab

2. **Edit Configuration:**

   - Click "Edit" button
   - Scroll down to "Environment variables" section
   - Click "Add environment variable" for each variable

3. **Add Variables:**

   - Enter the variable name (e.g., `DATABASE_URL`)
   - Enter the value
   - Click "Add" or "Save"

4. **Save and Deploy:**
   - Click "Save changes"
   - App Runner will automatically redeploy with new environment variables

## Using AWS Secrets Manager (Recommended for Production)

For sensitive values like passwords and secrets:

1. **Store secrets in Secrets Manager:**

   ```bash
   # Store database URL
   aws secretsmanager create-secret \
     --name trackerworkflow/database-url \
     --secret-string "postgresql://user:pass@host:5432/db" \
     --region us-east-1

   # Store JWT secret
   aws secretsmanager create-secret \
     --name trackerworkflow/jwt-secret \
     --secret-string "your-secret-key" \
     --region us-east-1
   ```

2. **Reference in App Runner:**
   - In App Runner Configuration → Environment variables
   - Use format: `arn:aws:secretsmanager:region:account:secret:secret-name:key::`
   - Or use the secret ARN directly

## Quick Setup Steps

1. **Get your database connection string:**

   - If using RDS: `postgresql://username:password@your-rds-endpoint:5432/database`
   - If using external database: Use your provider's connection string

2. **Set minimum required variables:**

   ```
   DATABASE_URL=postgresql://postgres:password@your-db-host:5432/TrackerWorkflow
   SECRET_KEY=your-very-long-random-secret-key-minimum-32-characters
   ```

3. **Test the connection:**
   - After setting variables, App Runner will redeploy
   - Check the logs to verify the application starts successfully
   - The application should connect to the database and start on port 8001

## Troubleshooting

### Application Still Fails to Start

1. **Check CloudWatch Logs:**

   - Go to App Runner → Logs → "View in CloudWatch"
   - Look for error messages about:
     - Database connection failures
     - Missing environment variables
     - Import errors

2. **Verify Database Access:**

   - Ensure your database is accessible from App Runner
   - Check security groups and network ACLs
   - Verify database credentials are correct

3. **Check Environment Variables:**
   - Verify all required variables are set
   - Check for typos in variable names
   - Ensure values don't have extra spaces

### Common Errors

**Error: "Container exit code: 1"**

- Usually means application crashed on startup
- Check CloudWatch logs for specific error
- Most common: Database connection failure or missing environment variable

**Error: "Database connection timeout"**

- Database might not be accessible from App Runner
- Check security groups
- Verify database endpoint is correct

**Error: "Module not found"**

- Missing dependency in requirements.txt
- Check Dockerfile includes all dependencies

## Example Configuration

Here's a complete example of environment variables:

```
DATABASE_URL=postgresql://postgres:mypassword@mydb.123456789.us-east-1.rds.amazonaws.com:5432/TrackerWorkflow
SECRET_KEY=my-very-long-secret-key-that-is-at-least-32-characters-long-for-security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
PYTHONUNBUFFERED=1
```

## Next Steps

1. Set the environment variables in App Runner
2. Save and wait for redeployment
3. Check the logs to verify successful startup
4. Test the API endpoint: `https://your-app-runner-url/`
