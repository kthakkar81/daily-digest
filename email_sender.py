"""Send digest emails via Gmail API"""
import os
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GMAIL_SCOPES, GMAIL_TOKEN_PATH, GMAIL_CREDENTIALS_PATH, SEND_FROM_EMAIL, SEND_TO_EMAIL

class EmailSender:
    """Send emails using Gmail API"""

    def __init__(self):
        self.service = None
        self.from_email = SEND_FROM_EMAIL
        self.to_email = SEND_TO_EMAIL

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing credentials
        if os.path.exists(GMAIL_TOKEN_PATH):
            with open(GMAIL_TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing Gmail credentials...")
                creds.refresh(Request())
            else:
                print("Starting OAuth flow for Gmail send permission...")
                print("A browser window will open for authorization.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMAIL_CREDENTIALS_PATH, GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(GMAIL_TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Credentials saved!")

        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def create_message(self, subject, html_body, text_body=None):
        """Create a MIME message for sending

        Args:
            subject: Email subject line
            html_body: HTML content of the email
            text_body: Plain text fallback (optional)

        Returns:
            Base64 encoded message ready for Gmail API
        """
        message = MIMEMultipart('alternative')
        message['To'] = self.to_email
        message['From'] = self.from_email
        message['Subject'] = subject

        # Add plain text version (fallback)
        if text_body:
            text_part = MIMEText(text_body, 'plain')
            message.attach(text_part)

        # Add HTML version
        html_part = MIMEText(html_body, 'html')
        message.attach(html_part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_email(self, subject, html_body, text_body=None):
        """Send an email via Gmail API

        Args:
            subject: Email subject line
            html_body: HTML content
            text_body: Plain text fallback (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.service:
            if not self.authenticate():
                print("❌ Failed to authenticate with Gmail")
                return False

        try:
            message = self.create_message(subject, html_body, text_body)

            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            print(f"✅ Email sent successfully!")
            print(f"   Message ID: {sent_message['id']}")
            print(f"   From: {self.from_email}")
            print(f"   To: {self.to_email}")
            print(f"   Subject: {subject}")

            return True

        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False

    def send_digest(self, html_content, date_str):
        """Send the daily digest email

        Args:
            html_content: The HTML digest content
            date_str: Date string for the subject line (e.g., "March 25, 2026")

        Returns:
            True if sent successfully
        """
        subject = f"📬 Your Daily Digest - {date_str}"
        text_body = f"Your daily digest for {date_str}\n\nPlease view this email in HTML format."

        return self.send_email(subject, html_content, text_body)


def test_send():
    """Test sending a simple email"""
    print("=" * 60)
    print("Testing Gmail Send Functionality")
    print("=" * 60)
    print()

    sender = EmailSender()

    # Simple test email
    html = """
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🎉 Gmail Send Test</h2>
            <p>This is a test email from your Daily Digest app.</p>
            <p>If you're reading this, Gmail send functionality is working!</p>
        </body>
    </html>
    """

    success = sender.send_email(
        subject="Test Email from Daily Digest",
        html_body=html,
        text_body="This is a test email. Please view in HTML format."
    )

    if success:
        print("\n" + "=" * 60)
        print("✅ Test email sent successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Test email failed")
        print("=" * 60)

    return success


if __name__ == "__main__":
    test_send()
