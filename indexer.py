import chromadb
from sentence_transformers import SentenceTransformer

from imap_client import fetch_emails

DB_PATH = "./chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=DB_PATH)
col = client.get_or_create_collection("emails", metadata={"hnsw:space": "cosine"})


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    if len(text) <= size:
        return [text]
    step = size - overlap
    return [text[i : i + size] for i in range(0, len(text), step)]


def index_email(e: dict) -> bool:
    """Embed and store one email. Returns False if it was already indexed."""
    if col.get(ids=[f"{e['id']}_0"])["ids"]:
        return False

    header = f"Subject: {e['subject']}\nFrom: {e['sender']}\nDate: {e['date']}\n\n"
    chunks = [header + c for c in chunk_text(e["body"] or "(no text)")]
    meta = {
        "sender": e["sender"],
        "subject": e["subject"],
        "date": e["date"],
        "date_ts": e["date_ts"],
        "email_id": e["id"],
    }
    col.add(
        ids=[f"{e['id']}_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=model.encode(chunks).tolist(),
        metadatas=[meta] * len(chunks),
    )
    return True


def sync_mailbox(limit: int = 100, folder: str = "INBOX") -> int:
    """Fetch recent emails and index the new ones. Returns the number added."""
    added = 0
    for e in fetch_emails(limit=limit, folder=folder):
        if index_email(e):
            added += 1
    return added


if __name__ == "__main__":
    print("New emails indexed:", sync_mailbox(limit=100))