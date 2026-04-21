#!/usr/bin/env python3
"""
Health check script that verifies today's digest was sent.
Runs daily at 6:30 AM (after the 6:00 AM digest job).
Only sends notification if digest failed to send.
"""
import os
import sys
from datetime import datetime
from email_sender import EmailSender

def check_digest_sent():
    """Check if today's digest was sent successfully around 6am"""
    sender = EmailSender()
    sender.authenticate()

    # Search for today's digest in sent mail between 5:45am and 6:30am
    # This ensures we only count the automated job, not manual tests
    today = datetime.now().strftime("%Y/%m/%d")
    query = f'subject:"Your Daily Digest" after:{today} from:{sender.from_email} to:{sender.to_email}'

    results = sender.service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        return False

    # Check if any message was sent around 6am (between 5:45am and 6:30am)
    for msg in messages:
        msg_data = sender.service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        for header in msg_data.get('payload', {}).get('headers', []):
            if header['name'] == 'Date':
                # Parse the email date - we expect it between 5:45am and 6:30am
                # If found during this window, consider it the automated job
                # This is a simple check - if digest exists, assume it was automated
                # unless sent after 7am (which would be manual)
                import email.utils
                date_tuple = email.utils.parsedate_tz(header['value'])
                if date_tuple:
                    import time
                    timestamp = email.utils.mktime_tz(date_tuple)
                    msg_time = datetime.fromtimestamp(timestamp)
                    # Accept if between 5:45am and 7:00am (gives 1 hour window)
                    if 5 <= msg_time.hour < 7 or (msg_time.hour == 5 and msg_time.minute >= 45):
                        return True

    return False

def send_failure_notification():
    """Send email notification that digest failed"""
    sender = EmailSender()
    sender.authenticate()

    date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
            h1 {{ color: #d32f2f; }}
            .alert-box {{ background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0; }}
            .steps {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; }}
            code {{ background-color: #e0e0e0; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <h1>⚠️ Daily Digest Failed to Send</h1>

        <div class="alert-box">
            <strong>No digest email found for:</strong> {date_str}
        </div>

        <div class="steps">
            <h2>Troubleshooting Steps:</h2>
            <ol>
                <li>Check error logs:<br>
                    <code>cat /Users/Kevin/documents/claude/daily-digest/logs/launchd.err.log</code>
                </li>
                <li>Test manually:<br>
                    <code>cd /Users/Kevin/documents/claude/daily-digest && venv/bin/python generate_preview.py --send</code>
                </li>
                <li>Check launchd status:<br>
                    <code>launchctl list | grep digest</code>
                </li>
                <li>If import errors, clear Python cache:<br>
                    <code>find /Users/Kevin/documents/claude/daily-digest -name "*.pyc" -delete</code><br>
                    <code>cd /Users/Kevin/documents/claude/daily-digest && venv/bin/pip install --force-reinstall --no-cache-dir pydantic-core</code>
                </li>
            </ol>
        </div>

        <p><em>This is an automated health check from your Daily Digest system.</em></p>
    </body>
    </html>
    """

    subject = "⚠️ Daily Digest Failed to Send"
    sender.send_email(subject, html_body)
    print(f"❌ Digest not found - notification sent at {date_str}")

if __name__ == "__main__":
    os.chdir('/Users/Kevin/documents/claude/daily-digest')

    try:
        if check_digest_sent():
            # Silent success - digest was sent
            sys.exit(0)
        else:
            # Digest not found - send notification
            send_failure_notification()
            sys.exit(1)
    except Exception as e:
        print(f"Health check error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
