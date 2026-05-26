import unittest
from datetime import datetime, timezone

from src.build_source_performance_report import build_report


def evidence(source, tier, published_at, source_type="google_news", **extra):
    return {
        "source": source,
        "source_tier": tier,
        "source_type": source_type,
        "published_at": published_at,
        "title": "Transfer haberi",
        "link": "https://example.test/story",
        **extra,
    }


def claim(player, destination, status, items):
    return {
        "player_name": player,
        "to_club": destination,
        "verification_status": status,
        "evidence": items,
    }


class SourcePerformanceReportTests(unittest.TestCase):
    def test_official_conversion_records_lead_time(self):
        intel = {
            "generated_at": "2026-05-25T12:00:00+00:00",
            "transfer_signals": 2,
            "transfers": [
                claim(
                    "Ali Örnek",
                    "BEŞİKTAŞ A.Ş.",
                    "OFFICIAL",
                    [evidence("Beşiktaş Resmi Web", "OFFICIAL", "2026-05-10T12:00:00+00:00", "official_club")],
                ),
                claim(
                    "Ali Örnek",
                    "Beşiktaş",
                    "RUMOR",
                    [evidence("Haber Muhabiri", "MEDIA", "2026-05-10T08:00:00+00:00")],
                ),
            ],
        }

        result = build_report(intel, twitter={"collection_status": "MISSING_CREDENTIALS"}, now=datetime(2026, 5, 25, tzinfo=timezone.utc))
        row = next(item for item in result["sources"] if item["source"] == "Haber Muhabiri")

        self.assertEqual(row["official_conversions"], 1)
        self.assertEqual(row["average_lead_hours"], 4.0)
        self.assertEqual(row["false_alarm_proxy_pct"], 0.0)
        self.assertGreater(row["score"], 80)

    def test_mature_unconfirmed_signal_is_false_alarm_proxy_only(self):
        intel = {
            "generated_at": "2026-05-25T12:00:00+00:00",
            "transfer_signals": 1,
            "transfers": [
                claim(
                    "Ali Örnek",
                    "GALATASARAY A.Ş.",
                    "RUMOR",
                    [evidence("Transfer Kanalı", "SECONDARY", "2026-04-01T10:00:00+00:00", "telegram")],
                ),
            ],
        }

        result = build_report(intel, now=datetime(2026, 5, 25, tzinfo=timezone.utc))
        row = next(item for item in result["sources"] if item["source"] == "Transfer Kanalı")

        self.assertEqual(row["matured_unconfirmed"], 1)
        self.assertEqual(row["false_alarm_proxy_pct"], 100.0)
        self.assertEqual(row["score"], 0.0)
        telegram = next(item for item in result["provider_measurements"] if item["source"] == "Telegram")
        self.assertEqual(telegram["false_alarm_proxy_pct"], 100.0)

    def test_x_transfer_reporters_are_visible_when_collection_is_unavailable(self):
        result = build_report(
            {"generated_at": "2026-05-25T12:00:00+00:00", "transfer_signals": 0, "transfers": []},
            twitter={"collection_status": "MISSING_CREDENTIALS", "configured_accounts": 45, "total_tweets": 0},
        )
        rows = {item["source"]: item for item in result["sources"]}

        self.assertEqual(rows["@yagosabuncuoglu"]["status"], "X_DATA_UNAVAILABLE")
        self.assertEqual(rows["@ertansuzgun"]["status"], "X_DATA_UNAVAILABLE")
        x_channel = next(item for item in result["provider_measurements"] if item["source"] == "X")
        self.assertEqual(x_channel["status"], "X_DATA_UNAVAILABLE")

    def test_empty_successful_telegram_channels_remain_visible(self):
        result = build_report(
            {"generated_at": "2026-05-25T12:00:00+00:00", "transfer_signals": 0, "transfers": []},
            telegram={"collection_status": "SUCCESS", "total_messages": 48},
        )
        rows = {item["source"]: item for item in result["sources"]}
        channel = next(item for item in result["provider_measurements"] if item["source"] == "Telegram")

        self.assertEqual(rows["Transfer Haber"]["status"], "NO_TRANSFER_CLAIMS")
        self.assertEqual(channel["status"], "NO_TRANSFER_CLAIMS")

    def test_retained_early_claim_converts_after_official_announcement_arrives(self):
        history = {
            "observations": [
                {
                    "source": "Muhabir",
                    "source_tier": "SECONDARY",
                    "source_type": "telegram",
                    "event_key": "ALI ORNEK|BESIKTAS",
                    "player_name": "Ali Örnek",
                    "to_club": "Beşiktaş",
                    "published_at": "2026-05-01T10:00:00+00:00",
                    "title": "İlk iddia",
                    "link": "https://example.test/early",
                }
            ]
        }
        intel = {
            "generated_at": "2026-05-05T14:00:00+00:00",
            "transfer_signals": 1,
            "transfers": [
                claim(
                    "Ali Örnek",
                    "BEŞİKTAŞ A.Ş.",
                    "OFFICIAL",
                    [evidence("Beşiktaş Resmi Web", "OFFICIAL", "2026-05-05T14:00:00+00:00", "official_club")],
                )
            ],
        }

        result = build_report(intel, history=history)
        row = next(item for item in result["sources"] if item["source"] == "Muhabir")

        self.assertEqual(row["official_conversions"], 1)
        self.assertEqual(row["average_lead_hours"], 100.0)

    def test_historical_official_event_is_retained_when_not_in_latest_snapshot(self):
        result = build_report(
            {"generated_at": "2026-05-25T12:00:00+00:00", "transfer_signals": 0, "transfers": []},
            history={
                "official_events": [
                    {"event_key": "ALI ORNEK|BESIKTAS", "official_at": "2026-05-05T14:00:00+00:00"}
                ]
            },
        )

        self.assertEqual(result["summary"]["official_events"], 1)
        self.assertEqual(result["summary"]["official_events_with_timestamp"], 1)

    def test_archived_official_claim_remains_available_to_performance_scoring(self):
        archived_official = claim(
            "Laszlo Benes",
            "Kayserispor",
            "OFFICIAL",
            [evidence("Kayserispor Resmi Web", "OFFICIAL", "2025-08-16T20:51:53+03:00", "official_club")],
        )
        result = build_report(
            {
                "generated_at": "2026-05-26T12:00:00+00:00",
                "transfer_signals": 0,
                "transfers": [],
                "historical_transfer_claims": [archived_official],
            }
        )

        self.assertEqual(result["summary"]["transfer_signals"], 0)
        self.assertEqual(result["summary"]["official_events"], 1)

    def test_explicit_reporter_attribution_creates_separate_media_observation(self):
        intel = {
            "generated_at": "2026-05-25T12:00:00+00:00",
            "transfer_signals": 1,
            "transfers": [
                claim(
                    "Ali Örnek",
                    "Fenerbahçe",
                    "RUMOR",
                    [
                        evidence(
                            "Diken",
                            "MEDIA",
                            "2026-05-10T08:00:00+00:00",
                            title="Sabuncuoğlu: Fenerbahçe Ali Örnek transferinde anlaşmaya vardı - Diken",
                        )
                    ],
                )
            ],
        }

        result = build_report(intel, now=datetime(2026, 5, 25, tzinfo=timezone.utc))
        reporter = next(item for item in result["sources"] if item["source"] == "Yağız Sabuncuoğlu")
        watch = next(item for item in result["reporter_watch"] if item["name"] == "Yağız Sabuncuoğlu")

        self.assertEqual(reporter["source_type"], "attributed_media")
        self.assertEqual(reporter["observations"], 1)
        self.assertEqual(watch["attributed_observations"], 1)
        self.assertNotEqual(watch["performance_status"], "ATTRIBUTION_PENDING")
        self.assertFalse(any(item["name"] == "Yakın Takip" for item in result["reporter_watch"]))
        self.assertTrue(any(item["name"] == "Yusuf Günaydın" for item in result["reporter_watch"]))

    def test_official_first_observed_time_is_reported_as_bound_not_exact_lead(self):
        intel = {
            "generated_at": "2026-05-25T12:00:00+00:00",
            "transfer_signals": 2,
            "transfers": [
                claim(
                    "Ali Örnek",
                    "Beşiktaş",
                    "OFFICIAL",
                    [
                        evidence(
                            "Beşiktaş Resmi Web",
                            "OFFICIAL",
                            None,
                            "official_club",
                            first_observed_at="2026-05-10T12:00:00+00:00",
                        )
                    ],
                ),
                claim(
                    "Ali Örnek",
                    "Beşiktaş",
                    "RUMOR",
                    [evidence("Haber Muhabiri", "MEDIA", "2026-05-10T08:00:00+00:00")],
                ),
            ],
        }

        result = build_report(intel)
        row = next(item for item in result["sources"] if item["source"] == "Haber Muhabiri")

        self.assertEqual(result["summary"]["official_events_with_timestamp"], 0)
        self.assertEqual(result["summary"]["official_events_with_first_observed_timestamp"], 1)
        self.assertEqual(row["average_lead_hours"], None)
        self.assertEqual(row["average_first_seen_lead_hours"], 4.0)
        self.assertEqual(row["status"], "FIRST_SEEN_BOUND")

    def test_improved_direction_replaces_old_observation_instead_of_double_counting(self):
        history = {
            "observations": [
                {
                    "source": "Yağız Sabuncuoğlu",
                    "source_tier": "ATTRIBUTED_MEDIA",
                    "source_type": "attributed_media",
                    "event_key": None,
                    "player_name": "Ali Örnek",
                    "to_club": None,
                    "published_at": "2026-05-01T10:00:00+00:00",
                    "title": "Sabuncuoğlu: Fenerbahçe Ali Örnek transferinde anlaşmaya vardı",
                    "link": "https://example.test/claim",
                }
            ]
        }
        intel = {
            "generated_at": "2026-05-25T12:00:00+00:00",
            "transfer_signals": 1,
            "transfers": [
                claim(
                    "Ali Örnek",
                    "Fenerbahçe",
                    "RUMOR",
                    [
                        evidence(
                            "Diken",
                            "MEDIA",
                            "2026-05-01T10:00:00+00:00",
                            title="Sabuncuoğlu: Fenerbahçe Ali Örnek transferinde anlaşmaya vardı",
                            link="https://example.test/claim",
                        )
                    ],
                )
            ],
        }

        result = build_report(intel, history=history)
        reporter = next(item for item in result["sources"] if item["source"] == "Yağız Sabuncuoğlu")

        self.assertEqual(reporter["observations"], 1)
        self.assertEqual(reporter["scoreable_claims"], 1)

    def test_same_media_publisher_channels_are_one_performance_observation(self):
        intel = {
            "generated_at": "2026-05-25T12:00:00+00:00",
            "transfer_signals": 1,
            "transfers": [
                claim(
                    "Ali Örnek",
                    "Galatasaray",
                    "RUMOR",
                    [
                        evidence(
                            "Hürriyet Spor",
                            "MEDIA",
                            "2026-05-10T07:00:00+00:00",
                            "rss",
                            title="Galatasaray Ali Örnek transferi için teklifte bulundu",
                            link="https://example.test/rss-copy",
                        ),
                        evidence(
                            "Hürriyet",
                            "MEDIA",
                            "2026-05-10T07:00:00+00:00",
                            "google_news",
                            title="Galatasaray Ali Örnek transferi için teklifte bulundu - Hürriyet",
                            link="https://example.test/google-copy",
                        ),
                    ],
                )
            ],
        }

        result = build_report(intel, now=datetime(2026, 5, 25, tzinfo=timezone.utc))
        rows = {item["source"]: item for item in result["sources"]}

        self.assertNotIn("Hürriyet Spor", rows)
        self.assertEqual(rows["Hürriyet"]["observations"], 1)
        self.assertEqual(rows["Hürriyet"]["scoreable_claims"], 1)


if __name__ == "__main__":
    unittest.main()
