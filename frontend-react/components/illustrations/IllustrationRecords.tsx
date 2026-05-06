export function IllustrationRecords() {
  return (
    <svg viewBox="0 0 200 130" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
      <defs>
        <linearGradient id="rec-bg" x1="0" y1="0" x2="200" y2="130" gradientUnits="userSpaceOnUse">
          <stop stopColor="#0d2018" />
          <stop offset="1" stopColor="#071410" />
        </linearGradient>
      </defs>

      <rect width="200" height="130" fill="url(#rec-bg)" />
      <circle cx="100" cy="65" r="55" fill="rgba(34,197,94,0.04)" />

      {/* Clipboard body */}
      <rect x="56" y="25" width="88" height="80" rx="9" fill="rgba(34,197,94,0.07)" stroke="rgba(34,197,94,0.25)" strokeWidth="1.5" />
      {/* Clipboard clip */}
      <rect x="78" y="17" width="44" height="14" rx="7" fill="rgba(34,197,94,0.14)" stroke="rgba(34,197,94,0.3)" strokeWidth="1.2" />

      {/* Lines */}
      <rect x="68" y="48" width="64" height="3.5" rx="1.75" fill="rgba(34,197,94,0.35)" />
      <rect x="68" y="58" width="48" height="3.5" rx="1.75" fill="rgba(34,197,94,0.22)" />
      <rect x="68" y="68" width="56" height="3.5" rx="1.75" fill="rgba(34,197,94,0.22)" />
      <rect x="68" y="78" width="36" height="3.5" rx="1.75" fill="rgba(34,197,94,0.16)" />
      <rect x="68" y="88" width="52" height="3.5" rx="1.75" fill="rgba(34,197,94,0.10)" />

      {/* ECG waveform right */}
      <polyline
        points="152,68 158,68 161,52 166,85 170,60 174,68 180,68"
        stroke="rgba(34,197,94,0.65)"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Check circle */}
      <circle cx="162" cy="106" r="12" fill="rgba(34,197,94,0.12)" stroke="rgba(34,197,94,0.35)" strokeWidth="1.5" />
      <polyline
        points="156,106 160,110 168,99"
        stroke="#22c55e"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
