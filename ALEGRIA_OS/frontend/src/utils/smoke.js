const SMOKE_PATTERNS = [
  "como ia",
  "es importante destacar",
  "en resumen",
  "sin duda",
  "en conclusión"
];

export function detectSmoke(text) {
  if (!text) return [];
  return SMOKE_PATTERNS.filter(p =>
    text.toLowerCase().includes(p)
  );
}
