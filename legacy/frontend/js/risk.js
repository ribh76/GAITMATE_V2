export function scoreToFallbackLabel(score) {
  if (score >= 85) return "High";
  if (score >= 65) return "Elevated";
  if (score >= 45) return "Monitor";
  return "Healthy";
}

export function tintForColor(color) {
  const tints = {
    "#2a8a5f": "#e7f3ed",
    "#8fbf4f": "#eef6df",
    "#d9a32a": "#faf1dc",
    "#e08a4a": "#fbeede",
    "#d65a4a": "#fbe8e4",
  };
  return tints[color] || "#e7f3ed";
}
