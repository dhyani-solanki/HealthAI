"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { getMedReport, deleteMedReport, fetchReportPdfBlob, type MedReportListItem } from "@/lib/api"
import { ReportDetailView } from "@/components/report-visuals"
import { Button } from "@/components/ui/button"
import { Loader2, Trash2, Upload, Eye, EyeOff } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

export default function ReportDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = Number(params.id)

  const [report, setReport] = useState<MedReportListItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showPdf, setShowPdf] = useState(false)
  const [pdfBlobUrl, setPdfBlobUrl] = useState<string | null>(null)
  const [loadingPdf, setLoadingPdf] = useState(false)

  useEffect(() => {
    if (!id || isNaN(id)) { setError("Invalid report ID"); setLoading(false); return }
    getMedReport(id)
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load report"))
      .finally(() => setLoading(false))
  }, [id])

  async function handleTogglePdf() {
    if (showPdf) { setShowPdf(false); return }
    if (pdfBlobUrl) { setShowPdf(true); return }
    setLoadingPdf(true)
    try {
      const url = await fetchReportPdfBlob(id)
      setPdfBlobUrl(url)
      setShowPdf(true)
    } catch { setError("Failed to load PDF") }
    finally { setLoadingPdf(false) }
  }

  async function handleDelete() {
    if (!confirm("Delete this report permanently?")) return
    try {
      await deleteMedReport(id)
      router.back()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed")
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-background">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center py-20">
            <p className="text-destructive font-medium mb-4">{error || "Report not found"}</p>
            <Button variant="outline" onClick={() => router.back()}>Go Back</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Report Analysis</h1>
          <div className="flex items-center gap-2">
            <Button variant="destructive" size="sm" onClick={handleDelete} className="gap-1.5">
              <Trash2 className="h-3.5 w-3.5" /> Delete
            </Button>
            <Button size="sm" asChild>
              <Link href="/dashboard/upload-report">
                <Upload className="h-3.5 w-3.5 mr-1.5" /> New Report
              </Link>
            </Button>
          </div>
        </div>

        {/* PDF Show/Hide */}
        <Card className="border-border/50 shadow-sm mb-6">
          <CardContent className="p-4">
            <Button
              variant="outline"
              onClick={handleTogglePdf}
              disabled={loadingPdf}
              className="w-full gap-2"
            >
              {loadingPdf ? (
                <><Loader2 className="h-4 w-4 animate-spin" /> Loading PDF...</>
              ) : showPdf ? (
                <><EyeOff className="h-4 w-4" /> Hide Original Report</>
              ) : (
                <><Eye className="h-4 w-4" /> View Original Report</>
              )}
            </Button>
            {showPdf && pdfBlobUrl && (
              <div className="mt-4 rounded-xl border border-border/50 overflow-hidden">
                <iframe
                  src={pdfBlobUrl}
                  className="w-full h-[600px]"
                  title="Report PDF Preview"
                />
              </div>
            )}
          </CardContent>
        </Card>

        <ReportDetailView
          report={{
            report_type: report.report_type,
            report_label: report.report_label,
            confidence: report.confidence,
            parameters: report.parameters || [],
            summary: report.summary,
            owner_type: report.owner_type,
            owner_name: report.owner_name,
            file_name: report.file_name,
            upload_date: report.upload_date,
          }}
          onBack={() => router.back()}
        />
      </div>
    </div>
  )
}
