import { getHealth } from "./api.js";

const status = document.querySelector("[data-health-status]");

if (status) {
  getHealth()
    .then(() => {
      status.textContent = "Live · sensor connected";
    })
    .catch(() => {
      status.textContent = "Sensor connection unavailable";
    });
}
