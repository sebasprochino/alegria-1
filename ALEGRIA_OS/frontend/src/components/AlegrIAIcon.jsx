import React from 'react';

/**
 * AlegrIAIcon
 * Representación visual premium del icono de ALEGR-IA.
 * Basado en el Anima Chordata con estética squircle y gradientes vibrantes.
 */
const AlegrIAIcon = ({ 
  size = 64, 
  className = "",
  animate = true
}) => {
  return (
    <div 
      className={`relative inline-block ${className}`}
      style={{ width: size, height: size }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="drop-shadow-2xl transition-transform duration-500 hover:scale-105"
      >
        <defs>
          <linearGradient id="alegriaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#8E54FF">
              {animate && (
                <animate 
                  attributeName="stop-color" 
                  values="#8E54FF; #7030FF; #8E54FF" 
                  dur="4s" 
                  repeatCount="indefinite" 
                />
              )}
            </stop>
            <stop offset="100%" stopColor="#FF52AF">
              {animate && (
                <animate 
                  attributeName="stop-color" 
                  values="#FF52AF; #FF2E95; #FF52AF" 
                  dur="4s" 
                  repeatCount="indefinite" 
                />
              )}
            </stop>
          </linearGradient>
          
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Fondo Squircle con radio suave */}
        <rect
          x="0"
          y="0"
          width="100"
          height="100"
          rx="30"
          fill="url(#alegriaGradient)"
        />

        {/* Estrella central: Representa el Anima Chordata */}
        <path
          d="M50 25C50 38.8071 61.1929 50 75 50C61.1929 50 50 61.1929 50 75C50 61.1929 38.8071 50 25 50C38.8071 50 50 38.8071 50 25Z"
          fill="white"
          filter="url(#glow)"
        >
          {animate && (
            <animateTransform
              attributeName="transform"
              type="scale"
              values="1; 1.05; 1"
              dur="3s"
              repeatCount="indefinite"
              additive="sum"
              from="50 50"
              to="50 50"
            />
          )}
        </path>

        {/* Brillo superior derecho */}
        <circle cx="72" cy="28" r="4" fill="white">
          {animate && (
            <animate 
              attributeName="opacity" 
              values="1; 0.5; 1" 
              dur="2s" 
              repeatCount="indefinite" 
            />
          )}
        </circle>

        {/* Brillo inferior izquierdo */}
        <circle cx="28" cy="72" r="5" fill="white">
          {animate && (
            <animate 
              attributeName="opacity" 
              values="1; 0.7; 1" 
              dur="2.5s" 
              repeatCount="indefinite" 
            />
          )}
        </circle>
      </svg>
    </div>
  );
};

export default AlegrIAIcon;
