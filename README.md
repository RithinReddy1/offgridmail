# 🔒 OffGridMail

### Privacy:First Email AI , 100% Local, Zero Cloud

> Your emails stay on your machine. Always.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-green)
![Llama](https://img.shields.io/badge/Llama-3.2-orange)
![License](https://img.shields.io/badge/License-MIT-purple)
![Cost](https://img.shields.io/badge/Cost-$0-brightgreen)

-----

## 🤔 Why I Built This

Every AI email tool sends your emails to someone else’s server.
Someone else’s computer reads them.
Someone else decides what’s private.

I wanted something different. So I built OffGridMail.

-----

## ✨ What It Does

- 📧 Reads your Gmail inbox every day at 8am automatically
- 🏷️ Categorizes emails : urgent / newsletter / action required
- ⚡ Assigns priority : high / medium / low
- ✍️ Drafts suggested replies
- ⭐ Flags urgent emails directly in Gmail
- 📝 Saves a full analysis log to your computer
- 🔒 100% local : no cloud, no API keys, no subscriptions

-----

## 🏗️ Tech Stack

|Tool        |Role                         |
|------------|-----------------------------|
|Llama 3.2   |Local AI model               |
|Ollama      |Runs AI on your machine      |
|Pydantic    |Structured output enforcement|
|Gmail API   |Fetches your emails          |
|Python 3.11+|Core language                |

-----

## 🚀 Quick Start

### 1. Install Ollama & Llama 3.2

```bash
# Download Ollama from ollama.com then:
ollama pull llama3.2
```

### 2. Clone this repo

```bash
git clone https://github.com/RithinReddy1/offgridmail.git
cd offgridmail
```

### 3. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install ollama pydantic google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 4. Set up Gmail API

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
1. Create a new project
1. Enable the Gmail API
1. Create OAuth credentials → Desktop App
1. Download `credentials.json` → place in project folder

### 5. Run it!

```bash
python3 email_ai.py
```

-----

## 📊 Example Output

```
🔒 Running at 08:00:00 — 100% local AI

📧 Invoice Due Tomorrow
   Category : urgent
   Priority : high
   Urgent?  : 🚨 YES
   ⭐ Flagged in Gmail!

📧 Weekly Newsletter
   Category : newsletter
   Priority : low
   Urgent?  : No

✅ Done! Log saved to email_log.txt
```

-----

## ⏰ Auto-Run Daily at 8am

```bash
crontab -e
```

Add this line:

```
0 8 * * * cd /Users/YOUR_NAME/offgridmail && source venv/bin/activate && python3 email_ai.py >> email_log.txt 2>&1
```

-----

## 🔒 Privacy Guarantee

```
Gmail → Your Machine → Ollama → Llama 3.2 → Your Log
```

- ✅ Zero data sent to any AI cloud
- ✅ Runs completely offline after Gmail fetch
- ✅ Open source — read every line

-----

## 🛠️ Useful Commands

```bash
# Run manually
python3 email_ai.py

# View today's log
tail -20 email_log.txt

# Check schedule
crontab -l
```

-----

## 👤 Author

Built by **Rithin Reddy** — with curiosity and zero cloud dependencies.

⭐ Star this repo if it helped you!

🔗 [LinkedIn](https://linkedin.com/in/yourprofile)
