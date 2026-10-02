import unittest

from src.build_team_scout_blueprints import candidate_matches_role


class ScoutRolePositionTests(unittest.TestCase):
    def test_verified_position_overrides_proxy_role_key(self):
        goalkeeper = {"role_key": "FB_TWO_WAY", "verified_position": "Goalkeeper"}
        self.assertFalse(candidate_matches_role(goalkeeper, "FB_TWO_WAY"))
        self.assertTrue(candidate_matches_role(goalkeeper, "GK_STABILITY"))

    def test_unverified_proxy_is_rejected_for_positional_role(self):
        proxy = {"role_key": "FB_TWO_WAY", "verified_position": None}
        self.assertFalse(candidate_matches_role(proxy, "FB_TWO_WAY"))

    def test_inferred_group_still_accepted_without_verified_position(self):
        candidate = {"role_key": "CB_DOMINANT", "verified_position": None, "inferred_group": "DEF"}
        self.assertTrue(candidate_matches_role(candidate, "CB_DOMINANT"))

    def test_non_positional_roles_accept_any_position(self):
        self.assertTrue(candidate_matches_role({"verified_position": "Goalkeeper"}, "RESALE_VALUE"))


if __name__ == "__main__":
    unittest.main()
