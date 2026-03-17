"""Generate a preview of the digest using test results"""
from email_fetcher import EmailFetcher
from content_filter import ContentFilter
from digest_generator import DigestGenerator

def main():
    print("Generating digest preview...")
    print()

    # Fetch and categorize
    fetcher = EmailFetcher()
    messages = fetcher.fetch_recent_emails(max_results=30)
    newsletters = fetcher.filter_newsletters(messages)

    if newsletters:
        filter_ai = ContentFilter()
        categorized = filter_ai.categorize_and_summarize(newsletters)

        # Generate HTML
        generator = DigestGenerator(categorized)
        filename = generator.save_to_file('digest_preview.html')

        print(f"\n✅ Preview generated: {filename}")
        print("\nOpening in browser...")

        import subprocess
        subprocess.run(['open', filename])
    else:
        print("No newsletters found to preview")

if __name__ == "__main__":
    main()
