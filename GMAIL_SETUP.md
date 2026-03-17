# Gmail OAuth Setup Guide

Follow these steps to enable Gmail access for Daily Digest.

## Step 1: Create Google Cloud Project

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. Click **"Select a project"** dropdown (top left)
3. Click **"New Project"**
4. Name it: `Daily Digest` (or anything you want)
5. Click **"Create"**

## Step 2: Enable Gmail API

1. Make sure your new project is selected (check top left)
2. Go to **[Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)**
3. Click **"Enable"**
4. Wait for it to enable (~30 seconds)

## Step 3: Configure OAuth Consent Screen

1. Go to **[OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)**
2. Select **"External"** (unless you have a workspace)
3. Click **"Create"**
4. Fill in required fields:
   - **App name:** Daily Digest
   - **User support email:** Your email
   - **Developer contact:** Your email
5. Click **"Save and Continue"**
6. On "Scopes" page: Click **"Save and Continue"** (we'll add scopes later)
7. On "Test users" page:
   - Click **"Add Users"**
   - Add your Gmail address
   - Click **"Save and Continue"**
8. Click **"Back to Dashboard"**

## Step 4: Create OAuth Credentials

1. Go to **[Credentials](https://console.cloud.google.com/apis/credentials)**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Application type: Select **"Desktop app"**
4. Name: `Daily Digest Desktop`
5. Click **"Create"**
6. Click **"Download JSON"** on the popup (or click the download icon next to your credential)
7. **IMPORTANT:** Rename the downloaded file to `credentials.json`

## Step 5: Move credentials.json to Project

1. Move the downloaded `credentials.json` file to:
   ```
   /Users/Kevin/Documents/claude/daily-digest/credentials/credentials.json
   ```

## Step 6: Run Setup Script

Open terminal and run:

```bash
cd /Users/Kevin/Documents/claude/daily-digest
source venv/bin/activate
python gmail_setup.py
```

This will:
1. Open your browser
2. Ask you to sign in to Google
3. Ask you to authorize "Daily Digest" to read your Gmail
4. Save the authorization token
5. Test the connection by fetching 5 recent emails

## Troubleshooting

**"Access blocked: This app's request is invalid"**
- Make sure you added yourself as a test user in OAuth consent screen

**"credentials.json not found"**
- Check the file is named exactly `credentials.json` (not `credentials (1).json` or `client_secret_....json`)
- Check it's in the `credentials/` folder

**Other errors**
- Make sure Gmail API is enabled
- Make sure you selected the correct project in Google Cloud Console

## After Setup

Once complete, you'll have:
- ✅ `credentials/credentials.json` - OAuth client credentials
- ✅ `credentials/token.json` - Your authorized access token

The script will automatically refresh tokens when they expire, so you only need to do this once!
