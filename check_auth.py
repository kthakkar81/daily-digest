#!/usr/bin/env python3
"""
Proactive authentication health check and refresh script.
Run this before the digest to ensure tokens are fresh.
"""
import os
import pickle
import sys
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from config import GMAIL_TOKEN_PATH, GMAIL_CREDENTIALS_PATH, GMAIL_SCOPES
from google_auth_oauthlib.flow import InstalledAppFlow


def check_and_refresh_token():
    """
    Check token health and proactively refresh if needed.
    Returns True if token is healthy, False if manual re-auth needed.
    """
    if not os.path.exists(GMAIL_TOKEN_PATH):
        print("❌ No token file found. Manual authentication required.")
        print(f"   Run: python -c \"from email_sender import EmailSender; EmailSender().authenticate()\"")
        return False

    try:
        # Load existing token
        with open(GMAIL_TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

        # Check token status
        print("🔍 Token Status Check")
        print(f"   Valid: {creds.valid}")
        print(f"   Expired: {creds.expired}")
        print(f"   Has refresh token: {bool(creds.refresh_token)}")

        if hasattr(creds, 'expiry') and creds.expiry:
            print(f"   Expiry: {creds.expiry} UTC")
            time_until_expiry = creds.expiry - datetime.utcnow()
            print(f"   Time until expiry: {time_until_expiry}")

            # Proactively refresh if expiring in next 5 minutes
            if time_until_expiry < timedelta(minutes=5):
                print("⚠️  Token expiring soon, refreshing proactively...")

        # Attempt refresh if needed
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                print("♻️  Refreshing expired token...")
                try:
                    creds.refresh(Request())

                    # Save refreshed token
                    with open(GMAIL_TOKEN_PATH, 'wb') as token:
                        pickle.dump(creds, token)

                    print("✅ Token refreshed successfully!")
                    print(f"   New expiry: {creds.expiry} UTC")
                    return True

                except Exception as refresh_error:
                    print(f"❌ Refresh failed: {refresh_error}")
                    print("   This usually means the refresh token itself is invalid.")
                    print("   Manual re-authentication required.")
                    return False
            else:
                print("❌ Token invalid and cannot be refreshed.")
                print("   Manual re-authentication required.")
                return False
        else:
            print("✅ Token is healthy and valid!")
            return True

    except Exception as e:
        print(f"❌ Error checking token: {e}")
        return False


if __name__ == "__main__":
    success = check_and_refresh_token()
    sys.exit(0 if success else 1)
