# 🔍 Debug 500 Internal Server Error on Login

## 🎯 Problem

Login endpoint returns `500 Internal Server Error` even though:

- ✅ Service is running
- ✅ Health checks are passing
- ✅ Database connects successfully
- ✅ Service stays up

## 🔍 Step 1: Check App Runner Logs for Error Details

The login endpoint has error logging, so the actual error should be in the logs:

1. **Go to App Runner Console:**

   - https://console.aws.amazon.com/apprunner/
   - Service: `service_track_one`
   - Click on **"Logs"** tab

2. **Look for Error Messages:**

   - Search for: `❌ Login error`
   - Or: `ERROR`
   - Or: `Traceback`
   - Look around the time you tried to login (12:59 PM based on your screenshot)

3. **Common Errors to Look For:**

### Error Type 1: Database Query Error

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Fix:** Database connection issue - check RDS security group

### Error Type 2: Password Verification Error

```
AttributeError: 'NoneType' object has no attribute 'password'
```

**Fix:** User doesn't exist in database

### Error Type 3: Bcrypt Error

```
TypeError: must be str, not None
```

**Fix:** Password field is None in database

### Error Type 4: JWT Token Error

```
jose.exceptions.JWTError: ...
```

**Fix:** SECRET_KEY issue

## 🔍 Step 2: Test with Known User

The user you're testing with: `testuser20251207233231@example.com`

**Check if this user exists in RDS:**

1. Connect to RDS via pgAdmin
2. Query: `SELECT email, password FROM users WHERE email = 'testuser20251207233231@example.com';`
3. If user doesn't exist, register first
4. If password is NULL, that's the issue

## 🔍 Step 3: Check Database Schema

The error might be due to:

- Missing `password` column
- `password` column is NULL
- Wrong column name

**Verify users table structure:**

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users';
```

Should have:

- `email` (varchar/text)
- `password` (varchar/text) - should NOT be nullable
- `hashed_password` (if using that instead)

## 🔍 Step 4: Check authenticate_user Function

The `authenticate_user` function in `crud.py` might be failing. Common issues:

1. **User not found:**

   ```python
   user = db.query(User).filter(User.email == email).first()
   if user is None:
       return None  # This should return 401, not 500
   ```

2. **Password is None:**

   ```python
   if not verify_password(password, user.password):
       return None
   ```

   If `user.password` is `None`, this will crash.

3. **Database connection lost:**
   - Connection might timeout
   - Session might be closed

## 🔧 Quick Fixes

### Fix 1: Add Better Error Handling

Update `crud.py` `authenticate_user` function:

```python
def authenticate_user(db: Session, email: str, password: str):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"User not found: {email}")
            return None

        if not user.password:
            logger.error(f"User {email} has no password set")
            return None

        if not verify_password(password, user.password):
            logger.warning(f"Invalid password for: {email}")
            return None

        return user
    except Exception as e:
        logger.error(f"Error in authenticate_user: {str(e)}", exc_info=True)
        raise
```

### Fix 2: Register a New User

If the user doesn't exist or has issues:

1. **Use API docs to register:**

   - Go to: `https://9uwp8ycrdq.us-east-1.awsapprunner.com/docs`
   - Use `/register` endpoint
   - Create a new user

2. **Or use SQL directly:**
   ```sql
   INSERT INTO users (email, password, name, created_at)
   VALUES (
       'test@example.com',
       '$2b$12$...', -- Hashed password
       'Test User',
       NOW()
   );
   ```

### Fix 3: Check Environment Variables

Verify in App Runner:

- `SECRET_KEY` is set (for JWT)
- `DATABASE_URL` is correct
- `ALGORITHM` is set (defaults to HS256)

## 🎯 Most Likely Causes

Based on the error pattern:

1. **User doesn't exist** (60% likely)

   - User `testuser20251207233231@example.com` not in database
   - **Fix:** Register the user first

2. **Password field is NULL** (30% likely)

   - User exists but `password` column is NULL
   - **Fix:** Update user password or re-register

3. **Database connection issue** (10% likely)
   - Connection drops during query
   - **Fix:** Check RDS security group and connection pooling

## 📋 Action Plan

1. **Check App Runner Logs** - Find the actual error message
2. **Verify user exists** - Check RDS database
3. **Test with registration** - Register a new user and try login
4. **Check password field** - Make sure it's not NULL
5. **Share the error** - If you find the error in logs, share it for specific fix

## 🔍 How to Get the Actual Error

The login endpoint logs errors with:

```python
logger.error(f"❌ Login error: {str(e)}", exc_info=True)
```

**In App Runner logs, look for:**

- `❌ Login error:` followed by the error message
- `Traceback` showing the full stack trace
- `ERROR` level messages around login time

**Share the error message from logs, and I can provide a specific fix!**

---

**Next Steps:**

1. Check App Runner logs for the actual error
2. Verify user exists in database
3. Try registering a new user
4. Share the error message if you find it
