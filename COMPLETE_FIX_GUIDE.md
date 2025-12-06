# Complete Fix Guide - App Runner Deployment Issues

## Current Issues

1. ❌ **Missing `email_validator` module** - Docker image needs rebuild
2. ❌ **DATABASE_URL showing localhost** - Environment variable not being read correctly

## Solution Steps

### Step 1: Verify Requirements.txt is Committed

Make sure `requirements.txt` includes `email-validator`:

```txt
email-validator==2.1.0
pydantic[email]==2.5.0
```

### Step 2: Rebuild Docker Image (CRITICAL)

The Docker image in ECR is old and doesn't have `email-validator`. You MUST rebuild it.

#### Option A: Trigger CodeBuild (Recommended)

1. **Go to CodeBuild Console:**

   - https://console.aws.amazon.com/codesuite/codebuild/projects
   - Select project: `TrackerAPI`
   - Click "Start build" button
   - Wait for build to complete (5-10 minutes)

2. **Verify Build Success:**
   - Check build logs
   - Should see: "Successfully pushed image to ECR"
   - Check ECR repository - new image should have recent timestamp

#### Option B: Build and Push Locally

If CodeBuild isn't working:

```bash
# 1. Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 290008131176.dkr.ecr.us-west-2.amazonaws.com

# 2. Build image (this will include email-validator)
docker build -t tracker_api .

# 3. Tag image
docker tag tracker_api:latest 290008131176.dkr.ecr.us-west-2.amazonaws.com/tracker_api:latest

# 4. Push to ECR
docker push 290008131176.dkr.ecr.us-west-2.amazonaws.com/tracker_api:latest
```

### Step 3: Verify Environment Variables in App Runner

1. **Go to App Runner Console:**

   - Service: `service_track`
   - Configuration tab
   - Verify `DATABASE_URL` is set correctly:
     ```
     postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
     ```

2. **Also Update GOOGLE_REDIRECT_URI:**
   - Change from: `http://localhost:8001/auth/google/callback`
   - To: `https://9uwp8ycrdq.us-east-1.awsapprunner.com/auth/google/callback`

### Step 4: Rebuild App Runner Service

After new Docker image is in ECR:

1. **Go to App Runner Console:**

   - Service: `service_track`
   - Click orange "Rebuild" button
   - Wait for rebuild to complete (3-5 minutes)

2. **Check Logs:**
   - Go to "Logs" tab
   - Should see: "✅ Using DATABASE_URL from environment"
   - Should NOT see: `ModuleNotFoundError: No module named 'email_validator'`
   - Should see: "✅ Database tables created/verified successfully"

### Step 5: Verify Success

1. **Check Application Logs:**

   - Should see RDS endpoint (not localhost)
   - Should see successful database connection
   - Should see application started on port 8001

2. **Test API:**
   - Go to: `https://9uwp8ycrdq.us-east-1.awsapprunner.com`
   - Should see: `{"message": "TrackerWorkflow API is running!"}`

## Why This Happens

### Issue 1: email_validator Missing

- **Root Cause:** Docker image was built before `email-validator` was added to `requirements.txt`
- **Solution:** Rebuild Docker image with updated `requirements.txt`
- **Prevention:** Always rebuild Docker image after updating `requirements.txt`

### Issue 2: DATABASE_URL Shows localhost

- **Root Cause:** Either:
  - Old Docker image doesn't have updated code that reads environment variables correctly
  - Environment variable wasn't set when the image was deployed
  - Logs are from an old deployment
- **Solution:**
  - Rebuild Docker image (includes updated code)
  - Verify environment variables are set correctly
  - Rebuild App Runner service

## Complete Environment Variables Checklist

Make sure ALL these are set in App Runner:

```
DATABASE_URL=postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
SECRET_KEY=jsdcuewyfd7q63r26gdweadhwvdiquohqdi73t76mnyt4132xzoikj
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_CLIENT_ID=129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://9uwp8ycrdq.us-east-1.awsapprunner.com/auth/google/callback
HUGGINGFACE_API_KEY=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
PYTHONUNBUFFERED=1
```

## Troubleshooting

### Still Getting email_validator Error?

- ✅ Verify CodeBuild completed successfully
- ✅ Check ECR - new image should have recent timestamp
- ✅ Verify `requirements.txt` includes `email-validator==2.1.0`
- ✅ Rebuild App Runner service after new image is in ECR

### Still Seeing localhost in Logs?

- ✅ Verify `DATABASE_URL` environment variable is set correctly
- ✅ Check logs are from the latest deployment (not cached)
- ✅ Rebuild App Runner service to pick up new image and environment variables

### Build Fails?

- Check CodeBuild logs for specific errors
- Verify IAM permissions for ECR
- Check Dockerfile is correct
- Verify all files are committed to repository

## Expected Timeline

1. **CodeBuild:** 5-10 minutes
2. **ECR Push:** Included in CodeBuild
3. **App Runner Rebuild:** 3-5 minutes
4. **Total:** ~10-15 minutes

## Success Indicators

After completing all steps, you should see in logs:

```
✅ Using DATABASE_URL from environment: postgresql://postgres:123@trackerworkflow-db...
🔗 Connecting to database: postgresql://postgres:123@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
✅ Database tables created/verified successfully
```

And the API should respond at: `https://9uwp8ycrdq.us-east-1.awsapprunner.com`
