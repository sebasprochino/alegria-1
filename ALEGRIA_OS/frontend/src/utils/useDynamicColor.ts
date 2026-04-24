import { useEffect } from 'react';

/**
 * Converts an arbitrary color string into a safe CSS class name.
 * e.g.  "#A29BFE"  →  "dc-_A29BFE"
 *        "rgb(1,2,3)" → "dc-rgb_1_2_3_"
 */
function colorToClassName(color: string): string {
  return 'dc-' + color.replace(/[^a-zA-Z0-9]/g, '_');
}

/**
 * useDynamicColor
 *
 * Injects a one-off <style> rule into <head> for the given color and returns
 * the generated class name. No inline style prop or .style assignment used —
 * the color lives entirely in the stylesheet, satisfying strict lint rules.
 */
export function useDynamicColor(color: string): string {
  const className = colorToClassName(color);

  useEffect(() => {
    const ruleId = `ds-rule-${className}`;
    if (document.getElementById(ruleId)) return; // already injected

    const tag = document.createElement('style');
    tag.id = ruleId;
    tag.textContent = `.${className}{background-color:${color};}`;
    document.head.appendChild(tag);
    // We intentionally never remove these rules: colors are finite and
    // re-injection on unmount/remount would cause a flash.
  }, [color, className]);

  return className;
}
