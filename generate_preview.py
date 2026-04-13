"""Generate a preview of the digest using test results"""
import sys
import subprocess
import traceback
from datetime import datetime
from multi_email_fetcher import MultiEmailFetcher
from content_filter import ContentFilter
from digest_generator import DigestGenerator
from email_sender import EmailSender

def send_error_notification(error_message, error_traceback):
    """Send error notification email when automation fails"""
    try:
        sender = EmailSender()
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        error_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
                h1 {{ color: #d32f2f; }}
                .error-box {{ background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0; }}
                .traceback {{ background-color: #f5f5f5; border: 1px solid #ddd; padding: 15px; margin: 20px 0; font-family: monospace; font-size: 12px; white-space: pre-wrap; overflow-x: auto; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <h1>🚨 Daily Digest Automation Failed</h1>

            <div class="error-box">
                <strong>Error occurred on:</strong> {date_str}
            </div>

            <h2>Error Message:</h2>
            <p><strong>{error_message}</strong></p>

            <h2>Full Traceback:</h2>
            <div class="traceback">{error_traceback}</div>

            <div class="footer">
                <p><strong>Next Steps:</strong></p>
                <ul>
                    <li>Check the error logs: <code>/Users/Kevin/Documents/claude/daily-digest/logs/launchd.err.log</code></li>
                    <li>Test manually: <code>cd /Users/Kevin/Documents/claude/daily-digest && python generate_preview.py --send</code></li>
                    <li>Review Python dependencies if import errors occur</li>
                </ul>
                <p><em>This is an automated error notification from your Daily Digest system.</em></p>
            </div>
        </body>
        </html>
        """

        sender.send_custom_email(
            html_content=error_html,
            subject=f"🚨 Daily Digest Error - {datetime.now().strftime('%B %d, %Y')}"
        )
        print("✅ Error notification email sent")
    except Exception as e:
        print(f"❌ Failed to send error notification: {e}")
        # Don't re-raise - we don't want error notification failures to hide the original error

def main():
    # Check if --send flag is present
    send_email = '--send' in sys.argv

    if send_email:
        print("=" * 60)
        print("Generating and SENDING Daily Digest")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Generating Digest Preview")
        print("=" * 60)
    print()

    # Fetch and categorize from all configured email sources
    print("Fetching newsletters from configured sources...")
    fetcher = MultiEmailFetcher()
    newsletters = fetcher.fetch_all_newsletters(max_results=30)

    if not newsletters:
        print("❌ No newsletters found to process")
        return

    print(f"✅ Found {len(newsletters)} newsletters")
    print()

    # Categorize with AI
    print("Categorizing content with AI...")
    filter_ai = ContentFilter()
    categorized = filter_ai.categorize_and_summarize(newsletters)
    print("✅ Content categorized")
    print()

    # Generate HTML
    print("Generating HTML digest...")
    generator = DigestGenerator(categorized)
    html_content = generator.generate_html()
    print("✅ HTML generated")
    print()

    if send_email:
        # Send via Gmail
        print("Sending digest via Gmail...")
        sender = EmailSender()
        date_str = datetime.now().strftime("%B %d, %Y")

        if sender.send_digest(html_content, date_str):
            print()
            print("=" * 60)
            print("✅ Digest sent successfully!")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("❌ Failed to send digest")
            print("=" * 60)
            # Save to file as backup
            filename = generator.save_to_file('digest_backup.html')
            print(f"Backup saved to: {filename}")
    else:
        # Save and open preview
        filename = generator.save_to_file('digest_preview.html')
        print(f"✅ Preview saved: {filename}")
        print()
        print("Opening in browser...")
        subprocess.run(['open', filename])
        print()
        print("=" * 60)
        print("To send this digest via email, run:")
        print("  python generate_preview.py --send")
        print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()

        print()
        print("=" * 60)
        print("❌ FATAL ERROR")
        print("=" * 60)
        print(f"Error: {error_message}")
        print()
        print("Traceback:")
        print(error_traceback)
        print("=" * 60)

        # Send error notification email (only if --send flag is present)
        if '--send' in sys.argv:
            print()
            print("Sending error notification email...")
            send_error_notification(error_message, error_traceback)

        # Exit with error code so launchd knows it failed
        sys.exit(1)
