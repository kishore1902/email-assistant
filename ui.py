import requests
import streamlit as st

API = "http://localhost:8000"

st.set_page_config(page_title="Email Assistant", page_icon="✉️", layout="centered")

st.markdown(
    """
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem; max-width: 820px;}

/* Header banner */
.hero {
    display: flex; align-items: center; gap: 16px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white; padding: 22px 26px; border-radius: 18px;
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.25); margin-bottom: 18px;
}
.hero-icon {
    font-size: 34px; background: rgba(255,255,255,0.18);
    width: 60px; height: 60px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
}
.hero h1 {margin: 0; font-size: 26px; font-weight: 700; color: white; padding: 0;}
.hero p {margin: 2px 0 0 0; font-size: 14px; opacity: 0.9;}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: white; border: 1px solid #E2E8F0; border-radius: 16px;
    padding: 14px 18px; margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #EEF2FF; border-color: #C7D2FE;
}

/* Buttons */
.stButton > button {
    border-radius: 12px; border: 1px solid #C7D2FE; background: white;
    color: #4338CA; font-weight: 500; transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #4F46E5; color: white; border-color: #4F46E5;
    transform: translateY(-1px);
}

/* Sidebar */
[data-testid="stSidebar"] {background: #F1F5F9; border-right: 1px solid #E2E8F0;}
.side-title {font-size: 18px; font-weight: 700; color: #312E81; margin-bottom: 4px;}
.badge {
    display: inline-block; padding: 4px 12px; border-radius: 999px;
    font-size: 12px; font-weight: 600;
}
.badge-ok {background: #DCFCE7; color: #166534;}
.badge-off {background: #FEE2E2; color: #991B1B;}
.stat-card {
    background: white; border: 1px solid #E2E8F0; border-radius: 12px;
    padding: 12px 14px; margin-top: 10px;
}
.stat-num {font-size: 24px; font-weight: 700; color: #4F46E5;}
.stat-label {font-size: 12px; color: #64748B;}

/* Chat input */
[data-testid="stChatInput"] {border-radius: 14px;}
</style>
""",
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []
if "pending" not in st.session_state:
    st.session_state.pending = None


def get_status():
    try:
        r = requests.get(f"{API}/status", timeout=3)
        return r.json()["indexed_chunks"]
    except Exception:
        return None


# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown('<div class="side-title">✉️ Email Assistant</div>', unsafe_allow_html=True)
    st.caption("Chat with your inbox using AI")

    chunks = get_status()
    if chunks is None:
        st.markdown('<span class="badge badge-off">● Backend offline</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-ok">● Backend online</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-card"><div class="stat-num">{chunks}</div>'
            f'<div class="stat-label">Indexed email chunks</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("**📥 Mailbox sync**")
    limit = st.number_input("Emails to fetch", min_value=10, max_value=1000, value=100, step=10)
    if st.button("🔄 Sync mailbox", use_container_width=True):
        with st.spinner("Fetching and indexing emails..."):
            try:
                r = requests.post(f"{API}/sync", params={"limit": int(limit)}, timeout=600)
                r.raise_for_status()
                st.success(f"✅ Indexed {r.json()['new_emails_indexed']} new emails")
            except Exception as ex:
                st.error(f"Sync failed: {ex}")

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.caption("🔒 Read-only access. Drafts are never sent automatically.")

# ---------------- Header ----------------
st.markdown(
    """
<div class="hero">
  <div class="hero-icon">✉️</div>
  <div>
    <h1>Email Assistant</h1>
    <p>Search, summarize and draft replies from your inbox in plain English</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------- Suggestions (only on empty chat) ----------------
SUGGESTIONS = [
    ("📊 Inbox count", "How many emails are in my inbox?"),
    ("📝 Summarize recent", "Summarize my emails from the last 3 days"),
    ("🔎 Find interviews", "Find emails about interviews or job applications"),
    ("✍️ Draft a reply", "Draft a polite reply to my latest email"),
]

if not st.session_state.history:
    st.markdown("##### 💡 Try asking")
    cols = st.columns(2)
    for i, (label, text) in enumerate(SUGGESTIONS):
        if cols[i % 2].button(label, key=f"sug{i}", use_container_width=True):
            st.session_state.pending = text
            st.rerun()

# ---------------- Chat history ----------------
for m in st.session_state.history:
    avatar = "🧑‍💼" if m["role"] == "user" else "🤖"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

# ---------------- Input ----------------
prompt = st.chat_input("Ask about your emails...")
if st.session_state.pending:
    prompt = st.session_state.pending
    st.session_state.pending = None

if prompt:
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(
                    f"{API}/chat",
                    json={"message": prompt, "history": st.session_state.history},
                    timeout=120,
                )
                r.raise_for_status()
                answer = r.json()["answer"]
            except Exception as ex:
                answer = f"⚠️ Could not reach the assistant: {ex}"
        st.markdown(answer)
    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": answer})