import time

from indexer import col, model


def search(query: str, k: int = 5, sender: str | None = None, days_back: int | None = None) -> list[dict]:
    """Semantic search with optional date filter (in Chroma) and sender filter (in Python)."""
    if col.count() == 0:
        return []

    where = None
    if days_back:
        cutoff = int(time.time()) - days_back * 86400
        where = {"date_ts": {"$gte": cutoff}}

    n = k * 4 if sender else k
    res = col.query(
        query_embeddings=model.encode([query]).tolist(),
        n_results=min(n, col.count()),
        where=where,
    )

    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        if sender and sender.lower() not in meta["sender"].lower():
            continue
        hits.append({"text": doc, "meta": meta, "distance": dist})
    return hits[:k]