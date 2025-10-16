import React from "react";
import "./WaveLogo.css";

const WaveLogo = () => {
    return (
        <svg
        className="logo-svg"
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        >
        {/* Outer circle with gradient */}
        <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: "#3dd9d0", stopOpacity: 1 }} />
            <stop
                offset="100%"
                style={{ stopColor: "#2caaa8", stopOpacity: 1 }}
            />
            </linearGradient>
            <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop
                offset="0%"
                style={{ stopColor: "#ffffff", stopOpacity: 0.9 }}
            />
            <stop offset="50%" style={{ stopColor: "#ffffff", stopOpacity: 1 }} />
            <stop
                offset="100%"
                style={{ stopColor: "#ffffff", stopOpacity: 0.9 }}
            />
            </linearGradient>
        </defs>

        {/* Background circle */}
        <circle cx="100" cy="100" r="95" fill="url(#logoGradient)" />

        {/* Stylized "W" made of waves */}
        <path
            d="M 40 80 Q 50 100, 60 80 T 80 80"
            stroke="url(#waveGradient)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
        />
        <path
            d="M 70 80 Q 80 100, 90 80 T 110 80"
            stroke="url(#waveGradient)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
        />
        <path
            d="M 100 80 Q 110 100, 120 80 T 140 80"
            stroke="url(#waveGradient)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
        />
        <path
            d="M 130 80 Q 140 100, 150 80 T 170 80"
            stroke="url(#waveGradient)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
        />

        {/* Wave pattern at bottom */}
        <path
            d="M 30 120 Q 50 110, 70 120 T 110 120 T 150 120 T 190 120"
            stroke="url(#waveGradient)"
            strokeWidth="6"
            fill="none"
            strokeLinecap="round"
            opacity="0.7"
        />
        <path
            d="M 20 135 Q 45 125, 70 135 T 120 135 T 170 135"
            stroke="url(#waveGradient)"
            strokeWidth="5"
            fill="none"
            strokeLinecap="round"
            opacity="0.5"
        />
        </svg>
    );
};

export default WaveLogo;
