# Fix CodeBuild ECR Permissions Issue

## Problem
The CodeBuild service role `codebuild-TrackerAPI-service-role` doesn't have permissions to access Amazon ECR.

## Solution: Add ECR Permissions to CodeBuild Service Role

### Option 1: Using AWS Console (Recommended)

1. **Go to IAM Console:**
   - Navigate to: https://console.aws.amazon.com/iam/
   - Click on "Roles" in the left sidebar

2. **Find the CodeBuild Service Role:**
   - Search for: `codebuild-TrackerAPI-service-role`
   - Click on the role name

3. **Add ECR Permissions:**
   - Click on "Add permissions" → "Create inline policy"
   - Click on "JSON" tab
   - Paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "arn:aws:ecr:us-west-2:290008131176:repository/tracker_api"
        }
    ]
}
```

4. **Review and Create:**
   - Name the policy: `CodeBuild-ECR-Permissions`
   - Click "Create policy"

### Option 2: Using AWS CLI

Run the following command to attach the policy:

```bash
aws iam put-role-policy \
    --role-name codebuild-TrackerAPI-service-role \
    --policy-name CodeBuild-ECR-Permissions \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:PutImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload"
                ],
                "Resource": "arn:aws:ecr:us-west-2:290008131176:repository/tracker_api"
            }
        ]
    }'
```

### Option 3: Update CodeBuild Project Settings

Alternatively, you can update the CodeBuild project to use a different service role that already has ECR permissions:

1. Go to CodeBuild Console
2. Select your project: `TrackerAPI`
3. Click "Edit" → "Environment"
4. Under "Service role", either:
   - Select an existing role with ECR permissions, OR
   - Create a new role with the permissions above

## Verify the Fix

After adding the permissions:

1. Go back to CodeBuild
2. Click "Retry build" on the failed build
3. The build should now be able to authenticate with ECR

## Required Permissions Summary

The CodeBuild service role needs:
- `ecr:GetAuthorizationToken` - To get login token (required for all ECR operations)
- `ecr:BatchCheckLayerAvailability` - To check if image layers exist
- `ecr:GetDownloadUrlForLayer` - To download image layers
- `ecr:BatchGetImage` - To pull images
- `ecr:PutImage` - To push images
- `ecr:InitiateLayerUpload` - To start uploading layers
- `ecr:UploadLayerPart` - To upload layer parts
- `ecr:CompleteLayerUpload` - To complete layer upload

## Notes

- Make sure the ECR repository `tracker_api` exists in `us-west-2` region
- If the repository doesn't exist, create it first:
  ```bash
  aws ecr create-repository --repository-name tracker_api --region us-west-2
  ```

