"use client"

import { useEffect, useState } from "react"
import { listMedReports, deleteMedReport, bulkDeleteMedReports, fetchReportPdfBlob, type MedReportListItem } from "@/lib/api"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Trash2, Loader2, FileText, ChevronRight, Search, Bot, Upload,
  Activity, CheckSquare, Square, X, Eye, EyeOff,
} from "lucide-react"
import Link from "next/link"

export default function HealthRecordsPage() {
  const [medReports, setMedReports] = useState<MedReportListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const [selectMode, setSelectMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())
  const [deleting, setDeleting] = useState(false)

  useEffect(() => { loadData() }, [])

  async function loadData() {
    setLoading(true)
    try {
      const reports = await listMedReports("myself")
      setMedReports(reports)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load")
    } finally { setLoading(false) }
  }

  async function handleDeleteReport(id: number) {
    if (!confirm("Delete this report?")) return
    try { await deleteMedReport(id); setMedReports((prev) => prev.filter((r) => r.id !== id)) } catch {}
  }

  function toggleSelect(id: number) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }

  function toggleSelectAll() {
    if (selectedIds.size === filteredReports.length) setSelectedIds(new Set())
    else setSelectedIds(new Set(filteredReports.map((r) => r.id)))
  }

  async function handleBulkDelete() {
    if (selectedIds.size === 0) return
    if (!confirm(`Delete ${selectedIds.size} selected report(s)?`)) return
    setDeleting(true)
    try {
      await bulkDeleteMedReports(Array.from(selectedIds))
      setMedReports((prev) => prev.filter((r) => !selectedIds.has(r.id)))
      setSelectedIds(new Set()); setSelectMode(false)
    } catch {} finally { setDeleting(false) }
  }

  function exitSelectMode() { setSelectMode(false); setSelectedIds(new Set()) }

  const filteredReports = medReports.filter((r) =>
    r.file_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.report_label?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.report_type?.toLowerCase().includes(searchQuery.toLowerCase())
  )

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
                <Bot className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Health Records</h1>
                <p className="text-muted-foreground">Your AI-analyzed medical reports</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="gap-1.5 py-1.5">
                <Activity className="h-3.5 w-3.5" />
                {medReports.length} Reports
              </Badge>
              <Button asChild>
                <Link href="/dashboard/upload-report">
                  <Upload className="h-4 w-4 mr-2" /> Upload Report
                </Link>
              </Button>
            </div>
          </div>
        </div>

        {/* Search + Select Controls */}
        <div className="mb-6 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
          <div className="relative max-w-md flex-1">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Search reports..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10 h-11 bg-secondary/30 border-border/50" />
          </div>
          <div className="flex items-center gap-2">
            {selectMode ? (
              <>
                <Button variant="ghost" size="sm" onClick={toggleSelectAll} className="text-xs gap-1.5">
                  {selectedIds.size === filteredReports.length ? <CheckSquare className="h-3.5 w-3.5" /> : <Square className="h-3.5 w-3.5" />}
                  {selectedIds.size === filteredReports.length ? "Deselect All" : "Select All"}
                </Button>
                <Button variant="destructive" size="sm" disabled={selectedIds.size === 0 || deleting} onClick={handleBulkDelete} className="text-xs gap-1.5">
                  {deleting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Trash2 className="h-3.5 w-3.5" />}
                  Delete ({selectedIds.size})
                </Button>
                <Button variant="ghost" size="sm" onClick={exitSelectMode} className="text-xs gap-1.5"><X className="h-3.5 w-3.5" /> Cancel</Button>
              </>
            ) : (
              filteredReports.length > 0 && (
                <Button variant="outline" size="sm" onClick={() => setSelectMode(true)} className="text-xs gap-1.5">
                  <CheckSquare className="h-3.5 w-3.5" /> Select
                </Button>
              )
            )}
          </div>
        </div>

        {error && (
          <Card className="mb-6 border-destructive/30 bg-destructive/5">
            <CardContent className="p-4"><p className="text-sm text-destructive">{error}</p></CardContent>
          </Card>
        )}

        {/* Reports List */}
        {filteredReports.length === 0 ? (
          <Card className="border-border/50 shadow-sm">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <Bot className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium text-foreground">No AI-analyzed reports yet</p>
              <p className="mt-1 text-sm text-muted-foreground">Upload a medical report PDF to get started</p>
              <Button className="mt-4" asChild>
                <Link href="/dashboard/upload-report"><Upload className="h-4 w-4 mr-2" /> Upload Report</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {filteredReports.map((r) => (
              <MedReportCard
                key={r.id}
                report={r}
                onDelete={() => handleDeleteReport(r.id)}
                selectMode={selectMode}
                selected={selectedIds.has(r.id)}
                onToggleSelect={() => toggleSelect(r.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function MedReportCard({ report, onDelete, selectMode, selected, onToggleSelect }: {
  report: MedReportListItem; onDelete: () => void;
  selectMode: boolean; selected: boolean; onToggleSelect: () => void;
}) {
  const paramCount = report.parameters?.length || 0
  const abnormalCount = report.parameters?.filter(p => p.status === "high" || p.status === "low").length || 0
  const [showPdf, setShowPdf] = useState(false)
  const [pdfBlobUrl, setPdfBlobUrl] = useState<string | null>(null)
  const [loadingPdf, setLoadingPdf] = useState(false)

  async function handleTogglePdf(e: React.MouseEvent) {
    e.stopPropagation()
    if (showPdf) { setShowPdf(false); return }
    if (pdfBlobUrl) { setShowPdf(true); return }
    setLoadingPdf(true)
    try {
      const url = await fetchReportPdfBlob(report.id)
      setPdfBlobUrl(url)
      setShowPdf(true)
    } catch {}
    finally { setLoadingPdf(false) }
  }

  return (
    <Card className={`border-border/50 shadow-sm overflow-hidden transition-all duration-150 hover:shadow-md ${selected ? "ring-2 ring-primary border-primary/50" : ""}`}>
      <div className="p-4 flex items-center justify-between">
        <Link
          href={selectMode ? "#" : `/dashboard/report/${report.id}`}
          className="flex items-center gap-3 min-w-0 flex-1 cursor-pointer"
          onClick={selectMode ? (e) => { e.preventDefault(); onToggleSelect() } : undefined}
        >
          {selectMode && (
            <span className="shrink-0">
              {selected ? <CheckSquare className="h-5 w-5 text-primary" /> : <Square className="h-5 w-5 text-muted-foreground" />}
            </span>
          )}
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 shrink-0">
            <FileText className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold text-foreground truncate">{report.file_name}</p>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <Badge className="text-[10px] px-1.5 py-0">{report.report_label || report.report_type}</Badge>
              {report.upload_date && (
                <span className="text-[10px] text-muted-foreground">
                  {new Date(report.upload_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
                </span>
              )}
              {report.confidence && (
                <Badge variant="outline" className={`text-[10px] px-1.5 py-0 ${
                  report.confidence === "high" ? "border-success/30 bg-success/5 text-success"
                    : report.confidence === "medium" ? "border-warning/30 bg-warning/5 text-warning"
                    : "border-destructive/30 bg-destructive/5 text-destructive"
                }`}>{report.confidence}</Badge>
              )}
              {paramCount > 0 && (
                <span className="text-[10px] text-muted-foreground">{paramCount} params{abnormalCount > 0 && <span className="text-red-500 font-semibold"> · {abnormalCount} abnormal</span>}</span>
              )}
            </div>
          </div>
        </Link>
        <div className="flex items-center gap-1.5 shrink-0">
          {!selectMode && (
            <Button variant="ghost" size="icon" onClick={handleTogglePdf} disabled={loadingPdf} className="h-7 w-7 text-muted-foreground hover:text-primary hover:bg-primary/10" title={showPdf ? "Hide PDF" : "View PDF"}>
              {loadingPdf ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : showPdf ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
            </Button>
          )}
          {!selectMode && (
            <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); onDelete() }} className="h-7 w-7 text-destructive hover:bg-destructive/10">
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          )}
          {!selectMode && (
            <Link href={`/dashboard/report/${report.id}`} className="p-1">
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </Link>
          )}
        </div>
      </div>
      {showPdf && pdfBlobUrl && (
        <div className="px-4 pb-4">
          <div className="rounded-xl border border-border/50 overflow-hidden">
            <iframe src={pdfBlobUrl} className="w-full h-[500px]" title="Report PDF" />
          </div>
        </div>
      )}
    </Card>
  )
}
