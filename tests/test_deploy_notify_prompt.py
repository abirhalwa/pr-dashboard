import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import DEPLOY_NOTIFY_PROMPT


class DeployNotifyPromptRulesTest(unittest.TestCase):
    """Regression guard for the deploy-notify subject/link selection rules.

    The actual classification is executed by an LLM at runtime against the
    DEPLOY_NOTIFY_PROMPT text — there is no Python function to exercise — so
    these assertions pin the *prompt* instead. They cover the CGP-55 bug:
    a subtask of a Bug parent was announced as "this story" linked to the
    subtask, because the old rules never rolled up to the parent unless the
    parent was a Story. The fix rolls up to the parent in all cases except
    when the parent is an Epic, and classifies by the effective ticket's type.

    Invariant: if you reword these rules, keep the Epic exception and the
    parent roll-up — dropping either reintroduces the CGP-55 bug.
    """

    def test_rolls_up_to_parent_unless_epic(self):
        # The roll-up must be the default for any parent that is not an Epic,
        # which is what makes a subtask of a Bug announce the parent Bug.
        self.assertIn("parent issuetype is NOT 'Epic'", DEPLOY_NOTIFY_PROMPT)
        self.assertIn("EFFECTIVE_URL = PARENT_URL", DEPLOY_NOTIFY_PROMPT)

    def test_epic_parent_falls_back_to_ticket(self):
        self.assertIn("the parent issuetype is 'Epic'", DEPLOY_NOTIFY_PROMPT)
        self.assertIn("EFFECTIVE_URL = TICKET_URL", DEPLOY_NOTIFY_PROMPT)
        self.assertIn("never the", DEPLOY_NOTIFY_PROMPT)  # "never the EFFECTIVE ticket"

    def test_bug_wording_keys_off_effective_type(self):
        self.assertIn("If EFFECTIVE_TYPE is 'Bug', 'Defect', or 'Hotfix'", DEPLOY_NOTIFY_PROMPT)
        self.assertIn('subject = "this bug fix", link = EFFECTIVE_URL', DEPLOY_NOTIFY_PROMPT)

    def test_default_wording_is_story(self):
        self.assertIn('subject = "this story", link = EFFECTIVE_URL', DEPLOY_NOTIFY_PROMPT)

    def test_old_buggy_rules_are_gone(self):
        # The old rules linked Bugs/fallbacks straight to TICKET_URL and only
        # used PARENT_URL when the parent was a Story. None of those remain.
        self.assertNotIn('subject = "this bug fix", link = TICKET_URL', DEPLOY_NOTIFY_PROMPT)
        self.assertNotIn("Else if parent issuetype is 'Story'", DEPLOY_NOTIFY_PROMPT)


if __name__ == "__main__":
    unittest.main()
