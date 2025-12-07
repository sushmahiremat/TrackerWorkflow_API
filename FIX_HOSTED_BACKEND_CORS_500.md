# 🔧 Fix Hosted Backend CORS & 500 Errors

## 🎯 Problem Summary

You're getting two errors when trying to login to the hosted backend:

1. **CORS Error**: `Access-Control-Allow-Origin header is missing`
2. **500 Internal Server Error**: Backend is crashing

## ✅ Solution Steps

### Step 1: Update Backend Code (Already Done)

I've updated `main.py` to:

- ✅ Fix CORS wildcard support using `allow_origin_regex`
- ✅ Add better error handling to login endpoints
- ✅ Add logging for debugging

### Step 2: Commit and Push Changes

```bash
cd TrackerWorkflow_API
git add main.py
git commit -m "Fix CORS wildcard support and add error handling"
git push origin main
```

### Step 3: Check App Runner Logs

The 500 error means something is crashing. Check the logs:

1. **Go to AWS App Runner Console**

   - https://console.aws.amazon.com/apprunner/
   - Select your backend service: `service_track_one`

2. **View Logs**

   - Click on your service
   - Go to **"Logs"** tab
   - Look for recent errors (red lines)
   - Common errors:
     - Database connection failures
     - Missing environment variables
     - Import errors

3. **Check Recent Deployments**
   - Go to **"Deployments"** tab
   - Check if the latest deployment succeeded
   - If it failed, click on it to see error details

### Step 4: Verify Environment Variables

Go to **App Runner → Your Service → Configuration → Environment variables**

Make sure you have **ALL** of these:

```env
DATABASE_URL=postgresql://postgres:w1p.z|qj9VV!b|OiPaaRn|4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow

GOOGLE_CLIENT_ID=129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com

GOOGLE_CLIENT_SECRET=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

GOOGLE_REDIRECT_URI=https://9uwp8ycrdq.us-east-1.awsapprunner.com/auth/google/callback

SECRET_KEY=uygduweydwudywugcgmjkiuytcxzszdsiutuytytrthfd

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ IMPORTANT:**

- Make sure `DATABASE_URL` is the **FIRST** variable (or at least present)
- Check for typos in variable names
- Make sure values are complete (not truncated)

### Step 5: Rebuild App Runner Service

After updating code and environment variables:

1. **Option A: Automatic Rebuild (if using GitHub)**

   - Push code to GitHub
   - App Runner will automatically rebuild
   - Wait 5-10 minutes for deployment

2. **Option B: Manual Rebuild**
   - Go to App Runner → Your Service
   - Click **"Deploy"** or **"Rebuild"**
   - Wait for deployment to complete

### Step 6: Test the Backend Directly

Before testing from frontend, test the backend directly:

```bash
# Test if backend is accessible
curl https://9uwp8ycrdq.us-east-1.awsapprunner.com/

# Test login endpoint (should return 422 for missing data, not 500)
curl -X POST https://9uwp8ycrdq.us-east-1.awsapprunner.com/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

If you get a 500 error, check the App Runner logs to see the actual error message.

## 🔍 Common Issues & Fixes

### Issue 1: Database Connection Error

**Error in logs:**

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Fix:**

- Check `DATABASE_URL` is correct
- Verify RDS security group allows App Runner IPs
- Check RDS is publicly accessible

### Issue 2: Missing Environment Variable

**Error in logs:**

```
KeyError: 'DATABASE_URL'
```

**Fix:**

- Add missing environment variables in App Runner
- Make sure variable names match exactly (case-sensitive)

### Issue 3: CORS Still Not Working

**Error:**

```
Access-Control-Allow-Origin header is missing
```

**Fix:**

- Make sure you pushed the updated `main.py` with CORS fixes
- Rebuild App Runner service
- Clear browser cache
- Check browser console for actual CORS error details

### Issue 4: Google OAuth 500 Error

**Error in logs:**

```
google.auth.exceptions.GoogleAuthError
```

**Fix:**

- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Check `GOOGLE_REDIRECT_URI` matches App Runner URL
- Make sure Google OAuth credentials are enabled in Google Cloud Console

## 🧪 Testing Checklist

After fixing, test these:

- [ ] Backend root endpoint works: `https://9uwp8ycrdq.us-east-1.awsapprunner.com/`
- [ ] Login endpoint doesn't return 500 (even with wrong credentials, should return 401)
- [ ] CORS headers are present (check Network tab in browser)
- [ ] Can register new user from frontend
- [ ] Can login with email/password from frontend
- [ ] Can login with Google OAuth from frontend

## 📊 Quick Debug Commands

### Check if backend is running:

```bash
curl -I https://9uwp8ycrdq.us-east-1.awsapprunner.com/
```

### Check CORS headers:

```bash
curl -I -X OPTIONS https://9uwp8ycrdq.us-east-1.awsapprunner.com/login \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST"
```

Should see:

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Credentials: true
```

## 🚀 Next Steps

1. **Commit and push the updated `main.py`**
2. **Check App Runner logs** to see the actual 500 error
3. **Verify environment variables** are all set correctly
4. **Rebuild App Runner service**
5. **Test from frontend** again

If you still get errors, **share the App Runner logs** and I'll help debug further!
