"""Unified email fetcher supporting multiple email providers"""
from email_fetcher import EmailFetcher
from yahoo_fetcher import YahooFetcher
from config import EMAIL_SOURCES

class MultiEmailFetcher:
    """Fetches emails from multiple sources (Gmail, Yahoo, etc.)"""

    def __init__(self):
        self.fetchers = []
        self._initialize_fetchers()

    def _initialize_fetchers(self):
        """Initialize fetchers based on EMAIL_SOURCES config"""
        for source in EMAIL_SOURCES:
            source = source.strip()
            try:
                if source == 'gmail':
                    self.fetchers.append(('Gmail', EmailFetcher()))
                    print("✓ Gmail fetcher initialized")
                elif source == 'yahoo':
                    self.fetchers.append(('Yahoo', YahooFetcher()))
                    print("✓ Yahoo fetcher initialized")
                else:
                    print(f"⚠ Unknown email source: {source}")
            except Exception as e:
                print(f"✗ Failed to initialize {source}: {str(e)}")

        if not self.fetchers:
            raise Exception("No email fetchers initialized. Check your configuration.")

    def fetch_all_newsletters(self, max_results=50):
        """Fetch newsletters from all configured email sources"""
        all_newsletters = []

        for source_name, fetcher in self.fetchers:
            try:
                print(f"\n{'='*60}")
                print(f"Fetching from {source_name}")
                print('='*60)

                # Fetch messages
                messages = fetcher.fetch_recent_emails(max_results=max_results)

                # Filter for newsletters
                newsletters = fetcher.filter_newsletters(messages)
                all_newsletters.extend(newsletters)

            except Exception as e:
                print(f"✗ Error fetching from {source_name}: {str(e)}")
                continue

        print(f"\n{'='*60}")
        print(f"Total newsletters from all sources: {len(all_newsletters)}")
        print('='*60)

        return all_newsletters

    def close_all(self):
        """Close all fetcher connections"""
        for source_name, fetcher in self.fetchers:
            try:
                if hasattr(fetcher, 'close'):
                    fetcher.close()
            except:
                pass


if __name__ == "__main__":
    # Test the multi fetcher
    fetcher = MultiEmailFetcher()
    newsletters = fetcher.fetch_all_newsletters(max_results=20)
    fetcher.close_all()

    print("\n" + "="*60)
    print(f"Test complete: {len(newsletters)} total newsletters found")
    print("="*60)
