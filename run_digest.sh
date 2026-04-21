#!/bin/bash
echo "=== Digest job started at $(date) ===" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
cd /Users/Kevin/Documents/claude/daily-digest
/Users/Kevin/Documents/claude/daily-digest/venv/bin/python /Users/Kevin/Documents/claude/daily-digest/generate_preview.py --send >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log 2>&1
echo "=== Digest job ended at $(date), exit code: $? ===" >> /Users/Kevin/Documents/claude/daily-digest/logs/wrapper.log
