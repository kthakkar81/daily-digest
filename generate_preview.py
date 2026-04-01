"""Generate a preview of the digest using test results"""
import sys
import subprocess
from datetime import datetime
from multi_email_fetcher import MultiEmailFetcher
from content_filter import ContentFilter
from digest_generator import DigestGenerator
from email_sender import EmailSender

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
    main()
