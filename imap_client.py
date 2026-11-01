import os
from dotenv import load_dotenv
from imap_tools import MailBox, AND

from cleaner import clean_body

load_dotenv()

IMAP_HOST = "imap.gmail.com"


def _credentials():
    user = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not user or not password:
        raise RuntimeError("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your .env file")
    return user, password


def fetch_emails(limit: int = 100, folder: str = "INBOX") -> list[dict]:
    """Fetch the newest `limit` emails without marking them as read."""
    user, password = _credentials()
    emails = []
    with MailBox(IMAP_HOST).login(user, password, initial_folder=folder) as mb:
        for msg in mb.fetch(AND(all=True), limit=limit, reverse=True, mark_seen=False, bulk=True):
            try:
                ts = int(msg.date.timestamp())
            except Exception:
                ts = 0
            emails.append(
                {
                    "id": f"{folder}-{msg.uid}",
                    "sender": msg.from_ or "",
                    "subject": msg.subject or "(no subject)",
                    "date": msg.date.strftime("%Y-%m-%d %H:%M") if ts else "unknown",
                    "date_ts": ts,
                    "body": clean_body(msg.text, msg.html),
                }
            )
    return emails
def mailbox_counts(folder: str = "INBOX") -> dict:
    user, password = _credentials()
    with MailBox(IMAP_HOST).login(user, password, initial_folder=folder) as mb:
        s = mb.folder.status(folder)
    return {"total": s.get("MESSAGES", 0), "unread": s.get("UNSEEN", 0)}


if __name__ == "__main__":
    for e in fetch_emails(limit=5):
        print(e["date"], "|", e["sender"], "|", e["subject"])