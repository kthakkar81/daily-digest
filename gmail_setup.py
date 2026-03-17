"""Gmail OAuth Setup and Testing Script"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GMAIL_SCOPES, GMAIL_TOKEN_PATH, GMAIL_CREDENTIALS_PATH

def authenticate_gmail():
    """Authenticate with Gmail and save credentials"""
    creds = None

    # Check if we already have valid credentials
    if os.path.exists(GMAIL_TOKEN_PATH):
        with open(GMAIL_TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(GMAIL_CREDENTIALS_PATH):
                print("❌ ERROR: credentials.json not found!")
                print(f"Expected location: {GMAIL_CREDENTIALS_PATH}")
                print("\nPlease follow the setup instructions to download credentials.json")
                return None

            print("Starting OAuth flow...")
            print("A browser window will open for you to authorize the app.")
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS_PATH, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        with open(GMAIL_TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Credentials saved!")

    return creds

def test_gmail_connection():
    """Test Gmail connection by fetching recent emails"""
    print("=" * 60)
    print("Gmail OAuth Setup & Test")
    print("=" * 60)
    print()

    # Authenticate
    creds = authenticate_gmail()
    if not creds:
        return False

    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # Test: Get user profile
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress')
        total_messages = profile.get('messagesTotal', 0)

        print("✅ Successfully connected to Gmail!")
        print(f"   Email: {email}")
        print(f"   Total messages: {total_messages:,}")
        print()

        # Test: Fetch 5 recent emails
        print("Fetching 5 most recent emails...")
        results = service.users().messages().list(
            userId='me',
            maxResults=5,
            q='category:primary OR category:promotions'
        ).execute()

        messages = results.get('messages', [])

        if messages:
            print(f"✅ Found {len(messages)} recent emails:")
            print()

            for i, msg in enumerate(messages, 1):
                # Get message details
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

                print(f"   {i}. {subject[:60]}")
                print(f"      From: {sender[:50]}")
                print()

        print("=" * 60)
        print("✅ Gmail setup complete and working!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Error connecting to Gmail: {str(e)}")
        return False

if __name__ == "__main__":
    test_gmail_connection()
