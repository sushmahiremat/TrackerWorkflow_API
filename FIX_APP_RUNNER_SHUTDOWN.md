# 🔧 Fix: App Runner Service Shutting Down

## 🔍 Problem Analysis

From your logs, I can see:
- ✅ Service starts successfully
- ✅ Database connects correctly
- ✅ Server runs on port 8001
- ❌ Service shuts down after ~10 minutes

**Root Cause:** App Runner's health check is likely failing or misconfigured, causing the service to be marked unhealthy and shut down.

## ✅ What's Working

1. **Root endpoint exists** (`/` returns `{"message": "TrackerWorkflow API is running!"}`)
2. **Docker health check** is configured correctly
3. **Database connection** works
4. **Server starts** on port 8001

## 🔧 Solution: Fix App Runner Health Check Configuration

### Step 1: Check App Runner Health Check Settings

1. **Go to App Runner Console:**
   - https://console.aws.amazon.com/apprunner
   - Service: `service_track_one`
   - Click on the service

2. **Go to Configuration:**
   - Click "Configuration" tab
   - Click "Edit" button

3. **Check Health Check Settings:**
   - Scroll to "Health check" section
   - **Health check path:** Should be `/` (root endpoint)
   - **Health check interval:** Usually 10 seconds
   - **Health check timeout:** Usually 5 seconds
   - **Healthy threshold:** Usually 1
   - **Unhealthy threshold:** Usually 5

4. **Verify Port Configuration:**
   - **Port:** Should be `8001`
   - **Protocol:** Should be `HTTP`

### Step 2: Update Health Check Configuration

If health check path is wrong, update it:

**Correct Settings:**
- **Health check path:** `/`
- **Port:** `8001`
- **Protocol:** `HTTP`
- **Health check interval:** `10` seconds
- **Health check timeout:** `5` seconds
- **Healthy threshold:** `1`
- **Unhealthy threshold:** `5`

### Step 3: Verify Root Endpoint Works

Test the root endpoint manually:

```bash
curl https://9uwp8ycrdq.us-east-1.awsapprunner.com/
```

Should return:
```json
{"message": "TrackerWorkflow API is running!"}
```

## 🐛 Alternative Issues

### Issue 1: App Runner Auto-Scaling

App Runner might be scaling down to 0 instances when idle. Check:

1. **Go to Configuration → Auto scaling**
2. **Min size:** Should be `1` (not `0`)
3. **Max size:** Can be `1` or higher

**Fix:** Set minimum instances to `1` to prevent shutdown.

### Issue 2: Health Check Path Mismatch

If App Runner is checking a different path (e.g., `/health`), it will fail.

**Fix:** Either:
- Update App Runner health check path to `/`
- Or add a `/health` endpoint in `main.py`:

```python
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Issue 3: Port Mismatch

If App Runner is checking a different port, it will fail.

**Fix:** Verify App Runner port is set to `8001` in Configuration.

### Issue 4: Network/Security Issues

If App Runner can't reach the service internally, health checks fail.

**Fix:** Check App Runner VPC configuration (if using custom VPC).

## 🔍 How to Diagnose

### Check App Runner Logs

1. **Go to App Runner Console → Logs**
2. **Look for:**
   - Health check failures
   - Connection errors
   - Timeout errors

### Check CloudWatch Metrics

1. **Go to CloudWatch → Metrics → App Runner**
2. **Check:**
   - `HealthyHostCount` - Should be > 0
   - `UnHealthyHostCount` - Should be 0
   - `RequestCount` - Should show activity

### Test Health Check Manually

```bash
# Test root endpoint
curl https://9uwp8ycrdq.us-east-1.awsapprunner.com/

# Test with verbose output
curl -v https://9uwp8ycrdq.us-east-1.awsapprunner.com/
```

## ✅ Quick Fix Checklist

- [ ] App Runner health check path is `/`
- [ ] App Runner port is `8001`
- [ ] Root endpoint (`/`) returns 200 OK
- [ ] Minimum instances is set to `1` (not 0)
- [ ] Health check interval is reasonable (10 seconds)
- [ ] Health check timeout is reasonable (5 seconds)

## 🚀 Recommended Configuration

**Health Check:**
- Path: `/`
- Interval: `10` seconds
- Timeout: `5` seconds
- Healthy threshold: `1`
- Unhealthy threshold: `5`

**Auto Scaling:**
- Min size: `1` (prevents shutdown)
- Max size: `5` (or as needed)
- Concurrency: `10` (or as needed)

**Port:**
- Port: `8001`
- Protocol: `HTTP`

## 📝 After Fixing

1. **Save configuration** in App Runner
2. **Wait for redeployment** (5-10 minutes)
3. **Check logs** - should see continuous running (no shutdown)
4. **Test endpoint** - should respond consistently
5. **Monitor for 30+ minutes** - service should stay running

## 🎯 Most Likely Fix

Based on the logs, the most likely issue is:

**App Runner health check path is wrong or minimum instances is 0.**

**Quick fix:**
1. Go to App Runner → Configuration → Edit
2. Set health check path to `/`
3. Set minimum instances to `1`
4. Save and wait for redeployment

---

**After applying the fix, your service should:**
- ✅ Stay running continuously
- ✅ Pass health checks
- ✅ Not shut down after 10 minutes
- ✅ Respond to requests consistently

