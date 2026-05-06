export function IllustrationMediScan() {
  return (
    <svg viewBox="0 0 200 130" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
      <defs>
        <linearGradient id="ms-bg" x1="0" y1="0" x2="200" y2="130" gradientUnits="userSpaceOnUse">
          <stop stopColor="#160d28" />
          <stop offset="1" stopColor="#0d0818" />
        </linearGradient>
        <linearGradient id="ms-beam" x1="30" y1="0" x2="170" y2="0" gradientUnits="userSpaceOnUse">
          <stop stopColor="rgba(168,85,247,0)" />
          <stop offset="0.5" stopColor="rgba(168,85,247,0.75)" />
          <stop offset="1" stopColor="rgba(168,85,247,0)" />
        </linearGradient>
      </defs>

      <rect width="200" height="130" fill="url(#ms-bg)" />
      <circle cx="100" cy="65" r="55" fill="rgba(168,85,247,0.04)" />

      {/* Pill */}
      <rect x="64" y="38" width="72" height="53" rx="26" fill="rgba(168,85,247,0.1)" stroke="rgba(168,85,247,0.4)" strokeWidth="1.8" />
      <line x1="100" y1="38" x2="100" y2="91" stroke="rgba(168,85,247,0.35)" strokeWidth="1.5" />
      <rect x="64" y="38" width="36" height="53" rx="26" fill="rgba(168,85,247,0.18)" />

      {/* Scan beam */}
      <rect x="30" y="63" width="140" height="2.5" rx="1.25" fill="url(#ms-beam)" />

      {/* Scan corner brackets */}
      <path d="M44 49 L44 38 L55 38" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" />
      <path d="M156 49 L156 38 L145 38" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" />
      <path d="M44 80 L44 91 L55 91" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" />
      <path d="M156 80 L156 91 L145 91" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" />

      {/* Data dots on left */}
      <circle cx="22" cy="50" r="4" fill="rgba(34,197,94,0.3)" stroke="#22c55e" strokeWidth="1.1" />
      <circle cx="22" cy="65" r="3" fill="rgba(249,115,22,0.3)" stroke="#f97316" strokeWidth="1.1" />
      <circle cx="22" cy="79" r="4" fill="rgba(168,85,247,0.3)" stroke="#a855f7" strokeWidth="1.1" />
      <rect x="30" y="47" width="18" height="3" rx="1.5" fill="rgba(34,197,94,0.3)" />
      <rect x="30" y="62" width="12" height="3" rx="1.5" fill="rgba(249,115,22,0.3)" />
      <rect x="30" y="76" width="16" height="3" rx="1.5" fill="rgba(168,85,247,0.3)" />

      {/* Glow spot on pill-center */}
      <circle cx="100" cy="65" r="7" fill="rgba(168,85,247,0.15)" />
    </svg>
  );
}
