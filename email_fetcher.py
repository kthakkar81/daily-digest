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
    EXCLUSION_PATTERNS,
    WHITELISTED_SENDERS,
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
        """Extract email body from payload, preferring HTML with more content"""
        # Collect all text parts (both plain and HTML)
        text_parts = []

        def extract_parts(payload_part):
            """Recursively extract all text/plain and text/html parts"""
            if 'parts' in payload_part:
                for part in payload_part['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        text_parts.append(('plain', text, len(text)))
                    elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        text = self._html_to_text(html)
                        text_parts.append(('html', text, len(text)))
                    elif 'parts' in part:
                        # Recursively check nested parts (e.g., multipart/related)
                        extract_parts(part)
            else:
                # Single part message
                if 'data' in payload_part.get('body', {}):
                    data = payload_part['body']['data']
                    if payload_part['mimeType'] == 'text/html':
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                        text = self._html_to_text(html)
                        text_parts.append(('html', text, len(text)))
                    elif payload_part['mimeType'] == 'text/plain':
                        text = base64.urlsafe_b64decode(data).decode('utf-8')
                        text_parts.append(('plain', text, len(text)))

        extract_parts(payload)

        # Return the longest text part (usually HTML has more content than plain)
        if text_parts:
            text_parts.sort(key=lambda x: x[2], reverse=True)  # Sort by length
            return text_parts[0][1]  # Return the longest text

        return ""

    def _html_to_text(self, html):
        """Convert HTML to plain text, preserving article links"""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract all links BEFORE converting to text
        links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text().strip()
            url = link['href']
            if url and url.startswith('http'):  # Only external links
                links.append(f"[{link_text}]({url})")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        # Append links at the end if any found
        if links:
            text += "\n\nArticle Links:\n" + "\n".join(links)

        return text

    def is_newsletter(self, email):
        """Check if email looks like a newsletter"""
        subject_lower = email['subject'].lower()
        sender_lower = email['sender'].lower()
        body_lower = email['body'][:1000].lower()  # Check first 1000 chars

        # First check exclusion patterns (FOMO marketing, etc.)
        for pattern in EXCLUSION_PATTERNS:
            if pattern.lower() in subject_lower or pattern.lower() in body_lower:
                return False

        # Check whitelisted senders (always include)
        for sender in WHITELISTED_SENDERS:
            if sender.lower() in sender_lower:
                return True

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
                    # Keep full body (links are at the end) - Claude will get first 5000 chars
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
