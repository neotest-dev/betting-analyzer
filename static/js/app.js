document.addEventListener("DOMContentLoaded", () => {
    console.log("Betting Opportunity Analyzer client initialized.");

    // Interactive Bankroll Calculator
    const bankrollInput = document.getElementById("bankroll-input");
    const bankrollDisplay = document.getElementById("bankroll-display");

    if (bankrollInput && bankrollDisplay) {
        bankrollInput.addEventListener("input", (e) => {
            const val = parseFloat(e.target.value) || 100;
            bankrollDisplay.textContent = `S/${val.toFixed(2)}`;
            updateCalculations(val);
        });
    }

    document.querySelectorAll("[data-bankroll]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById("calc-bankroll");
            if (input) input.value = button.getAttribute("data-bankroll") || "100";
        });
    });
});

function updateCalculations(bankroll) {
    const stakeElements = document.querySelectorAll("[data-stake-percentage]");
    stakeElements.forEach((el) => {
        const pct = parseFloat(el.getAttribute("data-stake-percentage")) || 0;
        const odds = parseFloat(el.getAttribute("data-odds")) || 0;
        const stakeVal = Math.round(bankroll * (pct / 100));
        el.textContent = `S/${stakeVal}`;

        if (odds > 0) {
            const row = el.closest("tr");
            if (row) {
                const payoutEl = row.querySelector(".payout-value");
                if (payoutEl) {
                    payoutEl.textContent = `S/${(stakeVal * odds).toFixed(2)}`;
                }
            }
        }
    });
}

// API Simulation Calculator Call
async function calculateCustomStake() {
    const bankroll = parseFloat(document.getElementById("calc-bankroll")?.value || 100);
    const oddsStr = document.getElementById("calc-odds")?.value || "2.15, 3.40, 3.60";
    const odds = oddsStr.split(",").map((o) => parseFloat(o.trim())).filter((o) => !isNaN(o));

    const resultBox = document.getElementById("calc-result-box");
    if (!resultBox) return;

    try {
        const response = await fetch("/api/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bankroll, odds, type: "surebet" })
        });

        const data = await response.json();
        if (data.success && data.result) {
            const res = data.result;
            let html = `<div class="panel-code">`;
            html += `<h4 class="${res.is_surebet ? 'text-emerald' : 'text-muted'} mb-sm">${res.is_surebet ? '¡Surebet Detectada!' : 'Sin Arbitraje'}</h4>`;
            html += `<p><strong>ROI:</strong> ${res.roi_percentage}%</p>`;
            html += `<p><strong>Beneficio Proyectado:</strong> S/${res.profit || 0}</p>`;
            if (res.stakes && res.stakes.length > 0) {
                html += `<ul class="mt-sm">`;
                res.stakes.forEach((s) => {
                    html += `<li>Cuota ${s.odds}: Stake S/${s.stake} (${s.percentage}%) - Retorno: S/${s.payout}</li>`;
                });
                html += `</ul>`;
            }
            html += `</div>`;
            resultBox.innerHTML = html;
        } else {
            resultBox.innerHTML = `<p class="text-danger">Error: ${data.error || 'Cálculo fallido'}</p>`;
        }
    } catch (err) {
        resultBox.innerHTML = `<p class="text-danger">Error de conexión con la API local.</p>`;
    }
}

async function refreshRealOdds() {
    const resultBox = document.getElementById("refresh-result-box");
    if (resultBox) {
        resultBox.innerHTML = `<div class="refresh-pending">Actualizando cuotas reales. Esto consume 1 request de OddsPapi.</div>`;
    }

    try {
        const response = await fetch("/api/refresh", { method: "POST" });
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || "No se pudo actualizar");
        }
        const report = data.report || {};
        if (resultBox) {
            resultBox.innerHTML = `<div class="refresh-success">Actualización completada: ${report.total_events || 0} eventos y ${report.total_opportunities || 0} oportunidades. Recargando dashboard...</div>`;
        }
        window.setTimeout(() => window.location.reload(), 900);
    } catch (err) {
        if (resultBox) {
            resultBox.innerHTML = `<p class="text-danger">Error al actualizar cuotas reales. Revisa tu API key y cuota disponible.</p>`;
        }
    }
}
