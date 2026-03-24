"""Setup and test Reddit API connection"""
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, SUBREDDITS

def setup_reddit():
    """Guide user through Reddit API setup"""
    print("="*60)
    print("Reddit API Setup")
    print("="*60)
    print()

    # Check credentials
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("❌ Reddit credentials not found in .env file")
        print()
        print("To use Reddit as a content source, you need to:")
        print("1. Go to: https://www.reddit.com/prefs/apps")
        print("2. Click 'create another app' at the bottom")
        print("3. Fill out the form:")
        print("   - Name: Daily Digest")
        print("   - Type: Select 'script'")
        print("   - Redirect URI: http://localhost:8080")
        print("4. Click 'create app'")
        print("5. Copy the credentials:")
        print("   - Client ID: The string under your app name")
        print("   - Client Secret: The 'secret' field")
        print("6. Add to your .env file:")
        print("   REDDIT_CLIENT_ID=your_client_id")
        print("   REDDIT_CLIENT_SECRET=your_client_secret")
        print()
        return False

    print(f"Client ID: {REDDIT_CLIENT_ID[:10]}...")
    print(f"Subreddits: {', '.join(SUBREDDITS)}")
    print()

    try:
        from reddit_fetcher import RedditFetcher

        # Test connection
        print("Testing Reddit API connection...")
        fetcher = RedditFetcher()
        print()

        # Fetch test posts
        print("Fetching sample posts...")
        posts = fetcher.fetch_top_posts(limit_per_subreddit=3)
        print()

        if posts:
            filtered = fetcher.filter_posts(posts, min_score=5)

            if filtered:
                print("\n" + "="*60)
                print("Sample Posts:")
                print("="*60)
                for post in filtered[:3]:
                    print(f"\n📌 {post['subject']}")
                    print(f"   {post['score']} upvotes | {post['num_comments']} comments")
                    print(f"   {post['url']}")

        print()
        print("="*60)
        print("✅ Reddit setup complete!")
        print("="*60)
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("Common issues:")
        print("  • Make sure your Client ID and Secret are correct")
        print("  • Check that the app type is 'script' in Reddit settings")
        print("  • Verify the credentials in your .env file")
        print()
        return False


if __name__ == "__main__":
    setup_reddit()
