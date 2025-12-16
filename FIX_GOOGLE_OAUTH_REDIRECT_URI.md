# Fix Google OAuth Redirect URI Mismatch Error

## Problem

**Error:** `redirect_uri_mismatch` when trying to use Google login in deployed environment.

**Why it works locally but not deployed:**
- Local: Frontend at `http://localhost:5173` → redirects to `http://localhost:5173/auth/google/callback` ✅
- Deployed: Frontend at `https://y55dfkjshm.us-west-2.awsapprunner.com` → needs redirect URI configured in Google Cloud Console ❌

## Root Cause

The Google Sign-In JavaScript library automatically uses the current origin (`window.location.origin`) for the redirect URI. So:
- **Local:** `http://localhost:5173/auth/google/callback`
- **Deployed:** `https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback`

This redirect URI **must be exactly** configured in Google Cloud Console.

## Solution: Update Google Cloud Console

### Step 1: Get Your Frontend URL

Your deployed frontend URL is:
```
https://y55dfkjshm.us-west-2.awsapprunner.com
```

So the redirect URI should be:
```
https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback
```

### Step 2: Update Google Cloud Console

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com/
   - Select your project

2. **Navigate to OAuth Credentials:**
   - Go to **APIs & Services** → **Credentials**
   - Find your OAuth 2.0 Client ID: `129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com`
   - Click **Edit** (pencil icon)

3. **Add Authorized Redirect URIs:**
   
   In the **Authorized redirect URIs** section, make sure you have:
   
   ```
   http://localhost:5173/auth/google/callback
   https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback
   ```
   
   **Important:**
   - Add BOTH local and deployed URIs
   - The URI must match **exactly** (including `https://`, no trailing slash)
   - No spaces before or after
   - Case-sensitive

4. **Also Check Authorized JavaScript Origins:**
   
   Add these to **Authorized JavaScript origins**:
   ```
   http://localhost:5173
   https://y55dfkjshm.us-west-2.awsapprunner.com
   ```

5. **Save Changes:**
   - Click **Save** at the bottom
   - Changes take effect immediately (no waiting)

### Step 3: Fix Backend Config (Remove Space)

There's a typo in `config.py` - a space in the redirect URI. Fix it:

**File:** `TrackerWorkflow_API/config.py`

**Line 25 - Current (WRONG):**
```python
google_redirect_uri: str = "https://9cqn6rispm.us-west-2.awsapprunner.com /auth/google/callback"
```

**Should be (CORRECT):**
```python
google_redirect_uri: str = "https://9cqn6rispm.us-west-2.awsapprunner.com/auth/google/callback"
```

**Note:** The backend redirect URI is only used for compatibility. The frontend uses its own origin automatically.

### Step 4: Verify Frontend Configuration

Make sure your frontend is using the correct Google Client ID:

**File:** `TrackerWorkflow/src/config/config.js`

Should have:
```javascript
GOOGLE_CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
```

And `VITE_GOOGLE_CLIENT_ID` should be set to:
```
129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com
```

## Quick Checklist

- [ ] Google Cloud Console → OAuth 2.0 Client ID → Edit
- [ ] Added redirect URI: `https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback`
- [ ] Added JavaScript origin: `https://y55dfkjshm.us-west-2.awsapprunner.com`
- [ ] Kept local redirect URI: `http://localhost:5173/auth/google/callback`
- [ ] Saved changes in Google Cloud Console
- [ ] Fixed space in `config.py` redirect URI (optional, for backend compatibility)
- [ ] Test Google login on deployed frontend

## Testing

1. **Open deployed frontend:**
   ```
   https://y55dfkjshm.us-west-2.awsapprunner.com/login
   ```

2. **Click "Sign in with Google"**

3. **Should redirect to Google sign-in page** (not show error)

4. **After signing in, should redirect back to your app**

## Common Mistakes

### ❌ Wrong Redirect URI Format
```
https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback/  ← Trailing slash
https://y55dfkjshm.us-west-2.awsapprunner.com /auth/google/callback  ← Space
http://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback    ← http instead of https
```

### ✅ Correct Redirect URI Format
```
https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback
```

## Why This Happens

Google OAuth requires **exact matching** of redirect URIs for security:
- Prevents unauthorized redirects
- Ensures tokens go to the right application
- Protects against phishing attacks

The redirect URI must be:
- **Exact match** (no wildcards)
- **Case-sensitive**
- **Include protocol** (`https://` or `http://`)
- **Include full path** (`/auth/google/callback`)

## Additional Notes

### If You Have Multiple Environments

Add all redirect URIs to Google Cloud Console:
```
http://localhost:5173/auth/google/callback                    # Local dev
https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback  # Production
https://staging.example.com/auth/google/callback              # Staging (if you have one)
```

### If Frontend URL Changes

If you redeploy and get a new App Runner URL:
1. Update Google Cloud Console with new redirect URI
2. Update frontend environment variables if needed
3. Rebuild and redeploy frontend

## Still Not Working?

1. **Check browser console (F12):**
   - Look for specific error messages
   - Check what redirect URI is being sent

2. **Verify in Google Cloud Console:**
   - Double-check redirect URI matches exactly
   - Check JavaScript origins are set
   - Make sure OAuth consent screen is configured

3. **Check frontend logs:**
   - Should see: `🔐 Initializing Google Sign-In with Client ID: ...`
   - Should see: `📍 Current origin: https://y55dfkjshm.us-west-2.awsapprunner.com`

4. **Test with curl:**
   ```bash
   # Check if frontend is accessible
   curl -I https://y55dfkjshm.us-west-2.awsapprunner.com
   ```

## Summary

The fix is simple:
1. **Add the deployed frontend redirect URI to Google Cloud Console**
2. **Make sure it matches exactly** (no spaces, correct protocol, correct path)
3. **Save and test**

That's it! The redirect URI mismatch error should be resolved.

