"""Test the full pipeline: fetch emails → categorize → display results"""
from email_fetcher import EmailFetcher
from content_filter import ContentFilter
from datetime import datetime

def main():
    print("="*70)
    print("DAILY DIGEST - AI CONTENT CURATOR - TEST RUN")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Fetch emails
    print("STEP 1: Fetching emails from Gmail...")
    print("-"*70)
    fetcher = EmailFetcher()
    messages = fetcher.fetch_recent_emails(max_results=30)  # Get last 30 emails
    newsletters = fetcher.filter_newsletters(messages)

    if not newsletters:
        print("\n❌ No newsletters found. Try increasing the date range or max_results.")
        return

    # Step 2: Categorize with AI
    print("\n" + "="*70)
    print("STEP 2: AI Categorization & Summarization")
    print("-"*70)
    filter_ai = ContentFilter()
    categorized = filter_ai.categorize_and_summarize(newsletters)

    # Step 3: Display results
    print("\n" + "="*70)
    print("STEP 3: Results")
    print("-"*70)

    stats, total = filter_ai.get_summary_stats()

    print(f"\n📊 Summary Statistics:")
    print(f"   Total newsletters processed: {len(newsletters)}")
    print(f"   Total items categorized: {total}")
    print()

    for category, count in stats.items():
        if count > 0:
            print(f"   • {category}: {count} item(s)")

    # Display each category
    print("\n" + "="*70)
    print("CATEGORIZED CONTENT")
    print("="*70)

    for category, items in categorized.items():
        if not items:
            continue

        print(f"\n{'='*70}")
        print(f"📂 {category.upper()}")
        print('='*70)

        for i, item in enumerate(items, 1):
            print(f"\n{i}. {item['subject']}")
            print(f"   From: {item['sender']}")
            print(f"   Score: {item['relevance_score']}/10")
            print(f"\n   Summary:")
            print(f"   {item['summary']}")

            if item['key_insights']:
                print(f"\n   Key Insights:")
                for insight in item['key_insights']:
                    print(f"   • {insight}")

            print("-"*70)

    print("\n" + "="*70)
    print("✅ TEST COMPLETE!")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Review the categorization - does it look accurate?")
    print("2. If good, we'll build the HTML email digest generator")
    print("3. Then set up daily automation")
    print()


if __name__ == "__main__":
    main()
