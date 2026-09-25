"""
AI-enhanced event discovery.

The assignment requires *more* than plain keyword matching - e.g. semantic
search, recommendations, or related-event suggestions (confirmed with your
tutor which approach you're doing).

This file currently ships a lightweight placeholder (difflib-based fuzzy
matching over title/description/category/venue/artist) so the app runs with
zero extra dependencies. Swap this out for real semantic search using
sentence-transformers before you submit - that's what will actually satisfy
the "AI-enhanced" requirement; the code below on its own is NOT sufficient.

--------------------------------------------------------------------------
HOW TO UPGRADE TO REAL SEMANTIC SEARCH (sentence-transformers):

    pip install sentence-transformers

    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('all-MiniLM-L6-v2')  # small, fast, good enough

    # Precompute embeddings for each event's text (title + description + category)
    # once (e.g. when the event is created, store as a pickled/JSON blob, or just
    # recompute on the fly for a small dataset - fine for coursework scale).

    def rank_events_by_query(events, query):
        if not events or not query:
            return events
        corpus = [f'{e.title}. {e.description} Category: {e.category}' for e in events]
        corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
        query_embedding = model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        ranked = sorted(zip(events, scores.tolist()), key=lambda pair: pair[1], reverse=True)
        return [e for e, score in ranked if score > 0.2]  # drop weak matches

This finds events based on MEANING (e.g. searching "chill night out with live
music" could surface a jazz event even with zero overlapping keywords),
rather than requiring an exact substring match.
--------------------------------------------------------------------------
"""

from difflib import SequenceMatcher


def _similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def rank_events_by_query(events, query):
    """Placeholder ranking: fuzzy-matches the query against several event
    fields and returns events sorted by relevance (best first), dropping
    anything with very low relevance. Replace with real embeddings - see
    the module docstring above."""
    if not query:
        return events

    scored = []
    for event in events:
        haystack = ' '.join(filter(None, [
            event.title, event.description, event.category, event.venue, event.artist
        ]))
        score = _similarity(query, haystack)
        # also boost heavily on a direct substring hit anywhere in the text
        if query.lower() in haystack.lower():
            score += 0.5
        scored.append((event, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [event for event, score in scored if score > 0.08]
