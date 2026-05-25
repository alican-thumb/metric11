BIG_MATCH_OPPONENTS = {
    "GALATASARAY A.Ş.",
    "FENERBAHÇE A.Ş.",
    "TRABZONSPOR A.Ş.",
}

SPECIALIST_SCORE_MULTIPLIERS = {
    # Segment backtest shows these are weak without direct corner/aerial/verified penalty taker data.
    "set_piece_defender": 0.55,
    "penalty_profile": 0.55,
    "impact_sub": 1.0,
    "big_match_scorer": 1.0,
}

ACTION_LABELS = {
    "PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO": "Korumalı taraf tahmini",
    "KEEP_PICK_WITH_DRAW_WARNING": "Beraberlik uyarılı tahmin",
    "KEEP_MAIN_PICK": "Ana tahmini koru",
    "taraf_eğilimi": "Taraf eğilimi",
    "senaryo_anlat": "Senaryo anlat",
    "beraberlik_korumalı_senaryo": "Beraberlik korumalı senaryo",
}
