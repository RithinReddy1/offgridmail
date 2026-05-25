import os
import base64
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Literal, List, Optional
from ollama import chat
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class EmailAnalysis(BaseModel):
    category: Literal["urgent", "action_required", "newsletter", "informational"]
    priority: Literal["high", "medium", "low"]
    summary: str
    is_urgent: bool
    suggested_reply: Optional[str]
    action_items: List[str]

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(service, max_results=20):  # ← now 20!
    results = service.users().messages().list(
        userId='me', labelIds=['INBOX'], q='is:unread', maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        full = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = full['payload']
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}
        body = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
        else:
            data = payload['body'].get('data', '')
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        emails.append({
            'id': msg['id'],
            'from': headers.get('From', ''),
            'subject': headers.get('Subject', ''),
            'body': body[:2000]
        })
    return emails

def analyze_email(email: dict) -> EmailAnalysis:
    prompt = f"""
You are an email assistant. Analyze this email and return a structured analysis.
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}
Be concise. Only suggest a reply if the email clearly needs one.
"""
    response = chat(
        model='llama3.2',
        format=EmailAnalysis.model_json_schema(),
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0}
    )
    return EmailAnalysis.model_validate_json(response.message.content)

def flag_urgent_in_gmail(service, email_id: str):
    service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'addLabelIds': ['STARRED']}
    ).execute()

def save_to_log(email: dict, analysis: EmailAnalysis):  # ← NEW: saves to file
    with open('email_log.txt', 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Time     : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"From     : {email['from']}\n")
        f.write(f"Subject  : {email['subject']}\n")
        f.write(f"Category : {analysis.category}\n")
        f.write(f"Priority : {analysis.priority}\n")
        f.write(f"Summary  : {analysis.summary}\n")
        f.write(f"Urgent   : {'YES' if analysis.is_urgent else 'No'}\n")
        if analysis.action_items:
            f.write(f"Actions  : {', '.join(analysis.action_items)}\n")
        if analysis.suggested_reply:
            f.write(f"Reply    : {analysis.suggested_reply}\n")

def main():
    print(f"🔒 Running at {datetime.now().strftime('%H:%M:%S')} — 100% local AI\n")
    service = get_gmail_service()
    emails = get_unread_emails(service, max_results=20)

    if not emails:
        print("No unread emails found.")
        return

    for email in emails:
        print(f"📧 Analyzing: {email['subject']}")
        analysis = analyze_email(email)

        print(f"   Category : {analysis.category}")
        print(f"   Priority : {analysis.priority}")
        print(f"   Summary  : {analysis.summary}")
        print(f"   Urgent?  : {'🚨 YES' if analysis.is_urgent else 'No'}")

        if analysis.action_items:
            print(f"   Actions  : {', '.join(analysis.action_items)}")
        if analysis.suggested_reply:
            print(f"   Draft    : {analysis.suggested_reply}")

        if analysis.is_urgent:
            flag_urgent_in_gmail(service, email['id'])
            print("   ⭐ Flagged in Gmail!")

        save_to_log(email, analysis)  # ← saves every email
        print()

    print("✅ Done! Log saved to email_log.txt")

if __name__ == '__main__':
    main()
import json
from pydantic import BaseModel
from typing import Literal, List, Optional
from ollama import chat
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── 1. PYDANTIC MODEL (the structured output schema) ──────────────
class EmailAnalysis(BaseModel):
    category: Literal["urgent", "action_required", "newsletter", "informational"]
    priority: Literal["high", "medium", "low"]
    summary: str                        # 1-sentence summary
    is_urgent: bool                     # True = needs immediate attention
    suggested_reply: Optional[str]      # None if no reply needed
    action_items: List[str]             # e.g. ["Reply by Friday", "Attach invoice"]

# ── 2. GMAIL CONNECTION ───────────────────────────────────────────
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(service, max_results=5):
    results = service.users().messages().list(
        userId='me', labelIds=['INBOX'], q='is:unread', maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        full = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = full['payload']
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}
        # Extract body
        body = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
        else:
            data = payload['body'].get('data', '')
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        emails.append({
            'id': msg['id'],
            'from': headers.get('From', ''),
            'subject': headers.get('Subject', ''),
            'body': body[:2000]  # limit to 2000 chars
        })
    return emails

# ── 3. ANALYZE EMAIL WITH LLAMA 3.2 ──────────────────────────────
def analyze_email(email: dict) -> EmailAnalysis:
    prompt = f"""
You are an email assistant. Analyze this email and return a structured analysis.

From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Be concise. Only suggest a reply if the email clearly needs one.
"""
    response = chat(
        model='llama3.2',
        format=EmailAnalysis.model_json_schema(),
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0}
    )
    return EmailAnalysis.model_validate_json(response.message.content)

# ── 4. LABEL URGENT EMAILS IN GMAIL ──────────────────────────────
def flag_urgent_in_gmail(service, email_id: str):
    # Add a STARRED label to urgent emails
    service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'addLabelIds': ['STARRED']}
    ).execute()

# ── 5. MAIN LOOP ──────────────────────────────────────────────────
def main():
    print("🔒 Connecting to Gmail (100% local AI processing)...\n")
    service = get_gmail_service()
    emails = get_unread_emails(service, max_results=5)

    if not emails:
        print("No unread emails found.")
        return

    for email in emails:
        print(f"📧 Analyzing: {email['subject']}")
        analysis = analyze_email(email)

        print(f"   Category  : {analysis.category}")
        print(f"   Priority  : {analysis.priority}")
        print(f"   Summary   : {analysis.summary}")
        print(f"   Urgent?   : {'🚨 YES' if analysis.is_urgent else 'No'}")

        if analysis.action_items:
            print(f"   Actions   : {', '.join(analysis.action_items)}")

        if analysis.suggested_reply:
            print(f"   Draft Reply:\n   ---\n   {analysis.suggested_reply}\n   ---")

        if analysis.is_urgent:
            flag_urgent_in_gmail(service, email['id'])
            print("   ⭐ Flagged as urgent in Gmail!")

        print()

if __name__ == '__main__':
    main()
