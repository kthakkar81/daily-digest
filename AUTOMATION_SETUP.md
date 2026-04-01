# Daily Digest Automation Setup

## ✅ Current Status

Your daily digest is **configured to run at 7:00 AM daily** via cron.

## 🔧 Fix macOS Permission Issue (Required)

Modern macOS requires **Full Disk Access** for cron to access your files.

### Steps to Enable:

1. **Open System Settings** → Privacy & Security → Full Disk Access
2. Click the **Lock icon** (bottom left) and authenticate
3. Click the **+** button
4. Press **Cmd + Shift + G** and enter: `/usr/sbin/cron`
5. Click **Open**
6. **Lock** the settings again

**After enabling:** Cron will be able to run your digest at 7am daily.

---

## 📋 Manual Commands

### Send Digest Now
```bash
cd /Users/Kevin/Documents/claude/daily-digest
python generate_preview.py --send
```

### Preview Without Sending (opens in browser)
```bash
cd /Users/Kevin/Documents/claude/daily-digest
python generate_preview.py
```

---

## 📊 Check Automation Status

### View cron schedule
```bash
crontab -l
```

### Check recent logs
```bash
tail -50 ~/Documents/claude/daily-digest/logs/cron.log
```

### Test cron manually
```bash
# Run the exact command cron will run
/Users/Kevin/Documents/claude/daily-digest/venv/bin/python \
  /Users/Kevin/Documents/claude/daily-digest/generate_preview.py --send
```

---

## 🔄 Manage Cron Job

### Disable automation
```bash
crontab -r
```

### Re-enable automation (7am daily)
```bash
echo "0 7 * * * /Users/Kevin/Documents/claude/daily-digest/venv/bin/python /Users/Kevin/Documents/claude/daily-digest/generate_preview.py --send >> /Users/Kevin/Documents/claude/daily-digest/logs/cron.log 2>&1" | crontab -
```

### Change time (example: 8:30 AM)
```bash
echo "30 8 * * * /Users/Kevin/Documents/claude/daily-digest/venv/bin/python /Users/Kevin/Documents/claude/daily-digest/generate_preview.py --send >> /Users/Kevin/Documents/claude/daily-digest/logs/cron.log 2>&1" | crontab -
```

---

## 🎯 What Happens Daily

1. **7:00 AM** - Cron triggers digest
2. **Fetches** emails from Gmail + Yahoo (last 24 hours)
3. **Filters** for newsletters and relevant content
4. **Categorizes** with AI (Claude)
5. **Generates** HTML digest
6. **Sends** to kevin.thakkar@gmail.com via Gmail API

---

## 🐛 Troubleshooting

### No email received?

1. **Check cron log:**
   ```bash
   cat ~/Documents/claude/daily-digest/logs/cron.log
   ```

2. **Check Gmail spam folder**

3. **Verify cron has Full Disk Access** (see above)

4. **Test manually:**
   ```bash
   cd ~/Documents/claude/daily-digest
   python generate_preview.py --send
   ```

### Permission errors?

- **macOS requires Full Disk Access for cron** - see setup steps above
- Alternative: Run manually each morning or use Automator

---

## 📧 Email Configuration

Currently sending from/to: **kevin.thakkar@gmail.com**

To change recipients, edit `.env`:
```bash
SEND_FROM_EMAIL=kevin.thakkar@gmail.com
SEND_TO_EMAIL=different@email.com
```

---

## 🔐 Re-authenticate Gmail (if token expires)

```bash
cd ~/Documents/claude/daily-digest
python gmail_setup.py
```

This will open a browser to re-authorize Gmail access.
