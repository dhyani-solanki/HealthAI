"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Loader2,
  Upload,
  ChevronRight,
  BarChart3,
  FlaskConical,
  ChevronDown,
  ChevronUp,
  BookOpen,
  AlertTriangle,
  Activity,
  Clipboard,
} from "lucide-react"
import Link from "next/link"

interface ReportInfoItem {
  key: string
  label: string
  icon: string
  short_desc: string
  what_it_measures: string
  why_important: string
  normal_ranges: { parameter: string; range: string }[]
  conditions_detected: string[]
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function DataInsightsPage() {
  const router = useRouter()
  const [reportInfo, setReportInfo] = useState<ReportInfoItem[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedKey, setExpandedKey] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const token = typeof window !== "undefined" ? localStorage.getItem("health_token") : null
        const headers: Record<string, string> = { "Content-Type": "application/json" }
        if (token) headers["Authorization"] = `Bearer ${token}`
        const res = await fetch(`${BASE_URL}/data-insights/report-info`, { headers })
        if (res.ok) setReportInfo(await res.json())
      } catch {}
      setLoading(false)
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-lg">
                <BarChart3 className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Report Guide</h1>
                <p className="text-muted-foreground">Health report reference guide & education</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="gap-1.5 py-1.5">
                <BookOpen className="h-3.5 w-3.5" />
                {reportInfo.length} Report Types
              </Badge>
              <Button asChild>
                <Link href="/dashboard/upload-report">
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Report
                </Link>
              </Button>
            </div>
          </div>
        </div>

        {/* Report Reference Grid */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
            <FlaskConical className="h-4 w-4 text-primary" />
            Health Report Reference
          </h2>

          {reportInfo.length === 0 ? (
            <Card className="border-border/50 shadow-sm">
              <CardContent className="flex flex-col items-center justify-center py-16">
                <BarChart3 className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-medium text-foreground">No report info available</p>
                <p className="mt-1 text-sm text-muted-foreground">Make sure the backend is running</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reportInfo.map((info) => (
                <ReportInfoCard
                  key={info.key}
                  info={info}
                  expanded={expandedKey === info.key}
                  onToggle={() => setExpandedKey(expandedKey === info.key ? null : info.key)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Upload CTA */}
        <Card className="border-primary/20 bg-primary/5 shadow-sm">
          <CardContent className="p-0">
            <Link href="/dashboard/upload-report" className="flex items-center gap-5 p-6 transition-all hover:bg-primary/10 rounded-xl">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary shrink-0">
                <Upload className="h-7 w-7 text-primary-foreground" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-foreground">Upload Medical Report</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Upload a PDF report for AI-powered analysis. Choose if it&apos;s for yourself, a family member, or others.
                </p>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function ReportInfoCard({ info, expanded, onToggle }: { info: ReportInfoItem; expanded: boolean; onToggle: () => void }) {
  return (
    <Card
      onClick={onToggle}
      className={`border-border/50 shadow-sm cursor-pointer transition-all hover:shadow-md hover:border-primary/30 ${
        expanded ? "md:col-span-2 lg:col-span-3" : ""
      }`}
    >
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{info.icon}</span>
            <div>
              <h3 className="text-sm font-bold text-foreground">{info.label}</h3>
              <p className="text-xs text-muted-foreground">{info.short_desc}</p>
            </div>
          </div>
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground shrink-0" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0" />
          )}
        </div>

        {expanded && (
          <div className="space-y-5 mt-5 pt-4 border-t border-border/50">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Clipboard className="h-3.5 w-3.5 text-primary" />
                <span className="text-xs font-bold uppercase tracking-wider text-primary">What it measures</span>
              </div>
              <p className="text-sm leading-relaxed text-muted-foreground">{info.what_it_measures}</p>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-3.5 w-3.5 text-warning" />
                <span className="text-xs font-bold uppercase tracking-wider text-warning">Why it&apos;s important</span>
              </div>
              <p className="text-sm leading-relaxed text-muted-foreground">{info.why_important}</p>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-3">
                <Activity className="h-3.5 w-3.5 text-primary" />
                <span className="text-xs font-bold uppercase tracking-wider text-primary">Normal Ranges</span>
              </div>
              <div className="overflow-x-auto rounded-xl border border-border/50">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-primary text-primary-foreground">
                      <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wider">Parameter</th>
                      <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wider">Range</th>
                    </tr>
                  </thead>
                  <tbody>
                    {info.normal_ranges.map((nr, i) => (
                      <tr key={i} className="border-b border-border/30 last:border-0 hover:bg-secondary/30">
                        <td className="px-4 py-2 font-medium text-foreground">{nr.parameter}</td>
                        <td className="px-4 py-2 font-bold text-primary">{nr.range}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-3">
                <FlaskConical className="h-3.5 w-3.5 text-primary" />
                <span className="text-xs font-bold uppercase tracking-wider text-primary">Conditions Detected</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {info.conditions_detected.map((c) => (
                  <Badge key={c} variant="secondary" className="text-xs">
                    {c}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
