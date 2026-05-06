export function IllustrationMediGenius() {
  return (
    <svg viewBox="0 0 200 130" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
      <defs>
        <linearGradient id="mg-bg" x1="0" y1="0" x2="200" y2="130" gradientUnits="userSpaceOnUse">
          <stop stopColor="#0d1f3c" />
          <stop offset="1" stopColor="#071426" />
        </linearGradient>
        <linearGradient id="mg-node-a" x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#3b82f6" stopOpacity="0.8" />
          <stop offset="1" stopColor="#06b6d4" stopOpacity="0.8" />
        </linearGradient>
        <filter id="mg-glow">
          <feGaussianBlur stdDeviation="2.5" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      <rect width="200" height="130" fill="url(#mg-bg)" />

      {/* Soft radial glow */}
      <circle cx="100" cy="65" r="55" fill="rgba(59,130,246,0.04)" />

      {/* Neural network connections */}
      <line x1="100" y1="28" x2="72" y2="50" stroke="rgba(59,130,246,0.2)" strokeWidth="1" />
      <line x1="100" y1="28" x2="128" y2="50" stroke="rgba(59,130,246,0.2)" strokeWidth="1" />
      <line x1="72" y1="50" x2="58" y2="76" stroke="rgba(6,182,212,0.18)" strokeWidth="1" />
      <line x1="72" y1="50" x2="100" y2="78" stroke="rgba(6,182,212,0.18)" strokeWidth="1" />
      <line x1="128" y1="50" x2="142" y2="76" stroke="rgba(6,182,212,0.18)" strokeWidth="1" />
      <line x1="128" y1="50" x2="100" y2="78" stroke="rgba(6,182,212,0.18)" strokeWidth="1" />
      <line x1="58" y1="76" x2="80" y2="100" stroke="rgba(34,197,94,0.15)" strokeWidth="1" />
      <line x1="142" y1="76" x2="120" y2="100" stroke="rgba(34,197,94,0.15)" strokeWidth="1" />
      <line x1="100" y1="78" x2="80" y2="100" stroke="rgba(34,197,94,0.15)" strokeWidth="1" />
      <line x1="100" y1="78" x2="120" y2="100" stroke="rgba(34,197,94,0.15)" strokeWidth="1" />

      {/* Nodes */}
      <circle cx="100" cy="28" r="7" fill="url(#mg-node-a)" filter="url(#mg-glow)" />
      <circle cx="100" cy="28" r="4" fill="#3b82f6" />

      <circle cx="72" cy="50" r="5.5" fill="rgba(6,182,212,0.25)" stroke="#06b6d4" strokeWidth="1.2" />
      <circle cx="128" cy="50" r="5.5" fill="rgba(6,182,212,0.25)" stroke="#06b6d4" strokeWidth="1.2" />

      <circle cx="58" cy="76" r="5" fill="rgba(59,130,246,0.2)" stroke="#3b82f6" strokeWidth="1.2" />
      <circle cx="100" cy="78" r="5" fill="rgba(59,130,246,0.2)" stroke="#3b82f6" strokeWidth="1.2" />
      <circle cx="142" cy="76" r="5" fill="rgba(59,130,246,0.2)" stroke="#3b82f6" strokeWidth="1.2" />

      <circle cx="80" cy="100" r="5" fill="rgba(34,197,94,0.25)" stroke="#22c55e" strokeWidth="1.2" />
      <circle cx="120" cy="100" r="5" fill="rgba(34,197,94,0.25)" stroke="#22c55e" strokeWidth="1.2" />

      {/* Chat bubble left */}
      <rect x="14" y="42" width="36" height="20" rx="7" fill="rgba(59,130,246,0.1)" stroke="rgba(59,130,246,0.3)" strokeWidth="1" />
      <rect x="18" y="47" width="22" height="3" rx="1.5" fill="rgba(59,130,246,0.5)" />
      <rect x="18" y="53" width="14" height="3" rx="1.5" fill="rgba(59,130,246,0.3)" />

      {/* Chat bubble right */}
      <rect x="150" y="60" width="36" height="20" rx="7" fill="rgba(6,182,212,0.10)" stroke="rgba(6,182,212,0.3)" strokeWidth="1" />
      <rect x="154" y="65" width="22" height="3" rx="1.5" fill="rgba(6,182,212,0.5)" />
      <rect x="154" y="71" width="14" height="3" rx="1.5" fill="rgba(6,182,212,0.3)" />
    </svg>
  );
}
