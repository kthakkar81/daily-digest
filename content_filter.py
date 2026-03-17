"""AI-powered content categorization and summarization using Claude"""
import anthropic
from config import ANTHROPIC_API_KEY, CATEGORIES, MAX_ITEMS_PER_CATEGORY

class ContentFilter:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.categories = {cat: [] for cat in CATEGORIES}

    def categorize_and_summarize(self, emails):
        """Categorize emails and create summaries using Claude"""
        print(f"\n🤖 Using AI to categorize {len(emails)} items...")
        print(f"   Categories: {', '.join(CATEGORIES)}")
        print()

        for i, email in enumerate(emails, 1):
            print(f"   Processing {i}/{len(emails)}: {email['subject'][:50]}...")

            try:
                # Get category and summary from Claude
                result = self._analyze_email(email)

                if result['category'] and result['category'] in self.categories:
                    self.categories[result['category']].append({
                        'subject': email['subject'],
                        'sender': email['sender'],
                        'date': email['date'],
                        'summary': result['summary'],
                        'relevance_score': result['relevance_score'],
                        'key_insights': result['key_insights']
                    })
                    print(f"      → {result['category']} (score: {result['relevance_score']}/10)")

            except Exception as e:
                print(f"      ✗ Error: {str(e)}")
                continue

        # Sort each category by relevance score
        for category in self.categories:
            self.categories[category].sort(
                key=lambda x: x['relevance_score'],
                reverse=True
            )

        # Keep only top N items per category
        for category in self.categories:
            self.categories[category] = self.categories[category][:MAX_ITEMS_PER_CATEGORY]

        return self.categories

    def _analyze_email(self, email):
        """Use Claude to analyze and categorize an email"""
        prompt = f"""Analyze this email/newsletter and categorize it into ONE of these categories:
{', '.join(CATEGORIES)}

Email Details:
Subject: {email['subject']}
From: {email['sender']}
Content: {email['body'][:2000]}

Tasks:
1. Determine which ONE category fits best (or "None" if it doesn't fit any)
2. Rate relevance from 1-10 for that category
3. Write a 2-sentence summary of key points
4. Extract 2-3 key insights or takeaways

Respond in this exact format:
CATEGORY: [category name or None]
RELEVANCE: [1-10]
SUMMARY: [2 sentences]
INSIGHTS:
- [insight 1]
- [insight 2]
- [insight 3]"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        return self._parse_response(response_text)

    def _parse_response(self, response):
        """Parse Claude's response into structured data"""
        lines = response.strip().split('\n')

        category = None
        relevance_score = 0
        summary = ""
        insights = []

        for i, line in enumerate(lines):
            line = line.strip()

            if line.startswith('CATEGORY:'):
                cat = line.replace('CATEGORY:', '').strip()
                category = cat if cat != 'None' else None

            elif line.startswith('RELEVANCE:'):
                try:
                    relevance_score = int(line.replace('RELEVANCE:', '').strip())
                except:
                    relevance_score = 5

            elif line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()

            elif line.startswith('INSIGHTS:'):
                # Collect all bullet points after INSIGHTS:
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith('-'):
                        insights.append(lines[j].strip()[1:].strip())

        return {
            'category': category,
            'relevance_score': relevance_score,
            'summary': summary,
            'key_insights': insights
        }

    def get_summary_stats(self):
        """Get summary statistics"""
        stats = {}
        total_items = 0

        for category, items in self.categories.items():
            count = len(items)
            stats[category] = count
            total_items += count

        return stats, total_items


if __name__ == "__main__":
    # Test with mock data
    print("Content Filter module loaded successfully!")
    print(f"Categories: {CATEGORIES}")
    print(f"Max items per category: {MAX_ITEMS_PER_CATEGORY}")
