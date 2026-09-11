from flask import Flask, render_template, request, jsonify
from pydantic import ValidationError
from src.config import config
from src.services import service
from src.database import db
from src.calculators.stakes import StakeCalculator
from src.models import CalculationRequest

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

# Prime database with initial demo opportunities on startup. In API mode the
# user must refresh manually to preserve the monthly request quota.
if config.PROVIDER_MODE != "API":
    try:
        service.refresh_and_analyze_all()
    except Exception as e:
        print(f"Startup analysis warning: {e}")

# Mandatory Disclaimer text required across all views/footers
DISCLAIMER = (
    "Los cálculos son estimaciones matemáticas. Las cuotas pueden cambiar, "
    "existir límites de apuesta y variar las reglas de liquidación de cada operador. "
    "Verifica siempre que las cuotas sigan vigentes antes de apostar."
)


@app.context_processor
def inject_global_vars():
    """Inject global variables to all Jinja2 templates"""
    return {
        "disclaimer": DISCLAIMER,
        "provider_mode": config.PROVIDER_MODE
    }


# ==========================================
# WEB VIEW ROUTES
# ==========================================

@app.route("/")
def dashboard():
    """Main Dashboard View"""
    report = service.refresh_and_analyze_all() if config.PROVIDER_MODE != "API" else service.get_summary()
    opps = service.get_filtered_opportunities()

    top_opportunity = opps[0] if opps else None
    avg_roi = round(sum(o["roi"] for o in opps) / len(opps), 2) if opps else 0.0

    return render_template(
        "dashboard.html",
        summary=report,
        top_opportunity=top_opportunity,
        avg_roi=avg_roi,
        opportunities=opps[:5]
    )


@app.route("/surebets")
def surebets():
    """Surebet Analyzer View"""
    sport = request.args.get("sport", "all")
    min_roi = request.args.get("min_roi", type=float)
    bookmaker = request.args.get("bookmaker", "all")

    surebets_list = service.get_filtered_opportunities(
        sport=sport, min_roi=min_roi, bookmaker=bookmaker
    )
    return render_template("surebets.html", opportunities=surebets_list)


@app.route("/odds")
def odds_view():
    """Stored odds/events view for provider diagnostics."""
    events = db.get_events()
    return render_template("odds.html", events=events, provider_status=service.get_provider_status())


@app.route("/history")
def history():
    """History and Simulations View"""
    history_logs = db.get_history()
    return render_template("history.html", history=history_logs)


@app.route("/settings")
def settings():
    """System Settings View"""
    return render_template("settings.html", config=config)


# ==========================================
# LOCAL API ENDPOINTS
# ==========================================

@app.route("/api/events", methods=["GET"])
def api_events():
    """Get all events from provider"""
    events = service.provider.get_events() if config.PROVIDER_MODE != "API" else db.get_events()
    return jsonify({"success": True, "count": len(events), "events": events})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Fetch provider data, analyze surebets, and store the fresh snapshot."""
    if config.PROVIDER_MODE == "API" and not config.EXTERNAL_API_KEY:
        return jsonify({"success": False, "error": "EXTERNAL_API_KEY is required when PROVIDER_MODE=API"}), 400
    report = service.refresh_and_analyze_all()
    return jsonify({"success": True, "provider_mode": config.PROVIDER_MODE, "report": report})


@app.route("/api/account", methods=["GET"])
def api_account():
    """Get safe account/quota details from the active API provider."""
    if not hasattr(service.provider, "get_account"):
        return jsonify({"success": False, "error": "Account endpoint is only available in API mode"}), 400
    return jsonify({"success": True, "account": service.provider.get_account()})


@app.route("/api/bookmakers", methods=["GET"])
def api_bookmakers():
    """Get available bookmakers from the active API provider."""
    if not hasattr(service.provider, "get_bookmakers"):
        return jsonify({"success": False, "error": "Bookmakers endpoint is only available in API mode"}), 400
    bookmakers = service.provider.get_bookmakers()
    return jsonify({"success": True, "count": len(bookmakers), "bookmakers": bookmakers})


@app.route("/api/tournaments", methods=["GET"])
def api_tournaments():
    """Get OddsPapi tournaments for the configured sport."""
    if not hasattr(service.provider, "get_tournaments"):
        return jsonify({"success": False, "error": "Tournaments endpoint is only available in API mode"}), 400
    tournaments = service.provider.get_tournaments()
    query = request.args.get("q", "").lower().strip()
    if query:
        tournaments = [
            t for t in tournaments
            if query in str(t.get("tournamentName", "")).lower()
            or query in str(t.get("tournamentSlug", "")).lower()
            or query in str(t.get("categoryName", "")).lower()
            or query in str(t.get("categorySlug", "")).lower()
        ]
    return jsonify({"success": True, "count": len(tournaments), "tournaments": tournaments})


@app.route("/api/fixtures", methods=["GET"])
def api_fixtures():
    """Get upcoming OddsPapi fixtures for configured bookmakers."""
    if not hasattr(service.provider, "get_fixtures"):
        return jsonify({"success": False, "error": "Fixtures endpoint is only available in API mode"}), 400
    fixtures = service.provider.get_fixtures()
    return jsonify({"success": True, "count": len(fixtures), "fixtures": fixtures})


@app.route("/api/provider/status", methods=["GET"])
def api_provider_status():
    """Return safe diagnostics about the current provider and last refresh."""
    return jsonify({"success": True, "status": service.get_provider_status()})


@app.route("/api/surebets", methods=["GET"])
def api_surebets():
    """Get active Surebets with optional filters"""
    sport = request.args.get("sport")
    min_roi = request.args.get("min_roi", type=float)
    bookmaker = request.args.get("bookmaker")

    opps = service.get_filtered_opportunities(sport=sport, min_roi=min_roi, bookmaker=bookmaker)
    return jsonify({"success": True, "count": len(opps), "surebets": opps})


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    Surebet calculator endpoint for custom stake simulations.
    Body format:
    {
      "bankroll": 500,
      "odds": [2.15, 3.40, 3.60]
    }
    """
    data = request.get_json() or {}
    try:
        calc_request = CalculationRequest(**data)
    except ValidationError as exc:
        return jsonify({"success": False, "error": "Invalid calculation request", "details": exc.errors()}), 400

    bankroll = float(calc_request.bankroll)
    odds = [float(o) for o in calc_request.odds]

    if not odds or any(o <= 1.0 for o in odds):
        return jsonify({"success": False, "error": "Invalid odds provided. Odds must be > 1.0"}), 400

    res = StakeCalculator.calculate_surebet_stakes(bankroll, odds)
    res["currency"] = "S/"
    return jsonify({"success": True, "result": res})


if __name__ == "__main__":
    print("=" * 60)
    print(f"  SUREBET ANALYZER - Running in {config.PROVIDER_MODE} mode")
    print("  Access local server at http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=config.PORT, debug=config.FLASK_DEBUG)
