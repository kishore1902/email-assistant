# ✉️ Email Assistant: Chat with Your Inbox using RAG and LLMs

An AI-powered email assistant that lets you search, summarize, and draft replies to your emails in plain English. It connects to Gmail over IMAP, indexes your messages in a vector database, and uses Retrieval-Augmented Generation (RAG) with Google Gemini to give answers grounded in your actual emails.

> <img width="1812" height="867" alt="image" src="https://github.com/user-attachments/assets/9f2125bd-f5fc-42eb-af72-91cf97726666" />


## ✨ Features

- **Natural-language search**: ask "What did the recruiter say about the interview?" instead of guessing keywords.
- **Summaries**: get the key points of recent emails or a sender's messages.
- **Draft replies**: generates a reply for you to review. Nothing is ever sent automatically.
- **Inbox stats**: ask how many emails are in your inbox or how many are unread.
- **Smart filters**: understands sender and time hints such as "from Amazon in the last 7 days".
- **Source-grounded answers**: the model answers only from retrieved emails and cites sender, subject, and date.
- **Prompt-injection safeguards**: email text is treated as untrusted data, not instructions.
- **Clean chat UI**: Streamlit interface with suggestion buttons and a backend status panel.

## 🏗️ How It Works

```
Gmail (IMAP) → Clean & parse → Chunk → Embed (MiniLM) → ChromaDB
                                                            ↓
User question → Intent routing (Gemini) → Retrieve top emails → Gemini answer
```

1. **Ingestion**: `imap-tools` fetches emails over IMAP without marking them as read.
2. **Cleaning**: HTML is converted to text, and quoted replies and noise are removed.
3. **Indexing**: emails are split into chunks, embedded with `all-MiniLM-L6-v2`, and stored in ChromaDB with metadata (sender, subject, date).
4. **Intent routing**: Gemini classifies each message as search, summarize, draft reply, count, or chat, and extracts filters.
5. **Retrieval and generation**: the most relevant chunks are passed to Gemini with strict grounding instructions.

## 🛠️ Tech Stack

Python · FastAPI · Streamlit · imap-tools · Sentence-Transformers · ChromaDB · Google Gemini API · BeautifulSoup

## 📁 Project Structure

```
email-assistant/
├── .streamlit/config.toml   # UI theme
├── cleaner.py               # email body cleaning
├── imap_client.py           # IMAP fetching and inbox counts
├── indexer.py               # chunking, embeddings, ChromaDB
├── retriever.py             # semantic search with filters
├── llm.py                   # Gemini wrapper
├── agent.py                 # intent routing and answer generation
├── main.py                  # FastAPI backend
├── ui.py                    # Streamlit chat interface
├── requirements.txt
└── .env.example
```

## 🚀 Getting Started

### 1. Clone and install
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 2. Get your credentials
- **Gmail app password**: turn on 2-Step Verification, then create an app password at https://myaccount.google.com/apppasswords. Make sure IMAP is enabled in Gmail settings.
- **Gemini API key**: create one in Google AI Studio.

### 3. Configure environment variables
Copy `.env.example` to `.env` and fill it in:
```
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=your16charapppassword
GEMINI_API_KEY=your-ai-studio-key
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Run
Open two terminals (with the virtual environment active in both):
```bash
uvicorn main:app --reload      # terminal 1: backend on port 8000
streamlit run ui.py            # terminal 2: chat UI on port 8501
```
In the sidebar, click **Sync mailbox** once, then start chatting.

## 💬 Example Questions

- "How many emails are in my inbox?"
- "Summarize my emails from the last 3 days"
- "Find emails about interviews or job applications"
- "What did <sender> say about the deadline?"
- "Draft a polite reply to my latest email"

## 🔒 Privacy and Security

- Access is read-only. The app has no code that sends, deletes, or modifies emails.
- Credentials live in `.env`, which is excluded from git. **Never commit your `.env` file.** If a key or app password leaks, revoke it immediately.
- Indexed emails are stored locally in `chroma_db/`.
- Retrieved email text is sent to the Gemini API to generate answers. Check Google's current data-usage terms for your API tier before indexing sensitive mail.

## ⚠️ Limitations

- Answers depend on retrieval quality, so very old or unsynced emails won't be found.
- Attachments are not parsed yet.
- Designed for a single user and a single mailbox.

## 🗺️ Roadmap

- [ ] Hybrid search (vector + BM25) and re-ranking
- [ ] Evaluation set with recall@k metrics
- [ ] Email categorization (urgent, newsletter, personal)
- [ ] Attachment text extraction (PDF, DOCX)
- [ ] Confirmed send-reply flow
- [ ] Multi-user support with secure token storage

## 📄 License

MIT License. See `LICENSE` for details.

## 👤 Author

**Kishore**: [GitHub](https://github.com/kishore1902)
