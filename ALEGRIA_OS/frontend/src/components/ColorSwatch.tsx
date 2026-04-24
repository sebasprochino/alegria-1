import React from 'react';
import { useDynamicColor } from '../utils/useDynamicColor';

/**
 * ColorSwatch
 *
 * Displays a colored square using a dynamically-injected CSS class.
 * No `style` prop, no `ref`, no `.style` property access anywhere —
 * fully satisfies strict "no inline styles" lint rules.
 */
interface ColorSwatchProps {
  color: string;
  className?: string;
  title?: string;
}

export default function ColorSwatch({ color, className = '', title }: ColorSwatchProps) {
  const colorClass = useDynamicColor(color);

  return (
    <div
      className={`${colorClass} ${className}`.trim()}
      title={title ?? color}
      aria-label={title ?? color}
    />
  );
}
