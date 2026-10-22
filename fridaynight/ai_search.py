"""
AI-enhanced event discovery using sentence-transformers.
Events are embedded once and cached, so each search only embeds the query.
"""

_model = None          # loaded lazily so the app still starts quickly
_cache = {}            # event.id -> (text that was embedded, embedding)


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def _event_text(event):
    # everything a user might describe an event by
    return f'{event.title}. {event.artist or ""}. {event.category}. {event.venue}. {event.description}'


def _embedding_for(event):
    """Return the cached embedding, recomputing only if the event text changed
    (so edited events are picked up automatically)."""
    text = _event_text(event)
    cached = _cache.get(event.id)
    if cached is None or cached[0] != text:
        _cache[event.id] = (text, _get_model().encode(text, convert_to_tensor=True))
    return _cache[event.id][1]


def keyword_search(events, query):
    """Traditional search: the query must appear somewhere in the event text."""
    q = query.lower()
    return [e for e in events if q in _event_text(e).lower()]


def rank_events_by_query(events, query, threshold=0.25):
    """Semantic search: rank events by how close their meaning is to the query."""
    if not query or not events:
        return events

    from sentence_transformers import util
    query_vec = _get_model().encode(query, convert_to_tensor=True)

    scored = []
    for event in events:
        score = util.cos_sim(query_vec, _embedding_for(event)).item()
        if query.lower() in _event_text(event).lower():
            score += 0.3   # a direct word match should always rank well
        scored.append((event, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [event for event, score in scored if score >= threshold]

def related_events(event, all_events, limit=3):
    """Return the events most similar in meaning to this one (not including itself)."""
    from sentence_transformers import util
    target = _embedding_for(event)

    scored = []
    for other in all_events:
        if other.id == event.id or other.status == 'Cancelled':
            continue
        score = util.cos_sim(target, _embedding_for(other)).item()
        scored.append((other, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [e for e, score in scored[:limit]]