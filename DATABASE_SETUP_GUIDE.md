# Database Setup Guide for App Runner

## Problem

App Runner runs in the cloud and cannot access a local database on your machine. You need a cloud-hosted database.

## Option 1: AWS RDS PostgreSQL (Recommended)

### Step 1: Create RDS PostgreSQL Database

1. **Go to AWS RDS Console:**

   - Navigate to: https://console.aws.amazon.com/rds/
   - Make sure you're in the same region as App Runner (us-east-1)

2. **Create Database:**

   - Click "Create database"
   - Choose "Standard create"
   - Engine: **PostgreSQL**
   - Version: Latest (e.g., PostgreSQL 15.x)
   - Template: **Free tier** (for testing) or **Production** (for production)

3. **Settings:**

   - **DB instance identifier:** `trackerworkflow-db`
   - **Master username:** `postgres` (or your preferred username)
   - **Master password:** Create a strong password (save this!)

4. **Instance configuration:**

   - **DB instance class:** `db.t3.micro` (free tier eligible) or larger for production
   - **Storage:** 20 GB (free tier) or more

5. **Connectivity:**

   - **VPC:** Default VPC (or your preferred VPC)
   - **Public access:** **Yes** (needed for App Runner to connect)
   - **VPC security group:** Create new or use existing
   - **Availability Zone:** No preference (or choose specific)

6. **Database authentication:**

   - **Password authentication**

7. **Additional configuration:**

   - **Initial database name:** `TrackerWorkflow`
   - **Backup retention:** 7 days (or your preference)
   - **Enable encryption:** Optional but recommended

8. **Click "Create database"**

### Step 2: Configure Security Group

1. **Wait for database to be available** (takes 5-10 minutes)

2. **Go to RDS Console → Databases → Your database**

3. **Click on the VPC security group** (under "Connectivity & security")

4. **Add inbound rule:**

   - **Type:** PostgreSQL
   - **Port:** 5432
   - **Source:**
     - For App Runner: `0.0.0.0/0` (allows App Runner to connect)
     - Or restrict to App Runner's IP range if known
   - **Description:** "Allow App Runner access"

5. **Save rules**

### Step 3: Get Database Endpoint

1. **In RDS Console → Your database**
2. **Copy the "Endpoint"** (e.g., `trackerworkflow-db.xxxxx.us-east-1.rds.amazonaws.com`)
3. **Note the port:** Usually `5432`

### Step 4: Update App Runner Environment Variables

1. **Go to App Runner Console → Your service → Configuration → Edit**

2. **Update DATABASE_URL:**

   ```
   DATABASE_URL=postgresql://postgres:your-password@trackerworkflow-db.xxxxx.us-east-1.rds.amazonaws.com:5432/TrackerWorkflow
   ```

   Replace:

   - `postgres` with your master username
   - `your-password` with your master password
   - `trackerworkflow-db.xxxxx.us-east-1.rds.amazonaws.com` with your endpoint

3. **Save and redeploy**

## Option 2: AWS RDS Serverless v2 (Auto-scaling)

For production workloads with variable traffic:

1. Follow Option 1 steps
2. Choose **Serverless v2** instead of provisioned
3. Set min/max capacity units
4. Database auto-scales based on demand

## Option 3: Other Cloud Databases

### Supabase (Free tier available)

- Go to: https://supabase.com
- Create project
- Get connection string
- Update `DATABASE_URL` in App Runner

### Railway PostgreSQL

- Go to: https://railway.app
- Create PostgreSQL database
- Get connection string
- Update `DATABASE_URL` in App Runner

### Neon (Serverless PostgreSQL)

- Go to: https://neon.tech
- Create project
- Get connection string
- Update `DATABASE_URL` in App Runner

### Render PostgreSQL

- Go to: https://render.com
- Create PostgreSQL database
- Get connection string
- Update `DATABASE_URL` in App Runner

## Option 4: Keep Local Database for Development

If you want to keep using local database for development:

1. **Use environment variables** to switch between local and cloud:

   ```python
   # In your code, use DATABASE_URL from environment
   # For local: DATABASE_URL=postgresql://postgres:123@localhost:5432/TrackerWorkflow
   # For App Runner: DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/TrackerWorkflow
   ```

2. **Local development:**

   - Run locally with local database
   - Use `.env` file with `localhost`

3. **Production (App Runner):**
   - Set `DATABASE_URL` in App Runner environment variables
   - Use cloud database (RDS or other)

## Quick RDS Setup (AWS CLI)

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier trackerworkflow-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YourStrongPassword123! \
  --allocated-storage 20 \
  --publicly-accessible \
  --region us-east-1

# Wait for database to be available (check status)
aws rds describe-db-instances \
  --db-instance-identifier trackerworkflow-db \
  --region us-east-1

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier trackerworkflow-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text \
  --region us-east-1
```

## Security Best Practices

1. **Use strong passwords** for database
2. **Enable encryption** at rest
3. **Restrict security group** to App Runner IPs if possible
4. **Use AWS Secrets Manager** for database credentials:

   ```bash
   aws secretsmanager create-secret \
     --name trackerworkflow/database-url \
     --secret-string "postgresql://user:pass@host:5432/db" \
     --region us-east-1
   ```

   Then reference in App Runner environment variables

5. **Regular backups** - RDS provides automatic backups

## Cost Considerations

- **RDS Free Tier:** 750 hours/month for 12 months (db.t3.micro)
- **After free tier:** ~$15-20/month for db.t3.micro
- **Serverless v2:** Pay per use, scales automatically
- **Other providers:** Many offer free tiers

## Testing the Connection

After setting up, test the connection:

1. **Update App Runner environment variable**
2. **Redeploy service**
3. **Check logs** - should see: `✅ Database tables created/verified successfully`
4. **Test API endpoint:** `https://your-app-runner-url/`

## Troubleshooting

### Connection Timeout

- Check security group allows inbound on port 5432
- Verify database is publicly accessible
- Check database endpoint is correct

### Authentication Failed

- Verify username and password
- Check database name matches

### Database Not Found

- Ensure initial database name is correct
- Or create database manually after RDS is ready
