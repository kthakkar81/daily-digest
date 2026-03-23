"""Fetch emails from Yahoo Mail using IMAP"""
import email
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from imapclient import IMAPClient
from bs4 import BeautifulSoup
from config import (
    YAHOO_EMAIL,
    YAHOO_PASSWORD,
    DAYS_TO_SCAN,
    NEWSLETTER_INDICATORS,
    EXCLUSION_PATTERNS,
    WHITELISTED_SENDERS
)

class YahooFetcher:
    def __init__(self):
        self.client = None
        self._authenticate()

    def _authenticate(self):
        """Connect to Yahoo Mail via IMAP"""
        if not YAHOO_EMAIL or not YAHOO_PASSWORD:
            raise Exception("Yahoo credentials not found in .env file")

        try:
            # Yahoo IMAP settings
            self.client = IMAPClient('imap.mail.yahoo.com', ssl=True)
            self.client.login(YAHOO_EMAIL, YAHOO_PASSWORD)
            print(f"✓ Connected to Yahoo Mail: {YAHOO_EMAIL}")
        except Exception as e:
            raise Exception(f"Failed to connect to Yahoo Mail: {str(e)}")

    def fetch_recent_emails(self, max_results=50):
        """Fetch recent emails from the last N days"""
        print(f"📧 Fetching emails from Yahoo (last {DAYS_TO_SCAN} day(s))...")

        # Select inbox
        self.client.select_folder('INBOX', readonly=True)

        # Calculate date range
        after_date = datetime.now() - timedelta(days=DAYS_TO_SCAN)

        # Search for emails since the date
        messages = self.client.search(['SINCE', after_date])

        # Limit results
        messages = list(messages)[:max_results]
        print(f"   Found {len(messages)} total emails")

        return messages

    def get_email_content(self, message_id):
        """Get full email content including body"""
        try:
            # Fetch the email
            raw_messages = self.client.fetch([message_id], ['RFC822'])
            raw_email = raw_messages[message_id][b'RFC822']

            # Parse email
            msg = email.message_from_bytes(raw_email)

            # Extract headers
            subject = msg['subject'] or 'No Subject'
            sender = msg['from'] or 'Unknown'
            date_str = msg['date']

            # Parse date
            try:
                email_date = parsedate_to_datetime(date_str) if date_str else datetime.now()
            except:
                email_date = datetime.now()

            # Extract body
            body = self._extract_body(msg)

            return {
                'id': str(message_id),
                'subject': subject,
                'sender': sender,
                'date': email_date,
                'body': body
            }
        except Exception as e:
            print(f"   ✗ Error fetching email {message_id}: {str(e)}")
            return None

    def _extract_body(self, msg):
        """Extract email body from message, preferring HTML with more content"""
        text_parts = []

        # Walk through all parts of the email
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()

                try:
                    if content_type == 'text/plain':
                        text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        text_parts.append(('plain', text, len(text)))
                    elif content_type == 'text/html':
                        html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        text = self._html_to_text(html)
                        text_parts.append(('html', text, len(text)))
                except Exception as e:
                    continue
        else:
            # Single part message
            content_type = msg.get_content_type()
            try:
                if content_type == 'text/html':
                    html = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    text = self._html_to_text(html)
                    text_parts.append(('html', text, len(text)))
                elif content_type == 'text/plain':
                    text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    text_parts.append(('plain', text, len(text)))
            except Exception as e:
                pass

        # Return the longest text part (usually HTML has more content than plain)
        if text_parts:
            text_parts.sort(key=lambda x: x[2], reverse=True)
            return text_parts[0][1]

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

        for msg_id in messages:
            try:
                email_data = self.get_email_content(msg_id)

                if not email_data:
                    continue

                # Skip if no body content
                if not email_data['body'] or len(email_data['body']) < 100:
                    continue

                # Check if it's a newsletter
                if self.is_newsletter(email_data):
                    newsletters.append(email_data)
                    print(f"   ✓ {email_data['subject'][:60]}")

            except Exception as e:
                print(f"   ✗ Error processing email: {str(e)}")
                continue

        print(f"\n✅ Found {len(newsletters)} newsletters/articles from Yahoo")
        return newsletters

    def close(self):
        """Close IMAP connection"""
        if self.client:
            try:
                self.client.logout()
            except:
                pass


if __name__ == "__main__":
    # Test the Yahoo fetcher
    fetcher = YahooFetcher()
    messages = fetcher.fetch_recent_emails(max_results=20)
    newsletters = fetcher.filter_newsletters(messages)
    fetcher.close()

    print("\n" + "="*60)
    print(f"Test complete: {len(newsletters)} newsletters found")
    print("="*60)
