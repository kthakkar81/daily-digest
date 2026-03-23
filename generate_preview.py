"""Generate a preview of the digest using test results"""
from multi_email_fetcher import MultiEmailFetcher
from content_filter import ContentFilter
from digest_generator import DigestGenerator

def main():
    print("Generating digest preview...")
    print()

    # Fetch and categorize from all configured email sources
    fetcher = MultiEmailFetcher()
    newsletters = fetcher.fetch_all_newsletters(max_results=30)

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
