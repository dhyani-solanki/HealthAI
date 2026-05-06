"use client"

import { useEffect, useState } from "react"
import { getFamilyReports, listMedReports, deleteMedReport, bulkDeleteMedReports, fetchReportPdfBlob, type FamilyMember, type MedReportListItem } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Loader2,
  ArrowLeft,
  FileText,
  Trash2,
  ChevronDown,
  Upload,
  Users,
  User,
  Heart,
  CheckSquare,
  Square,
  X,
  Eye,
  EyeOff,
} from "lucide-react"
import Link from "next/link"

export default function FamilyOthersPage() {
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([])
  const [othersReports, setOthersReports] = useState<MedReportListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [selectedMember, setSelectedMember] = useState<string | null>(null)
  const [selectMode, setSelectMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())
  const [deleting, setDeleting] = useState(false)

  useEffect(() => { loadData() }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [famData, othersData] = await Promise.all([getFamilyReports(), listMedReports("others")])
      setFamilyMembers(famData.family_members)
      setOthersReports(othersData)
    } catch (err) { setError(err instanceof Error ? err.message : "Failed to load") }
    finally { setLoading(false) }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this report?")) return
    try { await deleteMedReport(id); await loadData() } catch {}
  }

  function toggleSelect(id: number) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }

  function getCurrentReports(): MedReportListItem[] {
    if (selectedMember) return familyMembers.find((m) => m.name === selectedMember)?.reports || []
    return othersReports
  }

  function toggleSelectAll() {
    const current = getCurrentReports()
    if (selectedIds.size === current.length) setSelectedIds(new Set())
    else setSelectedIds(new Set(current.map((r) => r.id)))
  }

  async function handleBulkDelete() {
    if (selectedIds.size === 0) return
    if (!confirm(`Delete ${selectedIds.size} selected report(s)?`)) return
    setDeleting(true)
    try {
      await bulkDeleteMedReports(Array.from(selectedIds))
      setSelectedIds(new Set())
      setSelectMode(false)
      await loadData()
    } catch {} finally { setDeleting(false) }
  }

  function exitSelectMode() {
    setSelectMode(false)
    setSelectedIds(new Set())
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const selectedReports = selectedMember ? familyMembers.find((m) => m.name === selectedMember)?.reports || [] : []

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-lg">
                <Users className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Family & Others</h1>
                <p className="text-muted-foreground">Manage health reports for family members</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="gap-1.5 py-1.5">
                <Heart className="h-3.5 w-3.5" />
                {familyMembers.length} Members
              </Badge>
              <Button asChild>
                <Link href="/dashboard/upload-report">
                  <Upload className="h-4 w-4 mr-2" />
                  Add Report
                </Link>
              </Button>
            </div>
          </div>
        </div>

        {error && (
          <Card className="mb-6 border-destructive/30 bg-destructive/5">
            <CardContent className="p-4">
              <p className="text-sm text-destructive">{error}</p>
            </CardContent>
          </Card>
        )}

        {selectedMember ? (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Button variant="ghost" size="sm" onClick={() => { setSelectedMember(null); exitSelectMode() }} className="gap-2 text-muted-foreground">
                  <ArrowLeft className="h-4 w-4" /> Back
                </Button>
                <h2 className="text-xl font-bold flex items-center gap-2 text-foreground">
                  <User className="h-5 w-5 text-primary" />
                  {selectedMember}&apos;s Reports
                </h2>
              </div>
              {selectedReports.length > 0 && (
                <div className="flex items-center gap-2">
                  {selectMode ? (
                    <>
                      <Button variant="ghost" size="sm" onClick={toggleSelectAll} className="text-xs gap-1.5">
                        {selectedIds.size === selectedReports.length ? <CheckSquare className="h-3.5 w-3.5" /> : <Square className="h-3.5 w-3.5" />}
                        {selectedIds.size === selectedReports.length ? "Deselect All" : "Select All"}
                      </Button>
                      <Button variant="destructive" size="sm" disabled={selectedIds.size === 0 || deleting} onClick={handleBulkDelete} className="text-xs gap-1.5">
                        {deleting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Trash2 className="h-3.5 w-3.5" />}
                        Delete ({selectedIds.size})
                      </Button>
                      <Button variant="ghost" size="sm" onClick={exitSelectMode} className="text-xs gap-1.5">
                        <X className="h-3.5 w-3.5" /> Cancel
                      </Button>
                    </>
                  ) : (
                    <Button variant="outline" size="sm" onClick={() => setSelectMode(true)} className="text-xs gap-1.5">
                      <CheckSquare className="h-3.5 w-3.5" /> Select
                    </Button>
                  )}
                </div>
              )}
            </div>
            {selectedReports.length === 0 ? (
              <Card className="border-border/50 shadow-sm">
                <CardContent className="flex flex-col items-center justify-center py-16">
                  <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">No reports found for {selectedMember}.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {selectedReports.map((r) => (
                  <ReportCard
                    key={r.id} report={r}
                    onDelete={() => handleDelete(r.id)}
                    selectMode={selectMode} selected={selectedIds.has(r.id)}
                    onToggleSelect={() => toggleSelect(r.id)}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          <div>
            {familyMembers.length === 0 && othersReports.length === 0 ? (
              <Card className="border-border/50 shadow-sm">
                <CardContent className="flex flex-col items-center justify-center py-16">
                  <Users className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium text-foreground">No family reports yet</p>
                  <p className="mt-1 text-sm text-muted-foreground">Upload a report to get started</p>
                  <Button className="mt-4" asChild>
                    <Link href="/dashboard/upload-report">
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Report
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <>
                {familyMembers.length > 0 && (
                  <div className="mb-8">
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                      <Users className="h-4 w-4 text-primary" />
                      Family Members
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {familyMembers.map((member) => (
                        <Card
                          key={member.name}
                          className="border-border/50 shadow-sm cursor-pointer transition-all hover:shadow-md hover:border-primary/30"
                          onClick={() => setSelectedMember(member.name)}
                        >
                          <CardContent className="p-6 text-center">
                            <Avatar className="mx-auto h-16 w-16 mb-4 border-2 border-primary/20">
                              <AvatarFallback className="bg-primary/10 text-primary text-xl font-bold">
                                {member.name[0]}
                              </AvatarFallback>
                            </Avatar>
                            <p className="text-lg font-bold text-foreground">{member.name}</p>
                            <Badge variant="secondary" className="mt-2">
                              {member.report_count} Report{member.report_count !== 1 ? "s" : ""}
                            </Badge>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {othersReports.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                        <User className="h-4 w-4 text-primary" />
                        Others
                      </h2>
                      <div className="flex items-center gap-2">
                        {selectMode ? (
                          <>
                            <Button variant="ghost" size="sm" onClick={toggleSelectAll} className="text-xs gap-1.5">
                              {selectedIds.size === othersReports.length ? <CheckSquare className="h-3.5 w-3.5" /> : <Square className="h-3.5 w-3.5" />}
                              {selectedIds.size === othersReports.length ? "Deselect All" : "Select All"}
                            </Button>
                            <Button variant="destructive" size="sm" disabled={selectedIds.size === 0 || deleting} onClick={handleBulkDelete} className="text-xs gap-1.5">
                              {deleting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Trash2 className="h-3.5 w-3.5" />}
                              Delete ({selectedIds.size})
                            </Button>
                            <Button variant="ghost" size="sm" onClick={exitSelectMode} className="text-xs gap-1.5">
                              <X className="h-3.5 w-3.5" /> Cancel
                            </Button>
                          </>
                        ) : (
                          <Button variant="outline" size="sm" onClick={() => setSelectMode(true)} className="text-xs gap-1.5">
                            <CheckSquare className="h-3.5 w-3.5" /> Select
                          </Button>
                        )}
                      </div>
                    </div>
                    <div className="space-y-3">
                      {othersReports.map((r) => (
                        <ReportCard
                          key={r.id} report={r}
                          onDelete={() => handleDelete(r.id)}
                          selectMode={selectMode} selected={selectedIds.has(r.id)}
                          onToggleSelect={() => toggleSelect(r.id)}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function ReportCard({ report, onDelete, selectMode, selected, onToggleSelect }: {
  report: MedReportListItem; onDelete: () => void;
  selectMode: boolean; selected: boolean; onToggleSelect: () => void;
}) {
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
    <Card className={`border-border/50 shadow-sm overflow-hidden transition-all hover:shadow-md ${selected ? "ring-2 ring-primary border-primary/50" : ""}`}>
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
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground truncate">{report.file_name}</p>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <Badge className="text-[10px] px-1.5 py-0">{report.report_label || report.report_type}</Badge>
              <span className="text-[10px] text-muted-foreground">{report.upload_date?.slice(0, 10)}</span>
              {report.owner_name && (
                <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-primary/30 text-primary">
                  {report.owner_name}
                </Badge>
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
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
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
