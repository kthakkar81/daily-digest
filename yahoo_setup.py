"""Test Yahoo Mail IMAP connection and setup"""
from yahoo_fetcher import YahooFetcher
from config import YAHOO_EMAIL, YAHOO_PASSWORD

def test_yahoo_connection():
    """Test Yahoo Mail connection"""
    print("="*60)
    print("Yahoo Mail IMAP Setup Test")
    print("="*60)
    print()

    # Check credentials
    if not YAHOO_EMAIL or not YAHOO_PASSWORD:
        print("❌ Yahoo credentials not found in .env file")
        print()
        print("To use Yahoo Mail, you need to:")
        print("1. Add YAHOO_EMAIL and YAHOO_PASSWORD to your .env file")
        print("2. Use an App Password (not your regular password)")
        print()
        print("How to get a Yahoo App Password:")
        print("   1. Go to: https://login.yahoo.com/account/security")
        print("   2. Click 'Generate app password'")
        print("   3. Select 'Other App' and name it (e.g., 'Daily Digest')")
        print("   4. Copy the generated password to .env file")
        print()
        return False

    print(f"Email: {YAHOO_EMAIL}")
    print()

    try:
        # Test connection
        print("Connecting to Yahoo Mail...")
        fetcher = YahooFetcher()
        print("✅ Connection successful!")
        print()

        # Fetch a few test emails
        print("Fetching recent emails...")
        messages = fetcher.fetch_recent_emails(max_results=5)
        print(f"✅ Found {len(messages)} emails")
        print()

        if messages:
            print("Sample emails:")
            newsletters = fetcher.filter_newsletters(messages[:3])

            if newsletters:
                for nl in newsletters[:2]:
                    print(f"\n  • {nl['subject'][:70]}")
                    print(f"    From: {nl['sender'][:50]}")
                    print(f"    Body preview: {nl['body'][:100]}...")

        fetcher.close()

        print()
        print("="*60)
        print("✅ Yahoo Mail setup complete!")
        print("="*60)
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("Common issues:")
        print("  • Make sure you're using an App Password, not your regular password")
        print("  • Check that IMAP is enabled in Yahoo Mail settings")
        print("  • Verify your email and password in the .env file")
        print()
        return False


if __name__ == "__main__":
    test_yahoo_connection()
