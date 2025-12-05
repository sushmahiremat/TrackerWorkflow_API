# How to Rebuild Docker Image with Updated Requirements

## Problem

The Docker image in ECR doesn't have `email-validator` because it was built before the dependency was added to `requirements.txt`.

## Solution: Rebuild and Push New Docker Image

### Step 1: Commit and Push Updated Code

1. **Make sure all changes are committed:**
   ```bash
   git add requirements.txt
   git commit -m "Add email-validator dependency"
   git push
   ```

### Step 2: Trigger CodeBuild Build

You have two options:

#### Option A: Automatic (if connected to GitHub)

- If CodeBuild is connected to your GitHub repository
- Pushing to the repository will automatically trigger a new build
- Go to CodeBuild Console and wait for the build to complete

#### Option B: Manual Trigger

1. **Go to AWS CodeBuild Console:**
   - Navigate to: https://console.aws.amazon.com/codesuite/codebuild/projects
   - Select your project: `TrackerAPI`
   - Click "Start build" button
   - Wait for build to complete (5-10 minutes)

### Step 3: Verify New Image in ECR

1. **Go to ECR Console:**

   - Navigate to: https://console.aws.amazon.com/ecr/repositories
   - Select repository: `tracker_api`
   - Check the "Last updated" timestamp
   - Should show recent time after CodeBuild completes

2. **Verify Image Tag:**
   - The new image should be tagged as `latest`
   - Check the image digest to confirm it's different from the old one

### Step 4: Update App Runner Service

After the new image is pushed to ECR:

#### Option A: Automatic (if using latest tag)

- App Runner should automatically detect the new `latest` image
- It will redeploy automatically
- Check the service logs to verify

#### Option B: Manual Rebuild

1. **Go to App Runner Console:**
   - Service: `service_track`
   - Click "Rebuild" button (orange button)
   - This will pull the new image from ECR
   - Wait for rebuild to complete

### Step 5: Verify Application Starts

1. **Check App Runner Logs:**

   - Go to "Logs" tab
   - Look for successful startup messages
   - Should NOT see `ModuleNotFoundError: No module named 'email_validator'`

2. **Test the API:**
   - Go to your App Runner URL: `https://9uwp8ycrdq.us-east-1.awsapprunner.com`
   - Should see: `{"message": "TrackerWorkflow API is running!"}`

## Quick Checklist

- [ ] `requirements.txt` includes `email-validator==2.1.0` ✅ (Already done)
- [ ] Code committed and pushed to repository
- [ ] CodeBuild build triggered and completed successfully
- [ ] New Docker image pushed to ECR with `latest` tag
- [ ] App Runner service rebuilt or auto-redeployed
- [ ] Application starts without `email_validator` error
- [ ] DATABASE_URL environment variable updated to RDS endpoint (not localhost)

## Troubleshooting

### CodeBuild Fails

- Check CodeBuild logs for errors
- Verify IAM permissions for ECR access
- Check if Dockerfile is correct

### App Runner Still Using Old Image

- Force rebuild: Click "Rebuild" button
- Check ECR to verify new image exists
- Verify image tag is `latest`

### Still Getting email_validator Error

- Check if new image was actually built
- Verify requirements.txt is in the Docker image
- Check Dockerfile copies requirements.txt correctly

## Expected Timeline

1. **CodeBuild:** 5-10 minutes
2. **ECR Push:** Included in CodeBuild
3. **App Runner Rebuild:** 3-5 minutes
4. **Total:** ~10-15 minutes

## Alternative: Build Locally and Push

If CodeBuild is not working, you can build and push locally:

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 290008131176.dkr.ecr.us-west-2.amazonaws.com

# Build image
docker build -t tracker_api .

# Tag image
docker tag tracker_api:latest 290008131176.dkr.ecr.us-west-2.amazonaws.com/tracker_api:latest

# Push to ECR
docker push 290008131176.dkr.ecr.us-west-2.amazonaws.com/tracker_api:latest
```

Then rebuild App Runner service.
