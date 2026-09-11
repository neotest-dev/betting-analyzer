# AGENTS.md - Technical Architecture & Developer Guide

This document serves as the authoritative guide for AI coding assistants working on the `betting-analyzer` codebase.

---

## 🎯 System Overview & Mission

`betting-analyzer` is a focused Python 3.10+ web application dedicated exclusively to **Surebet (Arbitrage) Analysis**.

It detects **cross-bookmaker arbitrage opportunities** where:
1. The sum of inverse odds across different bookmakers is `< 1.0` (mathematical arbitrage)
2. **Each selection must come from a DIFFERENT bookmaker** — same-bookmaker surebets are false positives and are rejected

### Core Module:
**Surebet Arbitrage Analyzer**: Identifies risk-free arbitrage opportunities by comparing best odds across multiple bookmakers, validates cross-bookmaker diversity, calculates optimal stake allocation using high-precision `Decimal` math, and computes ROI.

---

## 🛠️ Technology Stack

* **Language**: Python 3.10+
* **Web Framework**: Flask 3.0+
* **Data Validation & Schemas**: Pydantic 2.5+
* **Data Processing**: Pandas, NumPy (available but minimal use)
* **Database**: SQLite (`betting_analyzer.db`) via native `sqlite3` driver
* **Testing**: Pytest 8.0+
* **Frontend**: Flask Jinja2 templates, Vanilla HTML5/CSS3 (Glassmorphism), Vanilla JavaScript ES6+

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
│   ├── models.py               # Pydantic Schemas (Event, BookmakerOdds, Opportunity)
│   ├── services.py             # Application Orchestrator / Service Layer
│   │
│   ├── providers/              # Odds Data Providers (Strategy Pattern)
│   │   ├── base_provider.py    # Abstract Class: OddsProvider
│   │   ├── demo_provider.py    # Local JSON Provider (Offline DEMO Mode)
│   │   └── api_provider.py     # External API Provider (OddsPapi integration)
│   │
│   ├── odds/                   # Odds Processing Pipeline
│   │   ├── normalizer.py       # Converts raw API/JSON structures to internal domain models
│   │   └── matcher.py          # Matches selections and extracts top market odds per bookmaker
│   │
│   ├── analyzers/              # Opportunity Detection Engine
│   │   └── surebet.py          # Arbitrage Detection Engine (cross-bookmaker validation)
│   │
│   └── calculators/            # Pure Mathematical Calculators
│       ├── stakes.py           # Surebet Stake Allocator (Decimal precision)
│       └── roi.py              # ROI Calculator
│
├── data/                       # Sample & Mock Data Sets
│   └── sample_odds.json        # Offline Mock Bookmaker Odds (multi-bookmaker per event)
│
├── templates/                  # Jinja2 HTML Views
│   ├── base.html               # Base layout (navbar: Dashboard, Surebets, Cuotas, Historial, Ajustes)
│   ├── dashboard.html          # Main dashboard with surebet metrics and calculator
│   ├── surebets.html           # Surebet detail view with cross-bookmaker badge
│   ├── odds.html               # Provider diagnostics / raw odds view
│   ├── history.html            # Simulation history
│   └── settings.html           # Configuration settings
│
├── static/                     # CSS (Glassmorphism) and Vanilla JS
└── tests/                      # Pytest Automated Test Suite
    ├── test_surebet.py         # Surebet analyzer tests (including diversity validation)
    ├── test_calculators.py     # StakeCalculator and ROICalculator tests
    └── test_api_provider.py    # OddsPapi API provider tests
```

---

## 🧮 Core Mathematical Formulas

### Surebet Arbitrage Engine (`src/analyzers/surebet.py`, `src/calculators/stakes.py`)

**Arbitrage Condition:**
$$\text{Inverse Sum} = \sum_{i=1}^{n} \frac{1}{\text{Odd}_i} < 1.0$$

**AND** each `Odd_i` must come from a **different bookmaker** (cross-bookmaker requirement).

**ROI Percentage:**
$$\text{ROI} = \left( \frac{1}{\text{Inverse Sum}} - 1 \right) \times 100$$

**Stake Allocation** (for selection $i$ given total bankroll $S$):
$$S_i = \frac{S}{\text{Odd}_i \times \text{Inverse Sum}}$$

*(Stake calculations use `Decimal` precision to avoid rounding errors.)*

---

## 🔑 Key Principles & Rules for AI Development

1. **Strict Architectural Separation**:
   * **Route Handlers** in `app.py` must only call orchestrator methods in `src/services.py`. No business logic in Flask routes.
   * **Calculators** in `src/calculators/` must be pure functions (no database queries or HTTP requests).
   * **Providers** in `src/providers/` must return normalized event dictionaries.

2. **Cross-Bookmaker Validation is Mandatory**:
   * `SurebetAnalyzer.analyze_event()` must always reject opportunities where all best odds come from the same bookmaker.
   * The check `len(set(bookies_list)) < 2` is a hard rejection, not configurable.

3. **DEMO Mode**:
   * Offline execution using `data/sample_odds.json` is a core feature.
   * The JSON must contain events with **multiple distinct bookmakers** so cross-bookmaker surebets can be found in demo mode.

4. **Data Schemas & Validation**:
   * Use Pydantic models in `src/models.py` for type safety. Avoid arbitrary nested dicts across module boundaries.

5. **Environment Variables & Secrets**:
   * Never hardcode API keys or database paths. Always fetch via `src/config.py`.

6. **Testing**:
   * Before considering any task complete, run `pytest -q`.
   * `test_surebet_rejected_same_bookmaker` and `test_surebet_accepted_cross_bookmaker` are critical regression tests — they must always pass.

---

## 🌐 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Dashboard view |
| `GET` | `/surebets` | Surebet list view (filters: sport, min_roi) |
| `GET` | `/odds` | Provider diagnostics / raw odds |
| `GET` | `/history` | Simulation history |
| `GET` | `/settings` | Configuration view |
| `POST` | `/api/refresh` | Fetch provider data and re-analyze |
| `GET` | `/api/surebets` | JSON: active surebets (filters: sport, min_roi, bookmaker) |
| `POST` | `/api/calculate` | JSON: custom stake simulation `{bankroll, odds[]}` |
| `GET` | `/api/events` | JSON: stored events |
| `GET` | `/api/provider/status` | JSON: provider diagnostics |
| `GET` | `/api/account` | JSON: API account/quota info (API mode only) |
| `GET` | `/api/bookmakers` | JSON: available bookmakers (API mode only) |
| `GET` | `/api/tournaments` | JSON: OddsPapi tournaments (API mode only) |
| `GET` | `/api/fixtures` | JSON: upcoming fixtures (API mode only) |
