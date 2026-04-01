#!/bin/bash

# Daily Digest Automation Script
# This script runs the daily digest and sends via email

# Log start time
echo "==================================================" >> /Users/Kevin/Documents/claude/daily-digest/logs/automation.log
echo "Daily Digest Started: $(date)" >> /Users/Kevin/Documents/claude/daily-digest/logs/automation.log
echo "==================================================" >> /Users/Kevin/Documents/claude/daily-digest/logs/automation.log

# Set working directory
cd /Users/Kevin/Documents/claude/daily-digest || exit 1

# Run using venv python directly
/Users/Kevin/Documents/claude/daily-digest/venv/bin/python \
    /Users/Kevin/Documents/claude/daily-digest/generate_preview.py \
    --send \
    >> /Users/Kevin/Documents/claude/daily-digest/logs/automation.log 2>&1

# Log completion
echo "Completed: $(date)" >> /Users/Kevin/Documents/claude/daily-digest/logs/automation.log
echo "" >> /Users/Kevin/Documents/claude/daily-digest/logs/automation.log

exit 0
