# Gmail Authentication Stability Fix

## What Was Implemented (May 11, 2026)

### 1. Proactive Token Health Check (`check_auth.py`)
- **Purpose**: Check and refresh tokens BEFORE they cause failures
- **What it does**:
  - Checks token expiry time
  - Proactively refreshes if expiring in next 5 minutes
  - Provides clear error messages if refresh token is invalid
  - Exit code 0 = healthy, 1 = needs manual re-auth

### 2. Updated Wrapper Script (`run_digest.sh`)
- **Now runs auth check first** before attempting to send digest
- **Fails fast** if authentication is broken
- **Clearer logging** showing exactly where failures occur
- **Prevents wasted API calls** when auth is already broken

### 3. Improved Error Handling (`email_sender.py`)
- **Wrapped all auth steps in try-catch** blocks
- **Returns False instead of raising exceptions** (prevents crashes)
- **Clear error messages** for each failure type
- **Continues when possible** (e.g., if save fails but creds are valid)

## What You Still Need To Do

### Critical: Fix Google Cloud Console Settings

Your OAuth app is likely in "Testing" mode, which causes tokens to expire or become invalid more frequently.

**Steps to fix:**

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select project: `daily-digest-490503`

2. **Navigate to OAuth Consent Screen**
   - Left menu → APIs & Services → OAuth consent screen
   - Current status: likely shows "Testing" with a warning

3. **Publish the App** (Recommended Option)
   - Click "PUBLISH APP" button
   - This moves it from "Testing" to "In Production"
   - **Important**: For personal use (your email only), you don't need Google verification
   - **Benefit**: Refresh tokens won't expire after 7 days
   - **Caveat**: If you add new scopes later, you'll need to re-auth once

   **OR**

4. **Add Your Email to Test Users** (Alternative)
   - Stay in "Testing" mode
   - Add `kevin.thakkar@gmail.com` to the test users list
   - This prevents the 7-day token expiry for your account
   - **Downside**: Still has some limitations

5. **Re-authenticate After Publishing**
   ```bash
   cd /Users/Kevin/Documents/claude/daily-digest
   rm credentials/token.json
   source venv/bin/activate
   python -c "from email_sender import EmailSender; EmailSender().authenticate()"
   ```

### Why This Matters

| Mode | Refresh Token Lifetime | Reliability |
|------|----------------------|-------------|
| **Testing (unpublished)** | 7 days max | ⚠️ Poor - tokens expire frequently |
| **Testing (with test user)** | Longer, but still limited | ⚙️ Better |
| **Published (production)** | No expiration | ✅ Best - only revoked on password change or manual revoke |

## How The System Now Works

### Daily Automated Flow (6:00 AM)
```
1. Cron triggers run_digest.sh
2. run_digest.sh runs check_auth.py
   ├─ Token healthy? → Continue to step 3
   └─ Token broken? → Log error, exit (no digest sent)
3. Generate and send digest
4. Log results
```

### Manual Testing
```bash
# Check token health
python check_auth.py

# Test digest send
python generate_preview.py --send
```

## Monitoring & Maintenance

### Check Logs
```bash
# View recent digest runs
tail -50 logs/wrapper.log

# Check for auth failures
grep -i "auth\|token" logs/wrapper.log | tail -20
```

### Manual Re-authentication (if needed)
If you see "Manual re-authentication required" in logs:
```bash
cd /Users/Kevin/Documents/claude/daily-digest
source venv/bin/activate
python -c "from email_sender import EmailSender; EmailSender().authenticate()"
```
A browser will open for re-auth.

## Expected Behavior Now

### ✅ Good Signs
- Daily digest arrives at ~6:00 AM
- `check_auth.py` shows "Token is healthy and valid!"
- Wrapper log shows "✅ Authentication healthy, proceeding with digest..."

### ⚠️ Warning Signs
- `check_auth.py` shows token refresh failures
- Wrapper log shows "AUTH FAILED" messages
- No digest emails for multiple days

### 🚨 Action Required
If auth keeps failing every 7 days:
- **Root cause**: Google Cloud app still in "Testing" mode
- **Solution**: Publish the app (see steps above)

## Testing The Fix

Run this to verify everything works:
```bash
cd /Users/Kevin/Documents/claude/daily-digest
source venv/bin/activate

# Test 1: Check auth health
python check_auth.py
echo "Exit code: $?"

# Test 2: Send test digest
python generate_preview.py --send
```

Both should complete without errors.

## Summary

**Implemented:**
- ✅ Proactive token refresh before expiry
- ✅ Auth check runs before every digest
- ✅ Better error handling with clear messages
- ✅ Fail-fast behavior (don't try to send if auth is broken)

**Still Needed (YOU):**
- ⏳ Publish Google Cloud app to production mode
- ⏳ Re-authenticate once after publishing

**Expected Result:**
- 📧 Reliable daily digests with no auth failures
- 🔄 Tokens auto-refresh seamlessly
- 💪 Robust error handling if something does go wrong
