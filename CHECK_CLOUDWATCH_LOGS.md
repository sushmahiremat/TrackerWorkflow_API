# 🔍 Check CloudWatch Logs for Login Error

## 🎯 Problem

You're getting `500 Internal Server Error` on login, but App Runner logs don't show the login attempt. The request IS reaching the backend (568ms processing time), but logs aren't appearing.

## ✅ Solution: Check CloudWatch Logs Directly

App Runner's log viewer might be filtering or not showing all logs. CloudWatch has the complete logs.

### Step 1: Go to CloudWatch Logs

1. **Open CloudWatch Console:**

   - https://console.aws.amazon.com/cloudwatch/
   - Make sure you're in the **us-east-1** region (where your backend is)

2. **Find Your Log Group:**

   - Click **"Log groups"** in the left sidebar
   - Look for log group starting with: `/aws/apprunner/`
   - It might be named like:
     - `/aws/apprunner/service_track_one/...`
     - `/aws/apprunner/9uwp8ycrdq/...`
     - Or search for: `apprunner`

3. **Open the Log Group:**

   - Click on the log group
   - You'll see multiple log streams (one per deployment/instance)

4. **Open the Most Recent Log Stream:**
   - Click on the most recent log stream (highest timestamp)
   - This contains the current running instance's logs

### Step 2: Search for Login Attempts

1. **In the Log Stream:**

   - Look for a search box
   - Search for: `login`
   - Or: `POST /login`
   - Or: `🔐 Login attempt`
   - Or: `ERROR`

2. **Look Around the Time You Tried Login:**
   - Your login attempt was at: `13:04` (1:04 PM)
   - Look for logs around that time
   - You should see:
     - `POST /login HTTP/1.1`
     - `🔐 Login attempt for email: test@example.com`
     - `❌ Login error: [error message]`

### Step 3: Check for Request Parsing Errors

If the error happens before our logging code, you might see:

- Pydantic validation errors
- Request body parsing errors
- Schema validation errors

Look for:

- `ValidationError`
- `422` status codes
- `Request validation error`

## 🔧 Alternative: Add More Verbose Logging

If CloudWatch also doesn't show logs, we can add middleware to log ALL requests:

### Add Request Logging Middleware

Add this to `main.py` before the CORS middleware:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log all incoming requests
    logger.info(f"📥 {request.method} {request.url.path} from {request.client.host}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ {request.method} {request.url.path} - ERROR after {process_time:.3f}s: {str(e)}", exc_info=True)
        raise
```

This will log ALL requests, so you'll definitely see the login attempt.

## 🐛 Possible Causes

### Cause 1: Error Before Logging Code

If the error happens during:

- Request parsing (Pydantic validation)
- Database connection (get_db dependency)
- Middleware processing

Then our `logger.info()` might not execute.

**Fix:** Add middleware logging (see above)

### Cause 2: Logs Not Flushing

Python's logging might not be flushing to CloudWatch immediately.

**Fix:** Add explicit flush or use print() statements (they always show up)

### Cause 3: Log Level Filtering

App Runner might be filtering out INFO level logs.

**Fix:** Check CloudWatch directly (has all logs)

## 🎯 Quick Test: Add Print Statements

Since `print()` statements always show up in logs, let's add them temporarily:

```python
@app.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    print("=" * 50)
    print("🔐 LOGIN ATTEMPT STARTED")
    print(f"Email: {user_credentials.email}")
    print("=" * 50)

    try:
        logger.info(f"🔐 Login attempt for email: {user_credentials.email}")
        print(f"🔐 Login attempt for email: {user_credentials.email}")

        user = authenticate_user(db, user_credentials.email, user_credentials.password)
        print(f"User found: {user is not None}")

        if not user:
            print("❌ User not found or invalid password")
            logger.warning(f"❌ Login failed: Invalid credentials for {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print("✅ User authenticated, creating token...")
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        print("✅ Token created successfully")
        logger.info(f"✅ Login successful for: {user_credentials.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        print(f"❌ HTTPException: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        logger.error(f"❌ Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
```

## 📋 Action Plan

1. **Check CloudWatch Logs** (most important):

   - Go to CloudWatch → Log groups
   - Find App Runner log group
   - Open most recent log stream
   - Search for `login` or `POST`

2. **If CloudWatch also doesn't show logs:**

   - Add the print statements above
   - Commit and push
   - Wait for redeployment
   - Try login again
   - Check logs (print statements always show up)

3. **Share the Error:**
   - Once you find the error in CloudWatch, share it
   - Or share the print statement output

---

**Next Steps:**

1. Check CloudWatch logs directly
2. Search for `login` or `POST /login`
3. Share the error message you find
