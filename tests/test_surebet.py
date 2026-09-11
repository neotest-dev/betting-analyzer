import pytest
from src.analyzers.surebet import SurebetAnalyzer
from src.calculators.stakes import StakeCalculator


def _make_event(bookmakers, market="1X2"):
    return {
        "event_id": "test_sure_001",
        "sport": "Soccer",
        "league": "Test League",
        "home_team": "Team A",
        "away_team": "Team B",
        "market": market,
        "timestamp": "2026-09-10T12:00:00Z",
        "bookmakers": bookmakers,
    }


def test_surebet_positive_arbitrage():
    """Test detection of positive arbitrage with diverse bookmakers"""
    # Odds: home 2.30 (Bookie 1), draw 3.80 (Bookie 2), away 4.10 (Bookie 3)
    # inverse_sum = 1/2.30 + 1/3.80 + 1/4.10 ≈ 0.9417 < 1.0 → valid surebet
    event = _make_event([
        {"name": "Bookie 1", "odds": {"home_win": 2.30, "draw": 3.40, "away_win": 3.00}},
        {"name": "Bookie 2", "odds": {"home_win": 2.10, "draw": 3.80, "away_win": 3.50}},
        {"name": "Bookie 3", "odds": {"home_win": 2.00, "draw": 3.20, "away_win": 4.10}},
    ])

    opportunities = SurebetAnalyzer.analyze_event(event, default_bankroll=100.0)
    assert len(opportunities) == 1
    opp = opportunities[0]
    assert opp["type"] == "surebet"
    assert opp["roi"] > 0
    assert opp["details"]["inverse_sum"] < 1.0
    assert len(opp["details"]["legs"]) == 3
    assert opp["details"]["unique_bookmakers_count"] >= 2


def test_surebet_negative_arbitrage():
    """Test standard market with margin (no surebet opportunity)"""
    event = _make_event([
        {"name": "Bookie 1", "odds": {"home_win": 1.90, "draw": 3.20, "away_win": 3.80}},
    ])

    opportunities = SurebetAnalyzer.analyze_event(event, default_bankroll=100.0)
    assert len(opportunities) == 0


def test_surebet_rejected_same_bookmaker():
    """
    Falsa surebet: inverse_sum < 1.0 pero todas las mejores cuotas vienen
    de la MISMA casa. Debe ser rechazada — no es un arbitraje explotable.
    """
    # Pinnacle domina todas las selecciones con cuotas que producen inverse_sum < 1
    # 1/2.71 + 1/3.88 + 1/3.71 ≈ 0.8963 < 1.0 (matemáticamente válido)
    # Pero todas vienen de Pinnacle → FALSA surebet
    event = _make_event([
        {
            "name": "Pinnacle",
            "odds": {"home_win": 2.71, "draw": 3.88, "away_win": 3.71},
        },
        {
            "name": "Bet365",
            "odds": {"home_win": 1.80, "draw": 3.00, "away_win": 2.90},  # cuotas inferiores
        },
    ])

    opportunities = SurebetAnalyzer.analyze_event(event, default_bankroll=500.0)
    # Debe ser rechazado: Bet365 no gana ninguna selección → todas de Pinnacle
    assert len(opportunities) == 0, (
        "Se detectó una surebet falsa: todas las cuotas vienen de la misma casa"
    )


def test_surebet_accepted_cross_bookmaker():
    """
    Surebet real: inverse_sum < 1.0 y las cuotas vienen de casas DIFERENTES.
    Debe ser aceptada e incluir metadata de diversidad.
    """
    event = _make_event([
        {"name": "Betano",   "odds": {"home_win": 2.50, "draw": 3.00, "away_win": 2.50}},
        {"name": "Inkabet",  "odds": {"home_win": 2.20, "draw": 3.90, "away_win": 2.80}},
        {"name": "Pinnacle", "odds": {"home_win": 2.10, "draw": 3.10, "away_win": 3.80}},
    ])
    # Best odds: home 2.50 (Betano), draw 3.90 (Inkabet), away 3.80 (Pinnacle)
    # inverse_sum = 1/2.50 + 1/3.90 + 1/3.80 ≈ 0.400 + 0.256 + 0.263 = 0.919 < 1.0

    opportunities = SurebetAnalyzer.analyze_event(event, default_bankroll=1000.0)
    assert len(opportunities) == 1
    opp = opportunities[0]

    # Verify cross-bookmaker fields are present
    assert "unique_bookmakers" in opp["details"]
    assert "unique_bookmakers_count" in opp["details"]
    assert opp["details"]["unique_bookmakers_count"] >= 2

    # Verify all legs have different bookmakers
    leg_bookmakers = [leg["bookmaker"] for leg in opp["details"]["legs"]]
    assert len(set(leg_bookmakers)) >= 2, "Las piernas deben provenir de casas distintas"
