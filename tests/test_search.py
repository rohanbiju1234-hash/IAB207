"""
Unit tests for the search and related-events code in ai_search.py.
Fake events are used, so no database is needed.

"""
import unittest
from types import SimpleNamespace

from fridaynight.ai_search import keyword_search, rank_events_by_query, related_events


def make_event(event_id, title, category, venue, description, artist='', status='Open'):
    return SimpleNamespace(
        id=event_id, title=title, artist=artist, category=category,
        venue=venue, description=description, status=status,
    )


JAZZ = make_event(901, 'Blue Note Jazz Evening', 'Jazz', 'Lantern Room',
                  'A smooth, relaxing night of saxophone and piano in a candlelit room.')
ROCK = make_event(902, 'Thunder Road Rock Night', 'Rock', 'Iron Warehouse',
                  'Loud electric guitars, heavy drums and a roaring crowd.')
ROCK2 = make_event(903, 'Guitar Heroes Live', 'Rock', 'Steel Hall',
                   'Classic rock covers with screaming guitar solos and big drums.')
EDM = make_event(904, 'Neon Nights EDM Rave', 'EDM', 'Old Quarter Laneway',
                 'DJs, heavy bass and lasers all night on the dance floor.')
CANCELLED = make_event(905, 'Cancelled Rock Show', 'Rock', 'Steel Hall',
                       'Loud guitars and drums, but this show is off.', status='Cancelled')

ALL_EVENTS = [JAZZ, ROCK, ROCK2, EDM]


class KeywordSearchTests(unittest.TestCase):
    def test_finds_word_in_title(self):
        self.assertEqual(keyword_search(ALL_EVENTS, 'Jazz'), [JAZZ])

    def test_is_case_insensitive(self):
        self.assertEqual(keyword_search(ALL_EVENTS, 'jAzZ'), [JAZZ])

    def test_finds_word_in_venue(self):
        self.assertEqual(keyword_search(ALL_EVENTS, 'Iron Warehouse'), [ROCK])

    def test_finds_word_in_description(self):
        self.assertEqual(keyword_search(ALL_EVENTS, 'saxophone'), [JAZZ])

    def test_no_match_returns_empty_list(self):
        self.assertEqual(keyword_search(ALL_EVENTS, 'xyzabc'), [])

    def test_matches_several_events(self):
        result = keyword_search(ALL_EVENTS, 'guitar')
        self.assertIn(ROCK, result)
        self.assertIn(ROCK2, result)
        self.assertNotIn(JAZZ, result)


class SemanticSearchTests(unittest.TestCase):
    def test_empty_query_returns_all_events(self):
        self.assertEqual(rank_events_by_query(ALL_EVENTS, ''), ALL_EVENTS)

    def test_no_events_returns_empty(self):
        self.assertEqual(rank_events_by_query([], 'jazz'), [])

    def test_relaxing_music_ranks_jazz_first(self):
        result = rank_events_by_query(ALL_EVENTS, 'smooth relaxing music for a quiet evening', threshold=0)
        self.assertEqual(result[0], JAZZ)

    def test_loud_guitars_ranks_rock_first(self):
        result = rank_events_by_query(ALL_EVENTS, 'loud electric guitars', threshold=0)
        self.assertIn(result[0], (ROCK, ROCK2))

    def test_dance_query_ranks_edm_first(self):
        result = rank_events_by_query(ALL_EVENTS, 'DJ and dancing all night', threshold=0)
        self.assertEqual(result[0], EDM)

    def test_very_high_threshold_returns_nothing(self):
        self.assertEqual(rank_events_by_query(ALL_EVENTS, 'jazz', threshold=5), [])

    def test_threshold_zero_returns_every_event(self):
        result = rank_events_by_query(ALL_EVENTS, 'music', threshold=-1)
        self.assertEqual(len(result), len(ALL_EVENTS))


class RelatedEventsTests(unittest.TestCase):
    def test_does_not_include_itself(self):
        result = related_events(ROCK, ALL_EVENTS)
        self.assertNotIn(ROCK, result)

    def test_excludes_cancelled_events(self):
        result = related_events(ROCK, ALL_EVENTS + [CANCELLED])
        self.assertNotIn(CANCELLED, result)

    def test_respects_limit(self):
        self.assertEqual(len(related_events(ROCK, ALL_EVENTS, limit=2)), 2)

    def test_most_similar_event_comes_first(self):
        # the other rock event should be closer to ROCK than jazz or EDM
        self.assertEqual(related_events(ROCK, ALL_EVENTS)[0], ROCK2)

    def test_empty_list_returns_empty(self):
        self.assertEqual(related_events(ROCK, []), [])


if __name__ == '__main__':
    unittest.main()