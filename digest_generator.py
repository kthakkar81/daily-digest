"""Generate HTML email digest from categorized content"""
from datetime import datetime
from config import CATEGORIES

class DigestGenerator:
    def __init__(self, categorized_content):
        self.content = categorized_content
        self.date = datetime.now().strftime('%B %d, %Y')

    def generate_html(self):
        """Generate HTML email digest"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #0066cc;
            margin: 0;
            font-size: 28px;
        }}
        .date {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .category {{
            margin-bottom: 40px;
        }}
        .category-title {{
            background-color: #0066cc;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        .item {{
            border-left: 3px solid #e0e0e0;
            padding-left: 15px;
            margin-bottom: 25px;
        }}
        .item-title {{
            color: #0066cc;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .item-meta {{
            color: #888;
            font-size: 13px;
            margin-bottom: 10px;
        }}
        .score {{
            background-color: #0066cc;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
        }}
        .summary {{
            color: #444;
            font-size: 14px;
            margin-bottom: 12px;
            line-height: 1.5;
        }}
        .insights {{
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .insights-title {{
            font-weight: 600;
            color: #555;
            margin-bottom: 8px;
        }}
        .insights ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .insights li {{
            color: #666;
            margin-bottom: 5px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #888;
            font-size: 12px;
        }}
        .empty-category {{
            color: #999;
            font-style: italic;
            padding: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📬 Your Daily Digest</h1>
            <div class="date">{self.date}</div>
        </div>
"""

        # Add each category
        total_items = 0
        for category in CATEGORIES:
            items = self.content.get(category, [])
            if not items:
                continue

            total_items += len(items)
            html += f"""
        <div class="category">
            <div class="category-title">📂 {category}</div>
"""

            for i, item in enumerate(items, 1):
                insights_html = ""
                if item.get('key_insights'):
                    insights_list = "\n".join([f"                    <li>{insight}</li>"
                                              for insight in item['key_insights']])
                    insights_html = f"""
            <div class="insights">
                <div class="insights-title">Key Insights:</div>
                <ul>
{insights_list}
                </ul>
            </div>"""

                html += f"""
            <div class="item">
                <div class="item-title">{item['subject']}</div>
                <div class="item-meta">
                    From: {item['sender'].split('<')[0].strip()} |
                    <span class="score">Score: {item['relevance_score']}/10</span>
                </div>
                <div class="summary">{item['summary']}</div>
{insights_html}
            </div>
"""

            html += """
        </div>
"""

        # If no items found
        if total_items == 0:
            html += """
        <div class="empty-category">
            No new content found today matching your interests. Check back tomorrow!
        </div>
"""

        # Footer
        html += f"""
        <div class="footer">
            <p>Generated by Daily Digest AI | {total_items} item(s) curated for you</p>
            <p>Categories: {', '.join(CATEGORIES)}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def save_to_file(self, filename='digest_preview.html'):
        """Save HTML to file for preview"""
        html = self.generate_html()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        return filename


if __name__ == "__main__":
    print("Digest Generator module loaded successfully!")
