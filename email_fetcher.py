"""Fetch and filter emails from Gmail"""
import os
import pickle
import base64
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from config import (
    GMAIL_TOKEN_PATH,
    DAYS_TO_SCAN,
    NEWSLETTER_INDICATORS,
    CATEGORIES
)

class EmailFetcher:
    def __init__(self):
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Load saved Gmail credentials"""
        if not os.path.exists(GMAIL_TOKEN_PATH):
            raise Exception("Gmail token not found. Run gmail_setup.py first.")

        with open(GMAIL_TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

        self.service = build('gmail', 'v1', credentials=creds)

    def fetch_recent_emails(self, max_results=50):
        """Fetch recent emails from the last N days"""
        print(f"📧 Fetching emails from last {DAYS_TO_SCAN} day(s)...")

        # Calculate date range
        after_date = datetime.now() - timedelta(days=DAYS_TO_SCAN)
        query = f'after:{after_date.strftime("%Y/%m/%d")}'

        # Fetch message list
        results = self.service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()

        messages = results.get('messages', [])
        print(f"   Found {len(messages)} total emails")

        return messages

    def get_email_content(self, message_id):
        """Get full email content including body"""
        message = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        headers = message['payload']['headers']

        # Extract headers
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), None)

        # Parse date
        email_date = parsedate_to_datetime(date) if date else datetime.now()

        # Extract body
        body = self._extract_body(message['payload'])

        return {
            'id': message_id,
            'subject': subject,
            'sender': sender,
            'date': email_date,
            'body': body
        }

    def _extract_body(self, payload):
        """Extract email body from payload"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        body = self._html_to_text(html)
                        break
                elif 'parts' in part:
                    body = self._extract_body(part)
                    if body:
                        break
        else:
            if 'data' in payload.get('body', {}):
                data = payload['body']['data']
                if payload['mimeType'] == 'text/html':
                    html = base64.urlsafe_b64decode(data).decode('utf-8')
                    body = self._html_to_text(html)
                else:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body

    def _html_to_text(self, html):
        """Convert HTML to plain text"""
        soup = BeautifulSoup(html, 'lxml')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text

    def is_newsletter(self, email):
        """Check if email looks like a newsletter"""
        subject_lower = email['subject'].lower()
        body_lower = email['body'][:1000].lower()  # Check first 1000 chars

        # Check for newsletter indicators
        for indicator in NEWSLETTER_INDICATORS:
            if indicator in subject_lower or indicator in body_lower:
                return True

        return False

    def filter_newsletters(self, messages):
        """Filter messages to only include newsletters and relevant content"""
        print("🔍 Filtering for newsletters and relevant content...")

        newsletters = []

        for msg in messages:
            try:
                email = self.get_email_content(msg['id'])

                # Skip if no body content
                if not email['body'] or len(email['body']) < 100:
                    continue

                # Check if it's a newsletter
                if self.is_newsletter(email):
                    # Truncate body to first 3000 characters for processing
                    email['body'] = email['body'][:3000]
                    newsletters.append(email)
                    print(f"   ✓ {email['subject'][:60]}")

            except Exception as e:
                print(f"   ✗ Error processing email: {str(e)}")
                continue

        print(f"\n✅ Found {len(newsletters)} newsletters/articles")
        return newsletters


if __name__ == "__main__":
    # Test the email fetcher
    fetcher = EmailFetcher()
    messages = fetcher.fetch_recent_emails(max_results=20)
    newsletters = fetcher.filter_newsletters(messages)

    print("\n" + "="*60)
    print(f"Test complete: {len(newsletters)} newsletters found")
    print("="*60)
