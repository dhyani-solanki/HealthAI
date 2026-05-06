"use client"

import { useState, useRef, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  FileText,
  CheckCircle2,
  Sparkles,
  X,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowLeft,
  AlertTriangle,
  Info,
} from "lucide-react"
import type { MedReportParam } from "@/lib/api"

/* ─── Animated Radial Gauge ─── */
export function RadialGauge({ value, nmin, nmax, unit, isHigh }: {
  value: number; nmin: number; nmax: number; unit: string; isHigh: boolean
}) {
  const [animPct, setAnimPct] = useState(0)
  const hasRange = nmin > 0 || nmax > 0
  const span = hasRange ? (nmax - nmin || 1) : (value * 0.5 || 1)
  const scaleMax = Math.max(hasRange ? nmax + span * 0.6 : value * 1.5, value * 1.3)
  const pct = Math.min(Math.max((value / scaleMax) * 100, 5), 95)
  const normalStartPct = hasRange ? (nmin / scaleMax) * 100 : 0
  const normalEndPct = hasRange ? Math.min((nmax / scaleMax) * 100, 100) : 0

  useEffect(() => {
    const timer = setTimeout(() => setAnimPct(pct), 100)
    return () => clearTimeout(timer)
  }, [pct])

  const radius = 52
  const stroke = 10
  const circumference = 2 * Math.PI * radius
  const arcLen = circumference * 0.75
  const offset = arcLen - (arcLen * animPct) / 100
  const normalStart = arcLen * (normalStartPct / 100)
  const normalLen = arcLen * ((normalEndPct - normalStartPct) / 100)
  const color = isHigh ? "#ef4444" : "#f59e0b"
  const normalColor = "#3b82f6"

  return (
    <div className="relative w-[140px] h-[140px] mx-auto">
      <svg viewBox="0 0 128 128" className="w-full h-full -rotate-[135deg]">
        <circle cx="64" cy="64" r={radius} fill="none" stroke="currentColor" strokeWidth={stroke}
          className="text-gray-100 dark:text-gray-800" strokeDasharray={`${arcLen} ${circumference}`} strokeLinecap="round" />
        {hasRange && (
          <circle cx="64" cy="64" r={radius} fill="none" stroke={normalColor} strokeWidth={stroke} opacity={0.2}
            strokeDasharray={`${normalLen} ${circumference - normalLen}`} strokeDashoffset={-normalStart} strokeLinecap="round" />
        )}
        <circle cx="64" cy="64" r={radius} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={`${arcLen} ${circumference}`} strokeDashoffset={offset}
          strokeLinecap="round" className="transition-all duration-1000 ease-out" style={{ filter: `drop-shadow(0 0 6px ${color}40)` }} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold" style={{ color }}>{value}</span>
        <span className="text-[10px] text-muted-foreground font-medium">{unit}</span>
      </div>
    </div>
  )
}

/* ─── Linear Gauge Bar ─── */
export function GaugeBar({ value, nmin, nmax, isHigh }: {
  value: number; nmin: number; nmax: number; isHigh: boolean
}) {
  const [animated, setAnimated] = useState(false)
  const hasRange = nmin > 0 || nmax > 0
  const span = hasRange ? (nmax - nmin || value * 0.5 || 1) : (value * 0.5 || 1)
  const scaleMax = Math.max(hasRange ? nmax + span * 0.5 : value * 1.5, value * 1.3)
  const range = scaleMax || 1

  const valPct = Math.min(Math.max((value / range) * 100, 2), 97)
  const nminPct = hasRange ? Math.max((nmin / range) * 100, 0) : 0
  const nmaxPct = hasRange ? Math.min((nmax / range) * 100, 100) : 0

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 50)
    return () => clearTimeout(t)
  }, [])

  return (
    <div className="my-3">
      <div className="relative h-7 mb-0.5">
        <div className="absolute -translate-x-1/2 z-10 transition-all duration-700 ease-out"
          style={{ left: animated ? `${valPct}%` : "0%" }}>
          <div className="bg-gray-800 dark:bg-gray-200 dark:text-gray-900 text-white text-[11px] font-bold px-2.5 py-1 rounded-lg shadow-lg whitespace-nowrap">
            {value}
          </div>
          <div className="w-0 h-0 mx-auto border-l-[5px] border-r-[5px] border-t-[5px] border-l-transparent border-r-transparent border-t-gray-800 dark:border-t-gray-200" />
        </div>
      </div>
      <div className="relative h-3 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden">
        {/* low zone */}
        <div className="absolute top-0 left-0 h-full rounded-l-full bg-gradient-to-r from-amber-200 to-amber-300 dark:from-amber-800 dark:to-amber-700 transition-all duration-700 ease-out"
          style={{ width: animated ? `${nminPct}%` : "0%" }} />
        {/* normal zone */}
        {hasRange && (
          <div className="absolute top-0 h-full bg-gradient-to-r from-emerald-300 via-emerald-400 to-emerald-300 dark:from-emerald-700 dark:to-emerald-600 transition-all duration-700 ease-out"
            style={{ left: `${nminPct}%`, width: animated ? `${nmaxPct - nminPct}%` : "0%" }} />
        )}
        {/* high zone */}
        {hasRange && (
          <div className="absolute top-0 h-full rounded-r-full bg-gradient-to-r from-red-300 to-red-400 dark:from-red-800 dark:to-red-700 transition-all duration-700 ease-out"
            style={{ left: `${nmaxPct}%`, width: animated ? `${100 - nmaxPct}%` : "0%" }} />
        )}
        {/* indicator dot */}
        <div className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-[18px] w-[18px] rounded-full border-[3px] border-white dark:border-gray-900 shadow-lg z-20 transition-all duration-700 ease-out ${
          isHigh ? "bg-red-500" : "bg-amber-500"
        }`} style={{ left: animated ? `${valPct}%` : "0%" }} />
      </div>
      <div className="flex justify-between mt-1.5">
        <span className="text-[10px] text-muted-foreground">0</span>
        {hasRange && <span className="text-[10px] text-emerald-500 font-medium">Normal: {nmin}–{nmax}</span>}
        <span className="text-[10px] text-muted-foreground">{Math.round(scaleMax)}</span>
      </div>
    </div>
  )
}

/* ─── Parse summary into numbered sections ─── */
export function parseSummarySections(text: string): { title: string; items: string[] }[] {
  const sections: { title: string; items: string[] }[] = []
  let current: { title: string; items: string[] } | null = null

  for (const line of text.split("\n")) {
    const trimmed = line.trim().replace(/\*\*/g, "")
    if (!trimmed) continue

    const headerMatch = trimmed.match(/^(?:#{1,3}\s*)?(\d+\.\s*.+)$/) || trimmed.match(/^(?:#{1,3}\s*)(.+)$/)
    if (headerMatch && !trimmed.startsWith("-") && !trimmed.startsWith("~") && trimmed.length < 100 && /\d+\.\s/.test(trimmed)) {
      if (current) sections.push(current)
      current = { title: headerMatch[1].replace(/^#+\s*/, ""), items: [] }
    } else if (current) {
      const item = trimmed.replace(/^[-~•*]\s*/, "").trim()
      if (item) current.items.push(item)
    } else {
      if (!sections.length && !current) {
        current = { title: "Overview", items: [] }
      }
      if (current) {
        const item = trimmed.replace(/^[-~•*]\s*/, "").trim()
        if (item) current.items.push(item)
      }
    }
  }
  if (current) sections.push(current)
  return sections
}

/* ─── Parse normal range from params ─── */
export function parseRange(p: MedReportParam): { nmin: number; nmax: number } {
  let nmin = p.normal_min ?? 0
  let nmax = p.normal_max ?? 0
  if ((!nmin && !nmax) && p.normal_range) {
    const parts = p.normal_range.split(/\s*[-–]\s*/).map(Number)
    if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
      nmin = parts[0]; nmax = parts[1]
    }
  }
  return { nmin, nmax }
}

/* ─── Full Report Detail View ─── */
export function ReportDetailView({ report, onBack, showVisuals = true }: {
  report: {
    report_type: string
    report_label: string
    confidence: string
    classification_reasoning?: string
    parameters: MedReportParam[]
    summary: string
    owner_type?: string
    owner_name?: string | null
    file_name?: string
    upload_date?: string
  }
  onBack?: () => void
  showVisuals?: boolean
}) {
  const params = report.parameters || []
  const totalCount = params.length
  const normalCount = params.filter(p => p.status === "normal").length
  const abnormalCount = params.filter(p => p.status === "high" || p.status === "low").length
  const borderlineCount = params.filter(p => p.status === "borderline").length
  const highCount = params.filter(p => p.status === "high").length
  const lowCount = params.filter(p => p.status === "low").length
  const abnormalParams = params.filter(p => p.status === "high" || p.status === "low")
  const summarySections = report.summary ? parseSummarySections(report.summary) : []
  const confidenceNum = report.confidence === "high" ? 96 : report.confidence === "medium" ? 75 : 45

  return (
    <div className="space-y-8">
      {/* Back button */}
      {onBack && (
        <Button variant="ghost" size="sm" onClick={onBack} className="gap-2 text-muted-foreground -ml-2">
          <ArrowLeft className="h-4 w-4" /> Back
        </Button>
      )}

      {/* File info */}
      {report.file_name && (
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <FileText className="h-4 w-4" />
          <span className="font-medium">{report.file_name}</span>
          {report.upload_date && (
            <span>· {new Date(report.upload_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })} at {new Date(report.upload_date).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}</span>
          )}
          {report.owner_name && <Badge variant="outline" className="text-[10px] ml-2">{report.owner_name}</Badge>}
        </div>
      )}

      {/* ── Detected Report Type Card ── */}
      <div className="flex items-center gap-4 rounded-2xl border border-border/50 bg-card p-5 shadow-sm">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-900/30">
          <FileText className="h-6 w-6 text-blue-500" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Detected Report Type</p>
          <p className="text-lg font-bold text-blue-600 dark:text-blue-400 truncate">{report.report_label || report.report_type || "Medical Report"}</p>
          {report.classification_reasoning && (
            <p className="text-xs text-muted-foreground mt-0.5">{report.classification_reasoning}</p>
          )}
        </div>
        <div className="text-right shrink-0">
          <p className="text-2xl font-bold text-emerald-500">{confidenceNum}%</p>
          <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Confidence</p>
        </div>
      </div>

      {/* ── Clinical Parameters Extraction ── */}
      {totalCount > 0 && (
        <div>
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/40">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            </div>
            <h3 className="text-base font-bold text-foreground">Clinical Parameters Extraction</h3>
            <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 border-0 text-[10px] font-bold uppercase">Completed</Badge>
          </div>

          {/* Stats row */}
          <div className="flex gap-3 mb-6">
            {[
              { label: "Total", value: totalCount, color: "text-gray-700 dark:text-gray-300", bg: "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700" },
              { label: "Normal", value: normalCount, color: "text-emerald-600", bg: "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800" },
              { label: "Abnormal", value: abnormalCount, color: "text-red-600 dark:text-red-400", bg: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800" },
              { label: "Borderline", value: borderlineCount, color: "text-amber-600 dark:text-amber-400", bg: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800" },
            ].map((s) => (
              <div key={s.label} className={`flex-1 rounded-xl border p-3 text-center ${s.bg}`}>
                <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
                <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">{s.label}</p>
              </div>
            ))}
          </div>

          {/* Parameter Table */}
          <div className="overflow-x-auto rounded-2xl border border-border/50 bg-card shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/50">
                  <th className="px-5 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Parameter</th>
                  <th className="px-5 py-3 text-center text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Your Value</th>
                  <th className="px-5 py-3 text-center text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Normal Range</th>
                  <th className="px-5 py-3 text-center text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Unit</th>
                  <th className="px-5 py-3 text-right text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Status</th>
                </tr>
              </thead>
              <tbody>
                {params.map((p, i) => (
                  <tr key={i} className="border-b border-border/30 last:border-0 hover:bg-secondary/20 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-900/20">
                          <Activity className="h-4 w-4 text-blue-400" />
                        </div>
                        <div>
                          <p className="font-semibold text-foreground">{p.name}</p>
                          {p.source && <p className="text-[10px] text-muted-foreground">Source: {p.source}</p>}
                        </div>
                      </div>
                    </td>
                    <td className={`px-5 py-3.5 text-center text-base font-bold ${
                      p.status === "high" ? "text-red-500" : p.status === "low" ? "text-amber-500" : "text-blue-500"
                    }`}>{p.value}</td>
                    <td className="px-5 py-3.5 text-center text-sm text-muted-foreground">{p.normal_range || "—"}</td>
                    <td className="px-5 py-3.5 text-center text-sm text-muted-foreground">{p.unit}</td>
                    <td className="px-5 py-3.5 text-right">
                      {p.status === "high" ? (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-red-500"><TrendingUp className="h-3 w-3" /> HIGH</span>
                      ) : p.status === "low" ? (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-500"><TrendingDown className="h-3 w-3" /> LOW</span>
                      ) : p.status === "borderline" ? (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-500">BORDERLINE</span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-500"><CheckCircle2 className="h-3 w-3" /> NORMAL</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── AI Summary ── */}
      {summarySections.length > 0 && (
        <div>
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/40">
              <CheckCircle2 className="h-4 w-4 text-blue-500" />
            </div>
            <h3 className="text-base font-bold text-foreground">Report Summary</h3>
            <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 border-0 text-[10px] font-bold uppercase">Generated</Badge>
          </div>
          <div className="space-y-4">
            {summarySections.map((section, i) => (
              <div key={i} className="rounded-2xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/30 p-5">
                <h4 className="font-bold text-sm text-foreground mb-3">{section.title}</h4>
                <div className="space-y-2">
                  {section.items.map((item, j) => (
                    <p key={j} className="text-sm text-muted-foreground leading-relaxed pl-4 relative before:content-['~'] before:absolute before:left-0 before:text-blue-400 before:font-medium">
                      {item}
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Abnormal Parameters Visualization ── */}
      {showVisuals && abnormalParams.length > 0 && (
        <AbnormalVisualization
          params={abnormalParams}
          highCount={highCount}
          lowCount={lowCount}
        />
      )}
    </div>
  )
}

/* ─── Abnormal Visualization Section (Advanced Interactive) ─── */
function AbnormalVisualization({ params, highCount, lowCount }: {
  params: MedReportParam[]; highCount: number; lowCount: number
}) {
  const [showCharts, setShowCharts] = useState(true)
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null)

  return (
    <div>
      <div className="flex items-center gap-3 mb-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/40">
          <AlertTriangle className="h-4 w-4 text-orange-500" />
        </div>
        <h3 className="text-base font-bold text-foreground">Abnormal Parameters</h3>
        <Badge className="bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 border-0 text-[10px] font-bold uppercase">{params.length} flagged</Badge>
      </div>

      {/* Summary pills */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex gap-3">
          {highCount > 0 && (
            <div className="flex items-center gap-2 rounded-2xl border border-red-200 dark:border-red-800 bg-gradient-to-r from-red-50 to-red-50/50 dark:from-red-900/20 dark:to-red-900/10 px-4 py-2.5 shadow-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/10"><TrendingUp className="h-4 w-4 text-red-500" /></div>
              <div>
                <span className="text-xl font-bold text-red-500">{highCount}</span>
                <p className="text-[10px] text-muted-foreground -mt-0.5">Above normal</p>
              </div>
            </div>
          )}
          {lowCount > 0 && (
            <div className="flex items-center gap-2 rounded-2xl border border-amber-200 dark:border-amber-800 bg-gradient-to-r from-amber-50 to-amber-50/50 dark:from-amber-900/20 dark:to-amber-900/10 px-4 py-2.5 shadow-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10"><TrendingDown className="h-4 w-4 text-amber-500" /></div>
              <div>
                <span className="text-xl font-bold text-amber-500">{lowCount}</span>
                <p className="text-[10px] text-muted-foreground -mt-0.5">Below normal</p>
              </div>
            </div>
          )}
        </div>
        <Button variant="outline" size="sm" className="gap-2 text-xs rounded-xl" onClick={() => setShowCharts(!showCharts)}>
          {showCharts ? <><X className="h-3 w-3" /> Hide</> : <><BarChart3 className="h-3 w-3" /> Show</>}
        </Button>
      </div>

      {showCharts && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {params.map((p, i) => {
            const { nmin, nmax } = parseRange(p)
            const val = typeof p.value === "number" ? p.value : parseFloat(String(p.value))
            const hasRange = nmin > 0 || nmax > 0
            const isHigh = p.status === "high"
            const deviation = hasRange
              ? isHigh
                ? ((val - nmax) / nmax * 100).toFixed(1)
                : ((nmin - val) / nmin * 100).toFixed(1)
              : "0"
            const expanded = expandedIdx === i

            return (
              <div key={i}
                onClick={() => setExpandedIdx(expanded ? null : i)}
                className={`rounded-2xl border bg-card shadow-sm cursor-pointer transition-all duration-300 ease-out hover:shadow-md ${
                  isHigh ? "border-red-200/60 dark:border-red-900/40 hover:border-red-300 dark:hover:border-red-800" : "border-amber-200/60 dark:border-amber-900/40 hover:border-amber-300 dark:hover:border-amber-800"
                } ${expanded ? "ring-2 ring-primary/20 scale-[1.01]" : ""}`}
              >
                {/* Header */}
                <div className="p-5 pb-0">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2.5">
                      <div className={`h-3 w-3 rounded-full animate-pulse ${isHigh ? "bg-red-500" : "bg-amber-500"}`} />
                      <span className="font-bold text-sm text-foreground">{p.name}</span>
                    </div>
                    <Badge variant="outline" className={`text-[10px] font-bold border px-2.5 py-0.5 ${
                      isHigh ? "bg-red-50 text-red-600 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800"
                        : "bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800"
                    }`}>{isHigh ? "HIGH" : "LOW"}</Badge>
                  </div>
                </div>

                {/* Radial gauge + value */}
                <div className="px-5">
                  <div className="flex items-center gap-4">
                    <RadialGauge value={val} nmin={nmin} nmax={nmax} unit={p.unit} isHigh={isHigh} />
                    <div className="flex-1 space-y-2">
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Your Value</p>
                        <p className={`text-2xl font-bold ${isHigh ? "text-red-500" : "text-amber-500"}`}>{val} <span className="text-sm font-medium text-muted-foreground">{p.unit}</span></p>
                      </div>
                      {hasRange && (
                        <div>
                          <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Normal Range</p>
                          <p className="text-sm font-bold text-emerald-500">{nmin} – {nmax} {p.unit}</p>
                        </div>
                      )}
                      <div className={`inline-flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-lg ${
                        isHigh ? "bg-red-50 text-red-500 dark:bg-red-900/20" : "bg-amber-50 text-amber-500 dark:bg-amber-900/20"
                      }`}>
                        {isHigh ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                        {deviation}% {isHigh ? "above" : "below"}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Linear gauge */}
                <div className="px-5">
                  <GaugeBar value={val} nmin={nmin} nmax={nmax} isHigh={isHigh} />
                </div>

                {/* Expandable details */}
                <div className={`overflow-hidden transition-all duration-300 ease-out ${expanded ? "max-h-60 opacity-100" : "max-h-0 opacity-0"}`}>
                  <div className="px-5 pb-5 pt-2 space-y-2.5">
                    {p.source && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Info className="h-3 w-3" /> Reference: {p.source}
                      </div>
                    )}
                    {p.insight && (
                      <div className="rounded-xl bg-blue-50/70 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/30 p-3">
                        <p className="text-xs text-muted-foreground leading-relaxed">
                          <Sparkles className="h-3 w-3 inline mr-1.5 text-blue-400" />
                          {p.insight}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Click hint */}
                <div className="px-5 pb-3">
                  <p className="text-[9px] text-center text-muted-foreground/50">{expanded ? "Click to collapse" : "Click for details"}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
