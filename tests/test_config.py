import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import _parse_teams, _parse_slack_ids


class ParseTeamsTest(unittest.TestCase):
    def _call(self, value):
        with unittest.mock.patch.dict(os.environ, {"TEAMS": value}):
            return _parse_teams()

    def test_empty_env(self):
        self.assertEqual(self._call(""), [])

    def test_blank_env(self):
        self.assertEqual(self._call("   "), [])

    def test_non_json(self):
        self.assertEqual(self._call("not-json"), [])

    def test_non_array_root(self):
        self.assertEqual(self._call('{"name":"x"}'), [])

    def test_valid_entry(self):
        result = self._call('[{"name":"Backend","channel_id":"C123","reviewers":["alice","bob"]}]')
        self.assertEqual(result, [{"name": "Backend", "channel_id": "C123", "reviewers": ["alice", "bob"]}])

    def test_missing_name_skipped(self):
        result = self._call('[{"channel_id":"C123"},{"name":"Good","channel_id":"C456"}]')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Good")

    def test_missing_channel_id_skipped(self):
        result = self._call('[{"name":"Bad"},{"name":"Good","channel_id":"C456"}]')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Good")

    def test_empty_name_skipped(self):
        result = self._call('[{"name":"","channel_id":"C123"},{"name":"OK","channel_id":"C456"}]')
        self.assertEqual(len(result), 1)

    def test_reviewers_optional(self):
        result = self._call('[{"name":"T","channel_id":"C1"}]')
        self.assertEqual(result[0]["reviewers"], [])


class ParseSlackIdsTest(unittest.TestCase):
    def _call(self, value):
        with unittest.mock.patch.dict(os.environ, {"SLACK_IDS": value}):
            return _parse_slack_ids()

    def test_empty_env(self):
        self.assertEqual(self._call(""), {})

    def test_valid_pair(self):
        self.assertEqual(self._call("alice:U01ABC"), {"alice": "U01ABC"})

    def test_multiple_pairs(self):
        result = self._call("alice:U01ABC,bob:U02DEF")
        self.assertEqual(result, {"alice": "U01ABC", "bob": "U02DEF"})

    def test_missing_colon_skipped(self):
        result = self._call("aliceU01ABC,bob:U02DEF")
        self.assertEqual(result, {"bob": "U02DEF"})

    def test_non_u_id_skipped(self):
        result = self._call("alice:not-an-id,bob:U02DEF")
        self.assertEqual(result, {"bob": "U02DEF"})

    def test_empty_login_skipped(self):
        result = self._call(":U01ABC,bob:U02DEF")
        self.assertEqual(result, {"bob": "U02DEF"})

    def test_blank_pair_skipped(self):
        result = self._call("alice:U01ABC,,bob:U02DEF")
        self.assertEqual(result, {"alice": "U01ABC", "bob": "U02DEF"})


import unittest.mock

if __name__ == "__main__":
    unittest.main()
