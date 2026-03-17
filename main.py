"""Main script for Daily Digest AI Content Curator"""
import sys
from datetime import datetime

def main():
    """Run the daily digest pipeline"""
    print("=" * 60)
    print("Daily Digest - AI Content Curator")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # TODO: Phase 1 - Email scanning
    # 1. Connect to Gmail
    # 2. Connect to Yahoo
    # 3. Fetch recent emails
    # 4. Filter for newsletters/content
    # 5. Categorize with AI
    # 6. Generate digest
    # 7. Send email

    print("✅ Project structure created!")
    print("Next steps:")
    print("1. Set up Gmail OAuth credentials")
    print("2. Configure Yahoo IMAP access")
    print("3. Add your API keys to .env file")
    print()

if __name__ == "__main__":
    main()
