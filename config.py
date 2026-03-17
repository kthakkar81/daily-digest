"""Configuration settings for Daily Digest"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email accounts
YAHOO_EMAIL = os.getenv('YAHOO_EMAIL')
YAHOO_PASSWORD = os.getenv('YAHOO_PASSWORD')

# Claude API
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Email delivery
SEND_FROM_EMAIL = os.getenv('SEND_FROM_EMAIL')
SEND_TO_EMAIL = os.getenv('SEND_TO_EMAIL')
DIGEST_SEND_TIME = os.getenv('DIGEST_SEND_TIME', '07:00')

# Content settings
DAYS_TO_SCAN = int(os.getenv('DAYS_TO_SCAN', 1))
MAX_ITEMS_PER_CATEGORY = int(os.getenv('MAX_ITEMS_PER_CATEGORY', 3))

# Gmail OAuth settings
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_TOKEN_PATH = 'credentials/token.json'
GMAIL_CREDENTIALS_PATH = 'credentials/credentials.json'

# Content categories
CATEGORIES = [
    'AdTech',
    'Fintech',
    'Investing',
    'Parenting',
    'Mental Health',
    'Product Management'
]

# Email filters - what to look for
NEWSLETTER_INDICATORS = [
    'unsubscribe',
    'newsletter',
    'digest',
    'weekly',
    'daily',
    'substack',
    'medium',
    'linkedin'
]
