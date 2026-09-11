from typing import List, Dict, Any, Optional
from src.config import config
from src.database import db
from src.providers.demo_provider import DemoProvider
from src.providers.api_provider import APIProvider
from src.analyzers.surebet import SurebetAnalyzer


class OpportunityService:
    """Orchestrates Providers, SurebetAnalyzer, and SQLite Data persistence"""

    def __init__(self):
        self.provider_mode = config.PROVIDER_MODE
        if self.provider_mode == "API":
            self.provider = APIProvider()
        else:
            self.provider = DemoProvider()

    def refresh_and_analyze_all(self, bankroll: float = 100.0) -> Dict[str, Any]:
        """
        Fetch events from active provider, run the Surebet Analyzer,
        store results in SQLite, and return a consolidated report.
        """
        events = self.provider.get_events()
        if not events:
            if self.provider_mode == "API":
                db.clear_snapshot()
            return {
                "total_events": 0,
                "total_opportunities": 0,
                "surebets_count": 0,
                "opportunities": [],
                "provider_status": self.get_provider_status()
            }

        # Persist events. API mode replaces the whole snapshot to avoid stale demo rows.
        if self.provider_mode == "API":
            db.replace_events(events)
        else:
            db.save_events(events)

        all_opportunities: List[Dict[str, Any]] = []

        for event in events:
            surebets = SurebetAnalyzer.analyze_event(event, default_bankroll=bankroll)
            all_opportunities.extend(surebets)

        # Persist a fresh opportunity snapshot to avoid stale or duplicated rows.
        db.replace_opportunities(all_opportunities)

        return {
            "total_events": len(events),
            "total_opportunities": len(all_opportunities),
            "surebets_count": len(all_opportunities),
            "opportunities": all_opportunities,
            "provider_status": self.get_provider_status()
        }

    def get_filtered_opportunities(
        self,
        sport: Optional[str] = None,
        min_roi: Optional[float] = None,
        bookmaker: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve and filter surebet opportunities from SQLite database"""
        opportunities = db.get_opportunities(opp_type="surebet")
        if not opportunities and self.provider_mode != "API":
            self.refresh_and_analyze_all()
            opportunities = db.get_opportunities(opp_type="surebet")

        filtered = []
        for opp in opportunities:
            if sport and sport.lower() != "all" and opp["sport"].lower() != sport.lower():
                continue
            if min_roi is not None and opp["roi"] < min_roi:
                continue
            if bookmaker and bookmaker.lower() != "all":
                details = opp.get("details", {})
                legs = details.get("legs", [])
                bm_match = any(leg.get("bookmaker", "").lower() == bookmaker.lower() for leg in legs)
                if not bm_match:
                    continue
            filtered.append(opp)
        return filtered

    def get_summary(self) -> Dict[str, Any]:
        """Build a dashboard summary from the current SQLite snapshot."""
        opportunities = db.get_opportunities(opp_type="surebet")
        return {
            "total_events": db.count_events(),
            "total_opportunities": len(opportunities),
            "surebets_count": len(opportunities),
            "opportunities": opportunities,
            "provider_status": self.get_provider_status(),
        }

    def get_provider_status(self) -> Dict[str, Any]:
        """Return provider diagnostics when supported."""
        if hasattr(self.provider, "get_provider_status"):
            return self.provider.get_provider_status()
        return {"mode": self.provider_mode, "configured": True}


service = OpportunityService()
