# AGENTS.md - Technical Architecture & Developer Guide for AI Assistants

This document serves as the authoritative guide for AI coding assistants (e.g. Gemini, ChatGPT, Claude, Cursor, Windsurf, Antigravity) working on the `betting-analyzer` codebase.

---

## 🎯 System Overview & Mission

`betting-analyzer` is a Python 3.10+ web application designed to analyze sports betting data, calculate mathematical probabilities, and identify strategic opportunities without placing automated bets.

### Core Modules:
1. **Surebet Arbitrage Analyzer**: Identifies risk-free arbitrage opportunities where the sum of inverse odds is $< 1.0$, calculates optimal stake allocation using high-precision `Decimal` math, and computes ROI.
2. **Value Betting Analyzer**: Evaluates bookmaker odds against internal statistical probability models (e.g. Poisson distribution, historical averages) to calculate expected edge (`Edge %`) and optimal bankroll allocation via the Kelly Criterion.
3. **Range & Gap Strategy Analyzer**: Analyzes market coverage gaps (gaps between line thresholds such as goals or corners across different bookmakers) and calculates Poisson probability of hit/miss.
4. **Statistical Engine**: Evaluates team statistics (mean, median, standard deviation, trends) for goals and corners.

---

## 🛠️ Technology Stack

* **Language**: Python 3.10+
* **Web Framework**: Flask 3.0+
* **Data Validation & Schemas**: Pydantic 2.5+
* **Data Processing & Analytics**: Pandas, NumPy, SciPy
* **Database**: SQLite (`betting_analyzer.db`) via native `sqlite3` driver
* **Testing**: Pytest 8.0+
* **Frontend**: Flask Jinja2 templates, Vanilla HTML5/CSS3 (Glassmorphism), Vanilla JavaScript ES6+ (No external heavy JS frameworks)

---

## 📁 Repository Structure & Directory Roles

```text
betting-analyzer/
├── app.py                      # Flask Application Entrypoint & REST API / HTML Routes
├── requirements.txt            # Python Dependencies
├── README.md                   # User-facing Documentation & Setup Guide
├── AGENTS.md                   # AI Assistant Architecture Guide (This File)
├── .env.example                # Template for Environment Variables
├── .gitignore                  # Git Exclusion Rules (.venv, .env, *.db, cache)
│
├── src/                        # Core Python Package
│   ├── config.py               # Settings & Environment Loader (dotenv)
│   ├── database.py             # SQLite DDL, Schema Migrations & Data Persistence
│   ├── models.py               # Pydantic Schemas (Event, Market, Odd, Opportunity)
│   ├── services.py             # Application Orchestrator / Service Layer
│   │
│   ├── providers/              # Odds Data Providers (Strategy Pattern)
│   │   ├── base_provider.py    # Abstract Class: OddsProvider
│   │   ├── demo_provider.py    # Local JSON Provider (Offline DEMO Mode)
│   │   └── api_provider.py     # External API Provider (OddsPapi integration)
│   │
│   ├── odds/                   # Odds Processing Pipeline
│   │   ├── normalizer.py       # Converts raw API/JSON structures to internal domain models
│   │   └── matcher.py          # Matches selections and extracts top market odds
│   │
│   ├── analyzers/              # Opportunity Detection Engines
│   │   ├── surebet.py          # Arbitrage Detection Engine
│   │   ├── value_betting.py    # Edge % & Value Detection Engine
│   │   └── range_strategy.py   # Coverage & Gap Detection Engine
│   │
│   ├── calculators/            # Pure Mathematical Calculators
│   │   ├── stakes.py           # Surebet Stake Allocator & Fractional Kelly Criterion
│   │   ├── probability.py      # Implied Probability & Poisson Matrix Generator
│   │   └── roi.py              # Expected Value (EV) & ROI Calculators
│   │
│   └── statistics/             # Historical Statistical Models
│       ├── goals.py            # Goal Distributions (Poisson, Mean, StdDev)
│       ├── corners.py          # Corner Statistics Engine
│       └── trends.py           # Team Form & Streak Analyzers
│
├── data/                       # Sample & Mock Data Sets
│   ├── sample_odds.json        # Offline Mock Bookmaker Odds
│   └── historical_matches.json # Historical Match Data for Statistical Calibration
│
├── templates/                  # Jinja2 HTML Vistas (Dashboard, Surebets, Valuebets, etc.)
├── static/                     # CSS (Glassmorphism) and Vanilla JS (Charts, Dynamic Filters)
└── tests/                      # Pytest Automated Test Suite
```

---

## 🧮 Core Mathematical Formulas & Conventions

### 1. Surebet Arbitrage Engine (`src/analyzers/surebet.py`, `src/calculators/stakes.py`)
* **Arbitrage Condition**:
  $$\text{Inverse Sum} = \sum_{i=1}^{n} \frac{1}{\text{Odd}_i} < 1.0$$
* **ROI Percentage**:
  $$\text{ROI} = \left( \frac{1}{\text{Inverse Sum}} - 1 \right) \times 100$$
* **Stake Allocation** (for selection $i$ given total bankroll $S$):
  $$S_i = S \times \frac{1 / \text{Odd}_i}{\text{Inverse Sum}}$$
  *(Note: Stake calculations must maintain `Decimal` precision to avoid rounding errors).*

### 2. Value Bet Engine (`src/analyzers/value_betting.py`, `src/calculators/stakes.py`)
* **Expected Edge (Edge %)**:
  $$\text{Edge \%} = (P_{\text{estimated}} \times \text{Odd} - 1) \times 100$$
  *Where $P_{\text{estimated}}$ is derived from Poisson / statistical historical distribution.*
* **Kelly Criterion Stake**:
  $$f^* = \frac{P_{\text{estimated}} \times \text{Odd} - 1}{\text{Odd} - 1}$$
  *(Fractional Kelly is often applied, e.g. $0.25 \times f^*$, to mitigate bankroll variance).*

### 3. Range Strategy Engine (`src/analyzers/range_strategy.py`)
* Evaluates overlapping and non-overlapping lines across operators (e.g. Over 2.5 goals at Bookmaker A vs Under 3.5 goals at Bookmaker B).
* Calculates the Poisson probability of landing in the "gap" (e.g. exactly 3 goals).

---

## 🔑 Key Principles & Rules for AI Development

When modifying or extending this repository, AI agents MUST follow these guidelines:

1. **Strict Architectural Separation**:
   * **Route Handlers** in `app.py` must only call orchestrator methods in `src/services.py` or database helper functions. Do NOT write business or calculation logic inside Flask route functions.
   * **Calculators** in `src/calculators/` must be pure functions (no database queries or HTTP requests inside calculators).
   * **Providers** in `src/providers/` must return normalized models or `Event` instances.

2. **Preserve DEMO Mode**:
   * Offline execution using `data/sample_odds.json` is a core feature. Any changes to domain schemas in `src/models.py` must be reflected in `data/sample_odds.json` or handled gracefully by `DemoProvider`.

3. **Data Schemas & Validation**:
   * Use Pydantic models in `src/models.py` for type safety and validation. Avoid returning arbitrary nested Python dictionaries across module boundaries.

4. **Environment Variables & Secrets**:
   * Never hardcode API keys or database paths. Always fetch configuration via `src/config.py` (which loads from `.env`).

5. **Testing Verification**:
   * Before considering any code task complete, execute the test suite:
     ```bash
     pytest -q
     ```
   * Add test coverage in `tests/` for any new calculator, analyzer, or provider feature.
