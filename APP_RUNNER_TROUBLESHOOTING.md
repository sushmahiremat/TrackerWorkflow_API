# App Runner Service Creation Failed - Troubleshooting Guide

## Problem

The `tracker_service` App Runner service failed to create. The service is in `us-east-1` but trying to pull an ECR image from `us-west-2`.

## Common Issues and Solutions

### Issue 1: Cross-Region ECR Access

**Problem:** App Runner in `us-east-1` is trying to access ECR repository in `us-west-2`.

**Solutions:**

#### Option A: Move App Runner Service to Same Region (Recommended)

1. Delete the current App Runner service in `us-east-1`
2. Create a new App Runner service in `us-west-2` region
3. Use the same ECR image: `290008131176.dkr.ecr.us-west-2.amazonaws.com/tracker_api:latest`

#### Option B: Copy Image to us-east-1 ECR

1. Create ECR repository in `us-east-1`:
   ```bash
   aws ecr create-repository --repository-name tracker_api --region us-east-1
   ```
2. Pull image from `us-west-2`:
   ```bash
   docker pull 290008131176.dkr.ecr.us-west-2.amazonaws.com/tracker_api:latest
   ```
3. Tag for `us-east-1`:
   ```bash
   docker tag 290008131176.dkr.ecr.us-west-2.amazonaws.com/tracker_api:latest 290008131176.dkr.ecr.us-east-1.amazonaws.com/tracker_api:latest
   ```
4. Login to `us-east-1` ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 290008131176.dkr.ecr.us-east-1.amazonaws.com
   ```
5. Push to `us-east-1`:
   ```bash
   docker push 290008131176.dkr.ecr.us-east-1.amazonaws.com/tracker_api:latest
   ```
6. Update App Runner service to use: `290008131176.dkr.ecr.us-east-1.amazonaws.com/tracker_api:latest`

### Issue 2: Missing IAM Permissions

**Problem:** App Runner service role doesn't have permissions to access ECR.

**Solution:** Add ECR permissions to App Runner service role

1. Go to IAM Console → Roles
2. Find the App Runner service role (usually named like `AppRunnerServiceRole-...` or check in App Runner service configuration)
3. Add the following inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ecr:GetAuthorizationToken"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "arn:aws:ecr:us-west-2:290008131176:repository/tracker_api"
    }
  ]
}
```

### Issue 3: Image Doesn't Exist

**Problem:** The Docker image might not exist in ECR.

**Solution:** Verify the image exists

```bash
# Check if repository exists
aws ecr describe-repositories --repository-names tracker_api --region us-west-2

# List images in repository
aws ecr list-images --repository-name tracker_api --region us-west-2
```

If the image doesn't exist:

1. Make sure CodeBuild completed successfully
2. Check CodeBuild logs to verify the image was pushed
3. Retry the CodeBuild if needed

### Issue 4: ECR Repository Policy

**Problem:** ECR repository might have restrictive policies.

**Solution:** Check and update ECR repository policy

```bash
aws ecr get-repository-policy --repository-name tracker_api --region us-west-2
```

If needed, set a policy that allows App Runner to pull:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppRunnerPull",
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage"
      ]
    }
  ]
}
```

Apply it:

```bash
aws ecr set-repository-policy --repository-name tracker_api --policy-text file://policy.json --region us-west-2
```

## Quick Fix Steps (Recommended)

1. **Check App Runner Logs:**

   - Go to App Runner Console → `tracker_service` → "Logs" tab
   - Look for specific error messages

2. **Verify Image Exists:**

   ```bash
   aws ecr describe-images --repository-name tracker_api --region us-west-2
   ```

3. **Check Service Role Permissions:**

   - Go to App Runner service → Configuration tab
   - Note the service role name
   - Verify it has ECR permissions

4. **Best Solution - Use Same Region:**
   - Delete App Runner service in `us-east-1`
   - Create new service in `us-west-2` (same region as ECR)
   - This avoids cross-region issues entirely

## App Runner Configuration File (apprunner.yaml)

If you want to use a configuration file, create `apprunner.yaml` in your repository:

```yaml
version: 1.0
runtime: docker
build:
  commands:
    build:
      - echo "No build needed, using pre-built image"
run:
  runtime-version: latest
  command: uvicorn main:app --host 0.0.0.0 --port 8001
  network:
    port: 8001
  env:
    - name: DATABASE_URL
      value: "from-secrets-manager"
    - name: SECRET_KEY
      value: "from-secrets-manager"
```

## Environment Variables

Make sure to set environment variables in App Runner:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)
- `GOOGLE_CLIENT_ID` - Google OAuth client ID (if using)
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret (if using)

You can set these in:

- App Runner Console → Configuration → Environment variables
- Or use AWS Secrets Manager for sensitive values

## Next Steps

1. Check the App Runner logs for the specific error
2. Verify the Docker image exists in ECR
3. Ensure IAM permissions are correct
4. Consider moving App Runner to `us-west-2` to match ECR region
5. Retry service creation or rebuild
