export function resolveIntent(input) {
  let transformed = input;

  // TRIGGERS (no routing)
  if (input.startsWith("r1")) {
    transformed = input.replace("r1", "resumí esto corto y directo");
  }

  if (input.startsWith("r2")) {
    transformed = input.replace("r2", "analizá esto en profundidad");
  }

  return transformed;
}
