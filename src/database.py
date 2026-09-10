import sqlite3
import json
from typing import List, Dict, Any, Optional
from src.config import config

class DatabaseManager:
    """SQLite Database Manager for Betting Opportunity Analyzer"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with dict-like row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create database tables if they do not exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Events Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    sport TEXT NOT NULL,
                    league TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    market TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Odds Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS odds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    bookmaker_name TEXT NOT NULL,
                    bookmaker_country TEXT,
                    odds_data TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(event_id) REFERENCES events(event_id)
                )
            """)

            # Opportunities Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    opportunity_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL, -- 'surebet', 'valuebet', 'range'
                    event_id TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    league TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    market TEXT NOT NULL,
                    roi REAL NOT NULL,
                    probability REAL,
                    details TEXT NOT NULL, -- JSON string
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Statistics Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    avg_goals REAL,
                    avg_corners REAL,
                    avg_cards REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id TEXT NOT NULL,
                    action TEXT NOT NULL, -- 'analyzed', 'simulated', 'saved'
                    bankroll REAL,
                    stake REAL,
                    expected_return REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_events(self, events: List[Dict[str, Any]]):
        """Save standard events and their odds to DB"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for event in events:
                cursor.execute("""
                    INSERT OR REPLACE INTO events (event_id, sport, league, home_team, away_team, market, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event["event_id"],
                    event["sport"],
                    event["league"],
                    event["home_team"],
                    event["away_team"],
                    event["market"],
                    event["timestamp"]
                ))

                cursor.execute("DELETE FROM odds WHERE event_id = ?", (event["event_id"],))

                for bm in event.get("bookmakers", []):
                    cursor.execute("""
                        INSERT INTO odds (event_id, bookmaker_name, bookmaker_country, odds_data)
                        VALUES (?, ?, ?, ?)
                    """, (
                        event["event_id"],
                        bm["name"],
                        bm.get("country", "Global"),
                        json.dumps(bm["odds"])
                    ))
            conn.commit()

    def replace_events(self, events: List[Dict[str, Any]]):
        """Replace stored events and odds with a fresh provider snapshot."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM odds")
            cursor.execute("DELETE FROM events")
            for event in events:
                cursor.execute("""
                    INSERT OR REPLACE INTO events (event_id, sport, league, home_team, away_team, market, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event["event_id"],
                    event["sport"],
                    event["league"],
                    event["home_team"],
                    event["away_team"],
                    event["market"],
                    event["timestamp"]
                ))

                for bm in event.get("bookmakers", []):
                    cursor.execute("""
                        INSERT INTO odds (event_id, bookmaker_name, bookmaker_country, odds_data)
                        VALUES (?, ?, ?, ?)
                    """, (
                        event["event_id"],
                        bm["name"],
                        bm.get("country", "Global"),
                        json.dumps(bm["odds"])
                    ))
            conn.commit()

    def clear_snapshot(self):
        """Clear current events, odds, and opportunities snapshot."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM opportunities")
            cursor.execute("DELETE FROM odds")
            cursor.execute("DELETE FROM events")
            conn.commit()

    def replace_opportunities(self, opportunities: List[Dict[str, Any]]):
        """Replace the current opportunity snapshot with new analysis results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM opportunities")
            for opp in opportunities:
                cursor.execute("""
                    INSERT OR REPLACE INTO opportunities
                    (opportunity_id, type, event_id, sport, league, home_team, away_team, market, roi, probability, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    opp["opportunity_id"],
                    opp["type"],
                    opp["event_id"],
                    opp["sport"],
                    opp["league"],
                    opp["home_team"],
                    opp["away_team"],
                    opp["market"],
                    opp["roi"],
                    opp.get("probability", 0.0),
                    json.dumps(opp.get("details", {}))
                ))
            conn.commit()

    def save_opportunities(self, opportunities: List[Dict[str, Any]]):
        """Save analyzed opportunities to SQLite"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for opp in opportunities:
                cursor.execute("""
                    INSERT OR REPLACE INTO opportunities 
                    (opportunity_id, type, event_id, sport, league, home_team, away_team, market, roi, probability, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    opp["opportunity_id"],
                    opp["type"],
                    opp["event_id"],
                    opp["sport"],
                    opp["league"],
                    opp["home_team"],
                    opp["away_team"],
                    opp["market"],
                    opp["roi"],
                    opp.get("probability", 0.0),
                    json.dumps(opp.get("details", {}))
                ))
            conn.commit()

    def get_opportunities(self, opp_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve active opportunities from SQLite"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if opp_type:
                cursor.execute("SELECT * FROM opportunities WHERE type = ? ORDER BY roi DESC", (opp_type,))
            else:
                cursor.execute("SELECT * FROM opportunities ORDER BY roi DESC")
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item["details"] = json.loads(item["details"])
                results.append(item)
            return results

    def count_events(self) -> int:
        """Return number of stored events."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            return int(cursor.fetchone()[0])

    def get_events(self) -> List[Dict[str, Any]]:
        """Return stored events with their bookmakers and odds."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY timestamp ASC")
            rows = cursor.fetchall()
            events = []
            for row in rows:
                event = dict(row)
                cursor.execute("SELECT bookmaker_name, bookmaker_country, odds_data FROM odds WHERE event_id = ?", (event["event_id"],))
                event["bookmakers"] = [
                    {
                        "name": odds_row["bookmaker_name"],
                        "country": odds_row["bookmaker_country"],
                        "odds": json.loads(odds_row["odds_data"]),
                    }
                    for odds_row in cursor.fetchall()
                ]
                events.append(event)
            return events

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve calculation/simulation history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.*, o.sport, o.league, o.home_team, o.away_team, o.market, o.type
                FROM history h
                JOIN opportunities o ON h.opportunity_id = o.opportunity_id
                ORDER BY h.created_at DESC
            """)
            return [dict(r) for r in cursor.fetchall()]

db = DatabaseManager()
