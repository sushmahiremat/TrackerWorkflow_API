# 🔍 How to Check App Runner Logs for 500 Error

## 🎯 The Problem

Your backend is returning **500 Internal Server Error** when trying to login. The CORS headers are working (we can see `Access-Control-Allow-Origin` in the response), but the backend is crashing.

## 📊 What We Know from Network Tab

- ✅ CORS is working (`Access-Control-Allow-Origin: http://localhost:5173` is present)
- ❌ Backend is crashing (500 error)
- Response is very small (54 bytes) - likely a generic error message
- Backend took 591ms before failing (`X-Envoy-Upstream-Service-Time: 591`)

## 🔍 Step-by-Step: Check App Runner Logs

### Step 1: Go to AWS App Runner Console

1. Open: https://console.aws.amazon.com/apprunner/
2. Make sure you're in the **us-east-1** region (your backend is there)
3. Click on your backend service: **`service_track_one`**

### Step 2: View Logs

1. Click on the **"Logs"** tab (or **"Observability"** → **"Logs"**)
2. You'll see a log stream with timestamps
3. Look for errors around the time you tried to login (check the time in your network tab: `18:15:32 GMT`)

### Step 3: Look for These Common Errors

#### Error Type 1: Database Connection Failed
```
sqlalchemy.exc.OperationalError: could not connect to server
Connection refused
```

**Fix:** Check `DATABASE_URL` environment variable in App Runner

#### Error Type 2: Missing Environment Variable
```
KeyError: 'DATABASE_URL'
NameError: name 'DATABASE_URL' is not defined
```

**Fix:** Add missing environment variables

#### Error Type 3: Import Error
```
ModuleNotFoundError: No module named 'xxx'
ImportError: cannot import name 'xxx'
```

**Fix:** Check `requirements.txt` has all dependencies

#### Error Type 4: Google OAuth Error
```
google.auth.exceptions.GoogleAuthError
ValueError: Invalid token
```

**Fix:** Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

#### Error Type 5: Database Query Error
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```

**Fix:** Database tables not created - backend needs to create them

### Step 4: Check Recent Deployments

1. Go to **"Deployments"** tab
2. Check if the latest deployment succeeded (green checkmark)
3. If it failed (red X), click on it to see error details
4. Common deployment errors:
   - Docker build failed
   - ECR image pull failed
   - Health check failed

## 🔧 Quick Fixes Based on Common Errors

### If Database Connection Error:

1. Go to **Configuration** → **Environment variables**
2. Verify `DATABASE_URL` is set:
   ```
   DATABASE_URL=postgresql://postgres:w1p.z|qj9VV!b|OiPaaRn|4W.P69@trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com:5432/TrackerWorkflow
   ```
3. Make sure RDS security group allows App Runner IPs
4. Check RDS is publicly accessible

### If Missing Environment Variable:

1. Go to **Configuration** → **Environment variables**
2. Add all required variables (see list below)
3. Click **"Save"** and wait for redeployment

### If Import Error:

1. Check `requirements.txt` has all dependencies
2. Rebuild Docker image
3. Push to ECR
4. Redeploy App Runner

## 📋 Required Environment Variables Checklist

Make sure ALL of these are set in App Runner:

- [ ] `DATABASE_URL` (full PostgreSQL connection string)
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `GOOGLE_REDIRECT_URI` (should be App Runner URL)
- [ ] `SECRET_KEY`
- [ ] `ALGORITHM` (optional, defaults to HS256)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` (optional, defaults to 30)

## 🚀 After Finding the Error

1. **Fix the issue** (add missing env var, fix database connection, etc.)
2. **Redeploy** the service
3. **Wait 5-10 minutes** for deployment
4. **Test again** from frontend

## 💡 Pro Tip: Enable Detailed Logging

The updated `main.py` now has better logging. After you deploy it, you'll see:
- `🔐 Login attempt for email: ...`
- `✅ Login successful for: ...`
- `❌ Login error: ...`

This will help identify exactly where it's failing.

## 📸 Share the Logs

Once you find the error in App Runner logs, share it with me and I'll help you fix it!

---

**Next Steps:**
1. Check App Runner logs (follow steps above)
2. Find the actual error message
3. Share it with me or fix based on the error type above
4. Redeploy and test again

