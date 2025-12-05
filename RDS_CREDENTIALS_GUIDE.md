# How to Find RDS Database Username and Password

## Username

The username is set when you create the RDS database and cannot be changed later. Here's where to find it:

### Method 1: RDS Console

1. **Go to AWS RDS Console:**

   - Navigate to: https://console.aws.amazon.com/rds/
   - Make sure you're in the correct region (us-west-2)

2. **Select Your Database:**

   - Click on "Databases" in the left sidebar
   - Click on your database: `trackerworkflow-db`

3. **Find Username:**
   - Look in the "Configuration" tab
   - Under "Database credentials" section
   - You'll see "Master username" - this is your username
   - Common default: `postgres` (for PostgreSQL)

### Method 2: Database Details

- The username is displayed in the database summary
- It's the "Master username" you set during database creation

## Password

⚠️ **Important:** AWS does NOT store your password for security reasons. You set it during database creation, and AWS doesn't save it.

### If You Remember the Password:

- Use the password you set when creating the database
- This is the password you entered in the "Master password" field

### If You Forgot the Password:

You have two options:

#### Option 1: Reset the Password (Recommended)

1. **Go to RDS Console:**

   - Select your database: `trackerworkflow-db`
   - Click "Modify" button (top right)

2. **Modify Database:**

   - Scroll down to "Database authentication"
   - Find "Master password" section
   - Click "Change master password"
   - Enter new password
   - Confirm new password

3. **Apply Changes:**

   - Choose "Apply immediately" or schedule for maintenance window
   - Click "Continue"
   - Review and click "Modify DB instance"

4. **Wait for Modification:**

   - Database will restart with new password
   - Takes 5-10 minutes

5. **Update App Runner:**
   - Go to App Runner → Configuration → Environment variables
   - Update `DATABASE_URL` with new password:
     ```
     postgresql://postgres:NEW_PASSWORD@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
     ```

#### Option 2: Check Your Notes/Password Manager

- Check where you saved the password when creating the database
- Check AWS Secrets Manager (if you stored it there)
- Check your password manager

## Complete Connection String Format

Once you have both username and password:

```
postgresql://[USERNAME]:[PASSWORD]@[ENDPOINT]:[PORT]/[DATABASE_NAME]
```

### Example:

```
postgresql://postgres:MyPassword123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
```

## Where to Find All Connection Details

### In RDS Console → Your Database:

1. **Username:**

   - Configuration tab → "Database credentials" → "Master username"

2. **Endpoint:**

   - Connectivity & security tab → "Endpoint & port" → "Endpoint"

3. **Port:**

   - Connectivity & security tab → "Endpoint & port" → "Port" (usually 5432 for PostgreSQL)

4. **Database Name:**

   - Configuration tab → "Database options" → "DB name"
   - Or the name you set during creation (e.g., `TrackerWorkflow`)

5. **Password:**
   - Not stored by AWS - you need to remember or reset it

## Quick Checklist

To create your DATABASE_URL, you need:

- [ ] Username (found in RDS Console → Configuration)
- [ ] Password (remembered or reset)
- [ ] Endpoint (found in RDS Console → Connectivity & security)
- [ ] Port (usually 5432 for PostgreSQL)
- [ ] Database name (set during creation)

## Security Best Practice

For production, consider using AWS Secrets Manager:

1. **Store credentials in Secrets Manager:**

   ```bash
   aws secretsmanager create-secret \
     --name trackerworkflow/database-credentials \
     --secret-string '{"username":"postgres","password":"YourPassword","endpoint":"trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com","port":5432,"database":"TrackerWorkflow"}' \
     --region us-west-2
   ```

2. **Reference in App Runner:**
   - Use secret ARN in environment variables
   - Or use AWS Systems Manager Parameter Store

## Troubleshooting

### Can't Connect to Database?

1. Check username is correct (usually `postgres`)
2. Verify password is correct (reset if needed)
3. Check security group allows inbound on port 5432
4. Verify database is publicly accessible
5. Check endpoint is correct

### Password Reset Not Working?

- Wait for database modification to complete
- Check database status is "Available"
- Verify new password meets requirements (usually 8+ characters)
