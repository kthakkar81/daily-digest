"""Fetch top posts from configured subreddits"""
import praw
from datetime import datetime, timedelta
from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    SUBREDDITS,
    DAYS_TO_SCAN
)

class RedditFetcher:
    def __init__(self):
        self.reddit = None
        self._authenticate()

    def _authenticate(self):
        """Connect to Reddit API"""
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            raise Exception("Reddit credentials not found in .env file")

        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            # Test connection
            self.reddit.user.me()
            print(f"✓ Connected to Reddit API")
        except Exception as e:
            # Read-only mode still works without user authentication
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            print(f"✓ Connected to Reddit API (read-only)")

    def fetch_top_posts(self, limit_per_subreddit=10):
        """Fetch top posts from configured subreddits"""
        print(f"📱 Fetching top posts from {len(SUBREDDITS)} subreddit(s)...")

        all_posts = []
        cutoff_time = datetime.now() - timedelta(days=DAYS_TO_SCAN)

        for subreddit_name in SUBREDDITS:
            subreddit_name = subreddit_name.strip()
            try:
                print(f"\n  Scanning r/{subreddit_name}...")
                subreddit = self.reddit.subreddit(subreddit_name)

                # Get hot posts from the last day
                post_count = 0
                for post in subreddit.hot(limit=50):  # Check more to find recent ones
                    post_time = datetime.fromtimestamp(post.created_utc)

                    # Only include posts from the last N days
                    if post_time < cutoff_time:
                        continue

                    # Skip stickied posts (usually rules/megathreads)
                    if post.stickied:
                        continue

                    # Extract post data
                    post_data = {
                        'id': post.id,
                        'subject': f"[r/{subreddit_name}] {post.title}",
                        'sender': f"u/{post.author.name if post.author else '[deleted]'}",
                        'date': post_time,
                        'body': self._format_post_body(post),
                        'url': f"https://reddit.com{post.permalink}",
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'subreddit': subreddit_name
                    }

                    all_posts.append(post_data)
                    post_count += 1
                    print(f"    ✓ {post.title[:60]}... ({post.score}↑, {post.num_comments}💬)")

                    if post_count >= limit_per_subreddit:
                        break

                if post_count == 0:
                    print(f"    No recent posts found")

            except Exception as e:
                print(f"    ✗ Error fetching r/{subreddit_name}: {str(e)}")
                continue

        print(f"\n✅ Found {len(all_posts)} Reddit posts")
        return all_posts

    def _format_post_body(self, post):
        """Format Reddit post body with title, content, and link"""
        body = f"Title: {post.title}\n\n"

        # Add post content if it exists
        if post.selftext:
            # Limit to first 2000 chars to avoid huge posts
            content = post.selftext[:2000]
            if len(post.selftext) > 2000:
                content += "... [truncated]"
            body += f"Content: {content}\n\n"

        # Add metadata
        body += f"Score: {post.score} upvotes | {post.num_comments} comments\n"
        body += f"Link: https://reddit.com{post.permalink}\n"

        # Add flair if exists
        if post.link_flair_text:
            body += f"Flair: {post.link_flair_text}\n"

        return body

    def filter_posts(self, posts, min_score=10):
        """Filter posts by minimum score (upvotes)"""
        print(f"🔍 Filtering Reddit posts (min score: {min_score})...")

        filtered = [p for p in posts if p['score'] >= min_score]

        # Sort by score (highest first)
        filtered.sort(key=lambda x: x['score'], reverse=True)

        print(f"✅ {len(filtered)} posts passed filter")
        return filtered


if __name__ == "__main__":
    # Test the Reddit fetcher
    fetcher = RedditFetcher()
    posts = fetcher.fetch_top_posts(limit_per_subreddit=5)
    filtered = fetcher.filter_posts(posts, min_score=10)

    print("\n" + "="*60)
    print(f"Test complete: {len(filtered)} high-quality posts found")
    print("="*60)

    if filtered:
        print("\nTop post:")
        top = filtered[0]
        print(f"  {top['subject']}")
        print(f"  {top['score']} upvotes | {top['num_comments']} comments")
        print(f"  {top['url']}")
