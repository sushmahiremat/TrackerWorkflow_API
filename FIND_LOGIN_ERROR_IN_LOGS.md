# 🔍 Find Login Error in App Runner Logs

## 🎯 Problem

You're getting `500 Internal Server Error` on login, but the logs you shared don't show any login attempts. This means either:

1. The request isn't reaching the backend
2. The logs are filtered
3. You need to try login again while watching logs

## 🔍 What to Look For

When you try to login, you should see these log messages:

### Expected Login Logs:

1. **Login attempt:**

   ```
   🔐 Login attempt for email: testuser20251207233231@example.com
   ```

2. **If successful:**

   ```
   ✅ Login successful for: testuser20251207233231@example.com
   ```

3. **If error occurs:**

   ```
   ❌ Login error: [error message here]
   Traceback (most recent call last):
     ...
   ```

4. **HTTP request:**
   ```
   INFO:     169.254.172.2:XXXXX - "POST /login HTTP/1.1" 500
   ```

## 📋 Step-by-Step: Find the Error

### Step 1: Try Login While Watching Logs

1. **Open App Runner Logs:**

   - Go to: https://console.aws.amazon.com/apprunner/
   - Service: `service_track_one`
   - Click **"Logs"** tab
   - Keep this tab open

2. **Try Login:**

   - Go to: `https://9uwp8ycrdq.us-east-1.awsapprunner.com/docs`
   - Use `/login` endpoint
   - Click **"Execute"**

3. **Watch Logs in Real-Time:**
   - Immediately after clicking "Execute", watch the logs
   - Look for new log entries
   - You should see:
     - `POST /login HTTP/1.1`
     - `🔐 Login attempt for email: ...`
     - Either success or error message

### Step 2: Check for POST Requests

The logs you shared only show `GET /` requests (health checks). Look for:

```
POST /login HTTP/1.1
```

If you don't see this, the request isn't reaching the backend.

### Step 3: Check Log Filter

1. **In App Runner Logs:**

   - Look for a search/filter box
   - Try searching for: `login`
   - Or: `POST`
   - Or: `ERROR`

2. **Check Log Level:**
   - Make sure you're viewing all log levels (INFO, WARNING, ERROR)
   - Not just INFO

### Step 4: Check CloudWatch Logs

If App Runner logs don't show the error:

1. **Go to CloudWatch:**

   - https://console.aws.amazon.com/cloudwatch/
   - Go to **"Log groups"**
   - Find log group for your App Runner service
   - Usually named: `/aws/apprunner/service_track_one/...`

2. **View Recent Logs:**
   - Click on the log group
   - Click on the most recent log stream
   - Search for: `login` or `ERROR`

## 🐛 Common Issues

### Issue 1: Request Not Reaching Backend

**Symptoms:**

- No `POST /login` in logs
- Only health checks visible

**Possible Causes:**

- App Runner load balancer blocking the request
- CORS preflight failing
- Request timing out before reaching backend

**Fix:**

- Check if you can access `/docs` (API documentation)
- Try curl directly:
  ```bash
  curl -X POST https://9uwp8ycrdq.us-east-1.awsapprunner.com/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test123"}'
  ```

### Issue 2: Logs Not Showing POST Requests

**Symptoms:**

- Only GET requests visible
- Login attempts don't appear

**Fix:**

- Check log filter settings
- Try CloudWatch logs instead
- Check if logging level is set correctly

### Issue 3: Error Happening Before Logging

**Symptoms:**

- Request reaches backend but crashes immediately
- No log messages at all

**Fix:**

- Check if database connection is working
- Verify all environment variables are set
- Check if there's a startup error

## ✅ Quick Test

Try this to see if login requests are reaching the backend:

1. **Add a simple test endpoint** (temporary):

   ```python
   @app.post("/test-login")
   def test_login():
       return {"message": "Login endpoint is reachable"}
   ```

2. **Test it:**
   - Go to `/docs`
   - Try `/test-login` endpoint
   - If this works, the issue is in the login logic
   - If this doesn't work, the issue is with routing/network

## 🎯 Action Plan

1. **Try login again** while watching App Runner logs in real-time
2. **Look for** `POST /login` or `🔐 Login attempt` messages
3. **If you see an error**, copy the full error message and traceback
4. **If you don't see any login logs**, the request isn't reaching the backend
5. **Check CloudWatch logs** as an alternative

## 📝 What to Share

When you find the error, share:

- The full error message
- The traceback (if available)
- The timestamp of the error
- Any `POST /login` log entries

---

**Next Steps:**

1. Try login again while watching logs
2. Look for `POST /login` or error messages
3. Share what you find
