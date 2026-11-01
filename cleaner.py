import re
from bs4 import BeautifulSoup

QUOTE_PATTERNS = [
    re.compile(r"^On\s.{5,300}?wrote:", re.I | re.M | re.S),
    re.compile(r"^-{2,}\s*Original Message\s*-{2,}", re.I | re.M),
    re.compile(r"^From:\s.+\n\s*Sent:\s", re.I | re.M),
]


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "head"]):
        tag.decompose()
    return soup.get_text("\n")


def clean_body(text: str, html: str, max_chars: int = 6000) -> str:
    """Prefer plain text, fall back to HTML, then strip quoted replies and noise."""
    if text and text.strip():
        body = text
    elif html:
        body = html_to_text(html)
    else:
        body = ""

    for pattern in QUOTE_PATTERNS:
        match = pattern.search(body)
        if match:
            body = body[: match.start()]

    lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith(">")]
    body = "\n".join(lines)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body[:max_chars]