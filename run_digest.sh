#!/bin/bash
echo "=== Digest job started at $(date) ===" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
cd /Users/Kevin/Documents/claude/daily-digest

# Step 1: Check authentication health
echo "" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
echo "Checking authentication health..." >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
/Users/Kevin/Documents/claude/daily-digest/venv/bin/python /Users/Kevin/Documents/claude/daily-digest/check_auth.py >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log 2>&1
AUTH_STATUS=$?

if [ $AUTH_STATUS -ne 0 ]; then
    echo "❌ Authentication check failed! Digest not sent." >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
    echo "   Manual re-authentication required." >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
    echo "   Run: cd /Users/Kevin/Documents/claude/daily-digest && source venv/bin/activate && python -c \"from email_sender import EmailSender; EmailSender().authenticate()\"" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
    echo "=== Digest job ended at $(date), exit code: $AUTH_STATUS (AUTH FAILED) ===" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
    exit $AUTH_STATUS
fi

# Step 2: Run digest (only if auth is healthy)
echo "" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
echo "✅ Authentication healthy, proceeding with digest..." >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
/Users/Kevin/Documents/claude/daily-digest/venv/bin/python /Users/Kevin/Documents/claude/daily-digest/generate_preview.py --send >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log 2>&1
DIGEST_STATUS=$?

echo "=== Digest job ended at $(date), exit code: $DIGEST_STATUS ===" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
exit $DIGEST_STATUS
