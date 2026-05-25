CREATE TABLE IF NOT EXISTS data_sources (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('API', 'SCRAPING', 'OPEN_DATA', 'MANUAL')),
    base_url TEXT,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    confidence_score NUMERIC(4,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS teams (
    id BIGSERIAL PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    country TEXT,
    league TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (canonical_name, country)
);

CREATE TABLE IF NOT EXISTS players (
    id BIGSERIAL PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    birth_date DATE,
    nationality TEXT,
    primary_position TEXT,
    preferred_foot TEXT,
    height_cm INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_aliases (
    id BIGSERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('TEAM', 'PLAYER', 'REFEREE', 'COACH')),
    entity_id BIGINT NOT NULL,
    alias TEXT NOT NULL,
    data_source_id BIGINT REFERENCES data_sources(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (entity_type, alias, data_source_id)
);

CREATE TABLE IF NOT EXISTS team_squads (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL REFERENCES teams(id),
    player_id BIGINT NOT NULL REFERENCES players(id),
    season TEXT NOT NULL,
    shirt_number INTEGER,
    squad_position TEXT,
    joined_at DATE,
    left_at DATE,
    contract_until DATE,
    market_value_eur NUMERIC(14,2),
    data_source_id BIGINT REFERENCES data_sources(id),
    raw_details JSONB,
    UNIQUE (team_id, player_id, season)
);

CREATE TABLE IF NOT EXISTS player_attribute_profiles (
    id BIGSERIAL PRIMARY KEY,
    player_id BIGINT REFERENCES players(id),
    player_name TEXT NOT NULL,
    player_name_normalized TEXT NOT NULL,
    team_name TEXT,
    source_name TEXT NOT NULL,
    source_url TEXT,
    license_status TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    age INTEGER,
    position TEXT,
    current_ability NUMERIC(6,2),
    potential_ability NUMERIC(6,2),
    growth_room NUMERIC(6,2),
    physical_score NUMERIC(6,2),
    mental_score NUMERIC(6,2),
    technical_score NUMERIC(6,2),
    role_fit_score NUMERIC(6,2),
    market_value_text TEXT,
    wage_text TEXT,
    raw_attributes JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (player_name_normalized, team_name, source_name)
);

CREATE TABLE IF NOT EXISTS referees (
    id BIGSERIAL PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    country TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (canonical_name, country)
);

CREATE TABLE IF NOT EXISTS matches (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT,
    data_source_id BIGINT REFERENCES data_sources(id),
    competition TEXT,
    season TEXT,
    matchday INTEGER,
    home_team_id BIGINT REFERENCES teams(id),
    away_team_id BIGINT REFERENCES teams(id),
    referee_id BIGINT REFERENCES referees(id),
    venue TEXT,
    match_date TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'SCHEDULED',
    home_score INTEGER,
    away_score INTEGER,
    raw_details JSONB,
    UNIQUE (external_id, data_source_id)
);

CREATE TABLE IF NOT EXISTS match_lineups (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    team_id BIGINT NOT NULL REFERENCES teams(id),
    player_id BIGINT NOT NULL REFERENCES players(id),
    is_starting BOOLEAN,
    position TEXT,
    shirt_number INTEGER,
    minute_in INTEGER,
    minute_out INTEGER,
    raw_details JSONB,
    UNIQUE (match_id, team_id, player_id)
);

CREATE TABLE IF NOT EXISTS player_availability (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    team_id BIGINT REFERENCES teams(id),
    player_id BIGINT NOT NULL REFERENCES players(id),
    status TEXT NOT NULL CHECK (status IN ('AVAILABLE', 'SUSPENDED', 'INJURED', 'DOUBTFUL', 'RESTED', 'UNKNOWN')),
    reason TEXT,
    source_kind TEXT NOT NULL CHECK (source_kind IN ('OFFICIAL', 'SCRAPING', 'DERIVED', 'MANUAL')),
    confidence_level TEXT CHECK (confidence_level IN ('LOW', 'MEDIUM', 'HIGH')),
    affects_lineup BOOLEAN NOT NULL DEFAULT true,
    model_version TEXT NOT NULL DEFAULT 'availability-v0',
    raw_details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (match_id, player_id, status, source_kind, model_version)
);

CREATE TABLE IF NOT EXISTS player_match_stats (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    player_id BIGINT NOT NULL REFERENCES players(id),
    team_id BIGINT REFERENCES teams(id),
    minutes_played INTEGER,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    shots INTEGER,
    shots_on_target INTEGER,
    fouls_committed INTEGER,
    fouls_won INTEGER,
    rating NUMERIC(4,2),
    data_source_id BIGINT REFERENCES data_sources(id),
    raw_details JSONB,
    UNIQUE (match_id, player_id, data_source_id)
);

CREATE TABLE IF NOT EXISTS team_match_stats (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    team_id BIGINT NOT NULL REFERENCES teams(id),
    goals_for INTEGER,
    goals_against INTEGER,
    shots INTEGER,
    shots_on_target INTEGER,
    possession_pct NUMERIC(5,2),
    corners INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    fouls INTEGER,
    data_source_id BIGINT REFERENCES data_sources(id),
    raw_details JSONB,
    UNIQUE (match_id, team_id, data_source_id)
);

CREATE TABLE IF NOT EXISTS referee_match_stats (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    referee_id BIGINT NOT NULL REFERENCES referees(id),
    yellow_cards INTEGER,
    red_cards INTEGER,
    penalties INTEGER,
    fouls INTEGER,
    var_reviews INTEGER,
    raw_details JSONB,
    UNIQUE (match_id, referee_id)
);

CREATE TABLE IF NOT EXISTS derived_player_metrics (
    id BIGSERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL REFERENCES players(id),
    team_id BIGINT REFERENCES teams(id),
    season TEXT,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    form_score NUMERIC(6,2),
    press_effort_score NUMERIC(6,2),
    defensive_activity_score NUMERIC(6,2),
    estimated_distance_km_min NUMERIC(5,2),
    estimated_distance_km_max NUMERIC(5,2),
    card_risk_score NUMERIC(6,2),
    goal_threat_score NUMERIC(6,2),
    resale_potential_score NUMERIC(6,2),
    confidence_level TEXT CHECK (confidence_level IN ('LOW', 'MEDIUM', 'HIGH')),
    model_version TEXT NOT NULL DEFAULT 'manual-v0',
    raw_features JSONB,
    UNIQUE (player_id, team_id, season, metric_date, model_version)
);

CREATE TABLE IF NOT EXISTS derived_team_metrics (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL REFERENCES teams(id),
    season TEXT,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    form_score NUMERIC(6,2),
    attack_score NUMERIC(6,2),
    defense_score NUMERIC(6,2),
    tempo_score NUMERIC(6,2),
    squad_age_risk_score NUMERIC(6,2),
    position_need JSONB,
    model_version TEXT NOT NULL DEFAULT 'manual-v0',
    raw_features JSONB,
    UNIQUE (team_id, season, metric_date, model_version)
);

CREATE TABLE IF NOT EXISTS derived_referee_metrics (
    id BIGSERIAL PRIMARY KEY,
    referee_id BIGINT NOT NULL REFERENCES referees(id),
    season TEXT,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    cards_per_match NUMERIC(6,2),
    red_cards_per_match NUMERIC(6,2),
    penalty_rate NUMERIC(6,2),
    home_bias_score NUMERIC(6,2),
    derby_intensity_score NUMERIC(6,2),
    strictness_score NUMERIC(6,2),
    model_version TEXT NOT NULL DEFAULT 'manual-v0',
    raw_features JSONB,
    UNIQUE (referee_id, season, metric_date, model_version)
);

CREATE TABLE IF NOT EXISTS match_predictions (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(id),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    model_version TEXT NOT NULL,
    home_win_probability NUMERIC(6,4),
    draw_probability NUMERIC(6,4),
    away_win_probability NUMERIC(6,4),
    over_2_5_probability NUMERIC(6,4),
    both_teams_score_probability NUMERIC(6,4),
    expected_home_goals NUMERIC(5,2),
    expected_away_goals NUMERIC(5,2),
    confidence_level TEXT CHECK (confidence_level IN ('LOW', 'MEDIUM', 'HIGH')),
    raw_features JSONB
);

CREATE TABLE IF NOT EXISTS player_match_predictions (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(id),
    player_id BIGINT REFERENCES players(id),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    model_version TEXT NOT NULL,
    start_probability NUMERIC(6,4),
    goal_probability NUMERIC(6,4),
    assist_probability NUMERIC(6,4),
    card_probability NUMERIC(6,4),
    error_risk_score NUMERIC(6,2),
    estimated_distance_km_min NUMERIC(5,2),
    estimated_distance_km_max NUMERIC(5,2),
    confidence_level TEXT CHECK (confidence_level IN ('LOW', 'MEDIUM', 'HIGH')),
    raw_features JSONB
);

CREATE TABLE IF NOT EXISTS analysis_reports (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(id),
    report_type TEXT NOT NULL CHECK (report_type IN ('MATCH_PREVIEW', 'SCOUTING', 'TEAM_NEED', 'REFEREE')),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    model_version TEXT,
    language TEXT NOT NULL DEFAULT 'tr',
    title TEXT NOT NULL,
    summary TEXT,
    report_markdown TEXT NOT NULL,
    source_prediction_id BIGINT REFERENCES match_predictions(id),
    raw_inputs JSONB
);
