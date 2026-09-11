import json
from pathlib import Path
from typing import List, Dict, Any
from src.providers.base_provider import OddsProvider
from src.config import config


class DemoProvider(OddsProvider):
    """Demo Mode Odds Provider loading data from local JSON files"""

    def __init__(self, sample_odds_path: Path = config.SAMPLE_ODDS_PATH):
        self.sample_odds_path = sample_odds_path

    def get_events(self) -> List[Dict[str, Any]]:
        """Load events from sample_odds.json"""
        if not self.sample_odds_path.exists():
            return []

        with open(self.sample_odds_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_odds(self, event_id: str) -> List[Dict[str, Any]]:
        """Get odds for a specific event by ID"""
        for event in self.get_events():
            if event["event_id"] == event_id:
                return event.get("bookmakers", [])
        return []

    def get_statistics(self, team_name: str) -> Dict[str, Any]:
        """Not applicable in surebet-only mode"""
        return {"team": team_name, "matches_played": 0}
