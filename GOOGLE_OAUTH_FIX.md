# Google OAuth 405/401 Error - Complete Fix

## 🔍 Problem Diagnosis

**Error:** `405 Method Not Allowed` when using Google login

**Root Cause:**
- Frontend is trying to POST to `/login` on the **frontend URL** (`y55dfkjshm`)
- `/login` is a frontend route (GET), not a backend API endpoint
- The backend API endpoint is `/auth/google` (POST) on the **backend URL** (`9cqn6rispm`)
- **Issue:** `API_BASE_URL` is incorrectly set to the frontend URL instead of backend URL

## ✅ Solution Applied

### 1. **Fixed config.js** - Correct API Base URL
   - Added explicit function to determine API base URL
   - Added safety check to prevent using frontend URL as API URL
   - Fallback to correct backend URL: `https://9cqn6rispm.us-west-2.awsapprunner.com`
   - Added warning logs for debugging

### 2. **Updated Login.jsx** - Handle Credential Parameter
   - Added `useEffect` to check for `credential` query parameter
   - If credential exists, automatically process Google login
   - Redirects to dashboard on success

### 2. **Google Cloud Console Configuration**

**For Client ID:** `181234528314-h1a19g5pmjifbhlrg05suul24m67gmjt.apps.googleusercontent.com`

**Authorized JavaScript Origins:**
```
http://localhost:5173
https://y55dfkjshm.us-west-2.awsapprunner.com
```

**Authorized Redirect URIs:**
```
http://localhost:5173/auth/google/callback
http://localhost:5173/login
https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback
https://y55dfkjshm.us-west-2.awsapprunner.com/login
```

**Why both `/login` and `/auth/google/callback`?**
- `/auth/google/callback` - Dedicated callback route (preferred)
- `/login` - Fallback (Google redirects to current page, so if user clicks button on `/login`, it redirects back to `/login`)

### 3. **How It Works Now**

**Flow:**
1. User clicks "Sign in with Google" on `/login`
2. Google redirects to `/login?credential=XXXXX` (GET request)
3. Login page detects credential parameter
4. Login page calls `googleLogin(credential)` which sends POST to `/auth/google`
5. Backend verifies token and returns JWT
6. User redirected to `/dashboard`

**Alternative Flow (if on callback route):**
1. User clicks "Sign in with Google" 
2. Google redirects to `/auth/google/callback?credential=XXXXX`
3. GoogleCallback component handles it (already implemented)
4. Same process continues

## 🚨 CRITICAL: Set Environment Variable in Production

**The 405 error happens because `VITE_API_BASE_URL` is not set correctly in production.**

### For AWS App Runner (Frontend):

1. **Go to AWS App Runner Console**
2. **Select your frontend service** (`y55dfkjshm`)
3. **Go to Configuration → Environment Variables**
4. **Add/Update:**
   ```
   VITE_API_BASE_URL=https://9cqn6rispm.us-west-2.awsapprunner.com
   ```
5. **Save and Redeploy**

**Important:** 
- ✅ Backend URL: `https://9cqn6rispm.us-west-2.awsapprunner.com`
- ❌ NOT Frontend URL: `https://y55dfkjshm.us-west-2.awsapprunner.com`

### Alternative: Build with Environment Variable

If you can't set it in App Runner, set it during build:

```bash
cd TrackerWorkflow
VITE_API_BASE_URL=https://9cqn6rispm.us-west-2.awsapprunner.com npm run build
```

## 🧪 Testing

1. **Local Test:**
   ```bash
   # Start frontend
   cd TrackerWorkflow
   npm run dev
   
   # Visit http://localhost:5173/login
   # Click "Sign in with Google"
   # Should redirect and login successfully
   ```

2. **Production Test:**
   - Visit `https://y55dfkjshm.us-west-2.awsapprunner.com/login`
   - Open browser console (F12)
   - Check logs: `🔧 API_BASE_URL:` should show backend URL
   - Click "Sign in with Google"
   - Should work without 405 errors

## 📋 Checklist

- [x] Login.jsx handles credential parameter
- [x] GoogleCallback.jsx exists and handles credential
- [x] Backend `/auth/google` POST endpoint exists
- [ ] Google Console has correct JavaScript origins
- [ ] Google Console has correct redirect URIs (both `/login` and `/auth/google/callback`)
- [ ] Frontend and backend use same Google Client ID

## 🔧 Backend Verification

**Backend Route:** `POST /auth/google`
- Accepts: `{ "id_token": "..." }`
- Returns: `{ "access_token": "...", "token_type": "bearer" }`

**Backend Config:** `TrackerWorkflow_API/config.py`
```python
google_client_id: str = "181234528314-h1a19g5pmjifbhlrg05suul24m67gmjt.apps.googleusercontent.com"
```

## 🚨 Common Issues

### Issue: Still getting 405 "Method Not Allowed"
**Root Cause:** `API_BASE_URL` is set to frontend URL instead of backend URL

**Solution:**
1. Check browser console - look for `🔧 API_BASE_URL:` log
2. If it shows `y55dfkjshm` (frontend), that's the problem!
3. Set `VITE_API_BASE_URL` environment variable in AWS App Runner
4. Rebuild and redeploy frontend
5. Verify in console that API_BASE_URL now shows `9cqn6rispm` (backend)

### Issue: Still getting 405 after setting environment variable
**Solution:** 
- Environment variables in Vite must be set at **BUILD TIME**
- If you set it in App Runner after build, you need to rebuild
- Or set it in your build command/CI/CD pipeline

### Issue: Still getting 401 "Invalid Google token"
**Solution:** 
1. Verify frontend and backend use same Client ID
2. Check backend logs to see token verification error
3. Ensure Google Console has correct JavaScript origins

### Issue: Redirect loops
**Solution:** Check that credential parameter is being processed and removed from URL

## 📝 Notes

- Google Identity Services (GSI) always redirects to the **current page**
- You cannot specify a custom redirect path with GSI
- Solution: Handle credential parameter on any page that might receive it
- Both `/login` and `/auth/google/callback` now handle credentials

