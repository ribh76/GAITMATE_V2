import { getLatestLigamentData } from "./api.js";
import { scoreToFallbackLabel, tintForColor } from "./risk.js";

const details = {
  ATFL: {
    number: 1,
    name: "Anterior Talofibular Ligament",
    x: "56%",
    y: "54%",
  },
  CFL: {
    number: 2,
    name: "Calcaneofibular Ligament",
    x: "40%",
    y: "73%",
  },
  PTFL: {
    number: 3,
    name: "Posterior Talofibular Ligament",
    x: "33%",
    y: "57%",
  },
};

const DEMO_STATES = {
  healthy: {
    time: "demo healthy",
    ligaments: {
      ATFL: demoLigament(18, "#2a8a5f", 1, "Low Risk", "Within healthy range. Keep up the good work!"),
      CFL: demoLigament(20, "#2a8a5f", 1, "Low Risk", "Within healthy range. Keep up the good work!"),
      PTFL: demoLigament(16, "#2a8a5f", 1, "Low Risk", "Within healthy range. Keep up the good work!"),
    },
    overall: {
      level: 1,
      score: 20,
      label: "Healthy",
      color: "#2a8a5f",
      source: "Demo",
    },
  },
  moderate: {
    time: "demo moderate",
    ligaments: {
      ATFL: demoLigament(56, "#d9a32a", 3, "Moderate Risk", "Keep monitoring and reduce high-impact movement."),
      CFL: demoLigament(52, "#d9a32a", 3, "Moderate Risk", "Keep monitoring and reduce high-impact movement."),
      PTFL: demoLigament(58, "#d9a32a", 3, "Moderate Risk", "Keep monitoring and reduce high-impact movement."),
    },
    overall: {
      level: 3,
      score: 55,
      label: "Monitor",
      color: "#d9a32a",
      source: "Demo",
    },
  },
  highRisk: {
    time: "demo high risk",
    ligaments: {
      ATFL: demoLigament(88, "#d65a4a", 5, "High Risk", "Reduce load and contact your clinician if symptoms persist."),
      CFL: demoLigament(84, "#d65a4a", 5, "High Risk", "Reduce load and contact your clinician if symptoms persist."),
      PTFL: demoLigament(86, "#d65a4a", 5, "High Risk", "Reduce load and contact your clinician if symptoms persist."),
    },
    overall: {
      level: 5,
      score: 85,
      label: "High Risk",
      color: "#d65a4a",
      source: "Demo",
    },
  },
};

const status = document.querySelector("[data-status]");
const pins = document.querySelector("[data-pins]");
const list = document.querySelector("[data-ligaments]");
const reading = document.querySelector("[data-reading]");
const overallScore = document.querySelector("[data-overall-score]");
const overallLabel = document.querySelector("[data-overall-label]");
const overallNote = document.querySelector("[data-overall-note]");
const marker = document.querySelector("[data-scale-marker]");
const demoButtons = document.querySelectorAll("[data-demo-state]");

let sensorPayload = null;
let demoState = null;

function demoLigament(score, color, level, label, advice) {
  return {
    average_strain: Math.round(score / 10),
    max_strain: Math.round(score / 8),
    gradient: level,
    variability: Number((level * 0.22).toFixed(2)),
    duration: Number((level * 0.2).toFixed(1)),
    loading: Number((score / 10).toFixed(1)),
    risk: {
      level,
      label,
      color,
      advice,
      score,
    },
  };
}

function formatNumber(value) {
  return Number(value || 0).toFixed(2).replace(/\.00$/, "");
}

function setActiveDemoButton(nextState) {
  demoButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.demoState === nextState);
  });
}

function renderPin(abbr, metric) {
  const item = details[abbr];
  const color = metric.risk.color;
  return `
    <span class="pin" style="left:${item.x}; top:${item.y}; background:${color};" title="${abbr}">
      ${item.number}
    </span>
  `;
}

function renderCard(abbr, metric) {
  const item = details[abbr];
  const color = metric.risk.color;
  const tint = tintForColor(color);
  const width = Math.min(100, Math.round(metric.risk.score));

  return `
    <article class="card ligament-card" style="border-left-color:${color}">
      <div class="row-between">
        <div>
          <div class="kicker">${abbr}</div>
          <h2 style="margin:4px 0 0; font-size:17px;">${item.name}</h2>
        </div>
        <span class="pill" style="color:${color}; background:${tint};">${metric.risk.label}</span>
      </div>
      <div class="progress" style="margin:16px 0 8px; color:${color};">
        <span style="width:${width}%"></span>
      </div>
      <div class="stat-row subtle" style="font-size:13px;">
        <span>Average ${formatNumber(metric.average_strain)}%</span>
        <span>Max ${formatNumber(metric.max_strain)}%</span>
        <span>Gradient ${formatNumber(metric.gradient)}</span>
        <span>Variability ${formatNumber(metric.variability)}</span>
        <span>Duration ${formatNumber(metric.duration)}</span>
        <span>Loading ${formatNumber(metric.loading)}</span>
      </div>
    </article>
  `;
}

function render(payload) {
  const ligaments = payload.ligaments || {};
  const overall = payload.overall || {};
  const color = overall.color || "#2a8a5f";
  const score = Math.min(100, Math.max(0, Math.round(overall.score || 0)));

  reading.textContent = demoState
    ? `Selected strain state: ${overall.label}.`
    : `Latest sensor reading: time ${payload.time}`;
  pins.innerHTML = Object.entries(ligaments).map(([abbr, metric]) => renderPin(abbr, metric)).join("");
  list.innerHTML = Object.entries(ligaments).map(([abbr, metric]) => renderCard(abbr, metric)).join("");
  overallScore.textContent = `${score}`;
  overallScore.style.color = color;
  overallLabel.textContent = overall.label || scoreToFallbackLabel(score);
  overallLabel.style.color = color;
  overallLabel.style.background = tintForColor(color);
  const highestRisk = Object.values(ligaments).sort((a, b) => b.risk.level - a.risk.level)[0]?.risk;
  const guidance = highestRisk?.level === 1
    ? "Within healthy range. Keep up the good work!"
    : highestRisk?.advice || "Within healthy range. Keep up the good work!";
  overallNote.textContent = `Current guidance: ${guidance}`;
  overallNote.style.background = tintForColor(color);
  marker.style.left = `${score}%`;
  marker.style.borderColor = color;
  status.textContent = demoState ? "Viewing selected strain state" : "Live · sensor connected";
}

demoButtons.forEach((button) => {
  button.addEventListener("click", () => {
    demoState = button.dataset.demoState;
    setActiveDemoButton(demoState);
    render(DEMO_STATES[demoState]);
  });
});

getLatestLigamentData()
  .then((payload) => {
    sensorPayload = payload;
    if (!demoState) {
      render(sensorPayload);
    }
  })
  .catch((error) => {
    status.textContent = "Sensor connection unavailable";
    list.innerHTML = `<p class="status-message error">${error.message}</p>`;
  });
