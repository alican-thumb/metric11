import unittest

from src.generate_preview_batch import team_slug


class TeamSlugTests(unittest.TestCase):
    def test_2026_27_fixture_names_map_to_existing_slugs(self):
        self.assertEqual(team_slug("İSTANBUL BAŞAKŞEHİR FK"), "basaksehir")
        self.assertEqual(team_slug("ARCA ÇORUM FK"), "corumfk")
        self.assertEqual(team_slug("AMED SPORTİF FAALİYETLER"), "amed")

    def test_dotted_capital_i_does_not_split_slug(self):
        self.assertEqual(team_slug("İZMİR TEST"), "izmir_test")


if __name__ == "__main__":
    unittest.main()
