"use client"

import { useState, useRef } from "react"
import {
  classifyMedReport, extractMedReportParams, generateMedReportSummary,
  saveMedReport, fetchPdfByPathBlob, fetchReportPdfBlob,
  type ClassifyResult, type MedReportParam,
} from "@/lib/api"
import { GaugeBar, RadialGauge, parseSummarySections, parseRange } from "@/components/report-visuals"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Upload, FileText, User, Users, UserPlus, Loader2, CheckCircle2,
  AlertCircle, ArrowRight, Sparkles, X, Save, Clock, Activity,
  TrendingUp, TrendingDown, BarChart3, Eye, EyeOff,
} from "lucide-react"
import Link from "next/link"

const FAMILY_RELATIONS = ["Grandfather", "Grandmother", "Father", "Mother", "Brother", "Sister", "Spouse", "Son", "Daughter"]

export default function UploadReportPage() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState("")

  // Owner selection
  const [ownerType, setOwnerType] = useState<"myself" | "family" | "others">("myself")
  const [ownerName, setOwnerName] = useState("")
  const [customName, setCustomName] = useState("")
  const [ownerDone, setOwnerDone] = useState(false)

  // File upload
  const [file, setFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)

  // Classify
  const [classifying, setClassifying] = useState(false)
  const [classifyData, setClassifyData] = useState<ClassifyResult | null>(null)

  // Extract params
  const [extracting, setExtracting] = useState(false)
  const [params, setParams] = useState<MedReportParam[] | null>(null)

  // Summary
  const [summarizing, setSummarizing] = useState(false)
  const [summary, setSummary] = useState<string | null>(null)

  // Visuals
  const [showVisuals, setShowVisuals] = useState(false)

  // Save
  const [saving, setSaving] = useState(false)
  const [savedAt, setSavedAt] = useState("")
  const [savedReportId, setSavedReportId] = useState<number | null>(null)

  // PDF preview
  const [showPdf, setShowPdf] = useState(false)
  const [pdfBlobUrl, setPdfBlobUrl] = useState<string | null>(null)
  const [loadingPdf, setLoadingPdf] = useState(false)

  function handleDrop(e: React.DragEvent) {
    e.preventDefault(); setDragActive(false)
    const f = e.dataTransfer.files[0]
    if (f && f.name.toLowerCase().endsWith(".pdf")) { setFile(f); setError("") }
    else setError("Only PDF files are accepted.")
  }

  async function handleUploadAndClassify() {
    if (!file) return
    setClassifying(true); setError("")
    try {
      const data = await classifyMedReport(file)
      setClassifyData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Classification failed")
    } finally { setClassifying(false) }
  }

  async function handleExtractParams() {
    if (!classifyData) return
    setExtracting(true); setError("")
    try {
      const res = await extractMedReportParams(classifyData.raw_text, classifyData.report_type)
      setParams(res.parameters)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parameter extraction failed")
    } finally { setExtracting(false) }
  }

  async function handleGenerateSummary() {
    if (!classifyData || !params) return
    setSummarizing(true); setError("")
    try {
      const res = await generateMedReportSummary(classifyData.report_type, params)
      setSummary(res.summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Summary generation failed")
    } finally { setSummarizing(false) }
  }

  async function handleSave() {
    if (!classifyData) return
    setSaving(true); setError("")
    try {
      const res = await saveMedReport({
        file_name: classifyData.file_name,
        file_path: classifyData.file_path,
        report_type: classifyData.report_type,
        report_label: classifyData.report_label,
        confidence: classifyData.confidence,
        parameters: params || [],
        summary: summary || "",
        owner_type: ownerType,
        owner_name: ownerType === "family" ? ownerName : ownerType === "others" ? customName : null,
      })
      setSavedAt(res.saved_at)
      setSavedReportId(res.report_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed")
    } finally { setSaving(false) }
  }

  async function handleTogglePdf() {
    if (showPdf) {
      setShowPdf(false)
      return
    }
    if (pdfBlobUrl) {
      setShowPdf(true)
      return
    }
    setLoadingPdf(true)
    try {
      let url: string
      if (savedReportId) {
        url = await fetchReportPdfBlob(savedReportId)
      } else if (classifyData?.file_path) {
        url = await fetchPdfByPathBlob(classifyData.file_path)
      } else return
      setPdfBlobUrl(url)
      setShowPdf(true)
    } catch { setError("Failed to load PDF preview") }
    finally { setLoadingPdf(false) }
  }

  function handleReset() {
    if (pdfBlobUrl) URL.revokeObjectURL(pdfBlobUrl)
    setFile(null); setError(""); setOwnerDone(false)
    setOwnerType("myself"); setOwnerName(""); setCustomName("")
    setClassifying(false); setClassifyData(null)
    setExtracting(false); setParams(null)
    setSummarizing(false); setSummary(null)
    setShowVisuals(false); setSaving(false); setSavedAt(""); setSavedReportId(null)
    setShowPdf(false); setPdfBlobUrl(null); setLoadingPdf(false)
  }

  const confidenceNum = classifyData ? (classifyData.confidence === "high" ? 96 : classifyData.confidence === "medium" ? 75 : 45) : 0
  const abnormalParams = (params || []).filter(p => p.status === "high" || p.status === "low")
  const summarySections = summary ? parseSummarySections(summary) : []

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-lg">
                <Upload className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Upload Report</h1>
                <p className="text-muted-foreground">AI-powered medical report analysis</p>
              </div>
            </div>
            <Badge variant="secondary" className="gap-1.5 py-1.5 w-fit">
              <Sparkles className="h-3.5 w-3.5" /> Gemini AI
            </Badge>
          </div>
        </div>

        {/* Vertical step flow — all completed steps stay visible */}
        <div className="space-y-5">

          {/* ════════ STEP 1: Who is this report for? ════════ */}
          <Card className={`border-border/50 shadow-sm transition-all ${ownerDone ? "opacity-75" : ""}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {ownerDone ? <CheckCircle2 className="h-5 w-5 text-emerald-500" /> : <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">1</div>}
                  <CardTitle className="text-base">Who is this report for?</CardTitle>
                </div>
                {ownerDone && (
                  <Badge variant="outline" className="text-xs">{ownerType === "myself" ? "Myself" : ownerType === "family" ? ownerName : customName}</Badge>
                )}
              </div>
            </CardHeader>
            {!ownerDone && (
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  {([
                    { key: "myself" as const, label: "Myself", icon: User, desc: "Health Records" },
                    { key: "family" as const, label: "Family", icon: Users, desc: "Family & Others" },
                    { key: "others" as const, label: "Others", icon: UserPlus, desc: "Family & Others" },
                  ]).map((opt) => {
                    const Icon = opt.icon
                    return (
                      <button key={opt.key} onClick={() => { setOwnerType(opt.key); if (opt.key === "myself") { setOwnerName(""); setCustomName("") } }}
                        className={`flex flex-col items-center gap-2 rounded-xl border p-4 transition-all hover:shadow-sm ${ownerType === opt.key ? "border-primary bg-primary/5 shadow-sm" : "border-border/50 bg-card hover:border-primary/30"}`}>
                        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${ownerType === opt.key ? "bg-primary text-primary-foreground" : "bg-secondary"}`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <p className={`text-xs font-semibold ${ownerType === opt.key ? "text-primary" : "text-foreground"}`}>{opt.label}</p>
                      </button>
                    )
                  })}
                </div>
                {ownerType === "family" && (
                  <div>
                    <Label className="text-sm font-medium mb-2 block">Select Relation</Label>
                    <div className="flex flex-wrap gap-2">
                      {FAMILY_RELATIONS.map((rel) => (
                        <Button key={rel} variant={ownerName === rel ? "default" : "outline"} size="sm" onClick={() => setOwnerName(rel)}>{rel}</Button>
                      ))}
                    </div>
                  </div>
                )}
                {ownerType === "others" && (
                  <div className="max-w-sm">
                    <Label className="text-sm font-medium mb-2 block">Enter Name</Label>
                    <Input placeholder="e.g. John Doe" value={customName} onChange={(e) => setCustomName(e.target.value)} className="bg-secondary/30 border-border/50" />
                  </div>
                )}
                <Button onClick={() => setOwnerDone(true)}
                  disabled={(ownerType === "family" && !ownerName) || (ownerType === "others" && !customName)}
                  className="w-full gap-2">
                  Continue <ArrowRight className="h-4 w-4" />
                </Button>
              </CardContent>
            )}
          </Card>

          {/* ════════ STEP 2: Upload PDF ════════ */}
          {ownerDone && (
            <Card className={`border-border/50 shadow-sm transition-all ${classifyData ? "opacity-75" : ""}`}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {classifyData ? <CheckCircle2 className="h-5 w-5 text-emerald-500" /> : <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">2</div>}
                    <CardTitle className="text-base">Upload PDF Report</CardTitle>
                  </div>
                  {classifyData && <Badge variant="outline" className="text-xs">{classifyData.file_name}</Badge>}
                </div>
              </CardHeader>
              {!classifyData && (
                <CardContent className="space-y-4">
                  <input type="file" ref={fileInputRef} accept=".pdf" className="hidden" onChange={(e) => {
                    const f = e.target.files?.[0]
                    if (f && f.name.toLowerCase().endsWith(".pdf")) { setFile(f); setError("") }
                    else setError("Only PDF files are accepted.")
                  }} />
                  {file ? (
                    <div className="flex items-center justify-between rounded-xl border border-primary/30 bg-primary/5 p-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                          <FileText className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-foreground">{file.name}</p>
                          <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon" onClick={() => setFile(null)} className="h-8 w-8"><X className="h-4 w-4" /></Button>
                    </div>
                  ) : (
                    <div className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 transition-all ${dragActive ? "border-primary bg-primary/5" : "border-border/50 bg-secondary/20 hover:border-primary/40"}`}
                      onDragOver={(e) => { e.preventDefault(); setDragActive(true) }} onDragLeave={() => setDragActive(false)} onDrop={handleDrop} onClick={() => fileInputRef.current?.click()}>
                      <Upload className="h-8 w-8 text-primary mb-3" />
                      <p className="text-sm font-semibold text-foreground">Drag & drop or click to browse</p>
                      <p className="text-xs text-muted-foreground">PDF up to 20MB</p>
                    </div>
                  )}
                  <Button onClick={handleUploadAndClassify} disabled={!file || classifying} className="w-full h-12 gap-2">
                    {classifying ? <><Loader2 className="h-4 w-4 animate-spin" /> Classifying report type...</> : <><Sparkles className="h-4 w-4" /> Upload & Detect Report Type</>}
                  </Button>
                </CardContent>
              )}
            </Card>
          )}

          {/* ════════ STEP 3: Report Type Result ════════ */}
          {classifyData && (
            <Card className="border-blue-200 dark:border-blue-800 shadow-sm">
              <CardContent className="p-5">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-900/30">
                    <FileText className="h-6 w-6 text-blue-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Detected Report Type</p>
                    <p className="text-lg font-bold text-blue-600 dark:text-blue-400">{classifyData.report_label || "Medical Report"}</p>
                    {classifyData.classification_reasoning && <p className="text-xs text-muted-foreground mt-0.5">{classifyData.classification_reasoning}</p>}
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-2xl font-bold text-emerald-500">{confidenceNum}%</p>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Confidence</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ════════ PDF Preview Show/Hide ════════ */}
          {classifyData && (
            <Card className="border-border/50 shadow-sm">
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
          )}

          {/* ════════ STEP 4: Extract Clinical Parameters ════════ */}
          {classifyData && !params && (
            <Button onClick={handleExtractParams} disabled={extracting} className="w-full h-12 gap-2" size="lg">
              {extracting ? <><Loader2 className="h-4 w-4 animate-spin" /> Extracting clinical parameters...</> : <><Activity className="h-4 w-4" /> Extract Clinical Parameters</>}
            </Button>
          )}

          {params && params.length > 0 && (
            <Card className="border-border/50 shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                  <CardTitle className="text-base">Clinical Parameters</CardTitle>
                  <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 border-0 text-[10px] font-bold">{params.length} extracted</Badge>
                </div>
              </CardHeader>
              <CardContent>
                {/* Stats row */}
                <div className="flex gap-3 mb-4">
                  {[
                    { label: "Total", value: params.length, bg: "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700", color: "text-gray-700 dark:text-gray-300" },
                    { label: "Normal", value: params.filter(p => p.status === "normal").length, bg: "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800", color: "text-emerald-600" },
                    { label: "Abnormal", value: abnormalParams.length, bg: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800", color: "text-red-600 dark:text-red-400" },
                    { label: "Borderline", value: params.filter(p => p.status === "borderline").length, bg: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800", color: "text-amber-600 dark:text-amber-400" },
                  ].map(s => (
                    <div key={s.label} className={`flex-1 rounded-xl border p-2.5 text-center ${s.bg}`}>
                      <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
                      <p className="text-[9px] font-medium text-muted-foreground uppercase">{s.label}</p>
                    </div>
                  ))}
                </div>
                {/* Table */}
                <div className="overflow-x-auto rounded-xl border border-border/50">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border/50">
                        <th className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Parameter</th>
                        <th className="px-4 py-2.5 text-center text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Value</th>
                        <th className="px-4 py-2.5 text-center text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Normal</th>
                        <th className="px-4 py-2.5 text-center text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Unit</th>
                        <th className="px-4 py-2.5 text-right text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {params.map((p, i) => (
                        <tr key={i} className="border-b border-border/30 last:border-0 hover:bg-secondary/20">
                          <td className="px-4 py-3">
                            <p className="font-semibold text-foreground text-sm">{p.name}</p>
                            {p.source && <p className="text-[10px] text-muted-foreground">Source: {p.source}</p>}
                          </td>
                          <td className={`px-4 py-3 text-center font-bold ${p.status === "high" ? "text-red-500" : p.status === "low" ? "text-amber-500" : "text-blue-500"}`}>{p.value}</td>
                          <td className="px-4 py-3 text-center text-muted-foreground text-xs">{p.normal_range || "—"}</td>
                          <td className="px-4 py-3 text-center text-muted-foreground text-xs">{p.unit}</td>
                          <td className="px-4 py-3 text-right">
                            {p.status === "high" ? <span className="text-xs font-bold text-red-500 flex items-center justify-end gap-1"><TrendingUp className="h-3 w-3" />HIGH</span>
                              : p.status === "low" ? <span className="text-xs font-bold text-amber-500 flex items-center justify-end gap-1"><TrendingDown className="h-3 w-3" />LOW</span>
                              : p.status === "borderline" ? <span className="text-xs font-bold text-amber-500">BORDERLINE</span>
                              : <span className="text-xs font-bold text-emerald-500 flex items-center justify-end gap-1"><CheckCircle2 className="h-3 w-3" />NORMAL</span>}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ════════ STEP 5: Generate Summary ════════ */}
          {params && !summary && (
            <Button onClick={handleGenerateSummary} disabled={summarizing} className="w-full h-12 gap-2" size="lg">
              {summarizing ? <><Loader2 className="h-4 w-4 animate-spin" /> Generating AI summary...</> : <><Sparkles className="h-4 w-4" /> Generate AI Summary</>}
            </Button>
          )}

          {summary && summarySections.length > 0 && (
            <Card className="border-border/50 shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                  <CardTitle className="text-base">AI Summary</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {summarySections.map((section, i) => (
                  <div key={i} className="rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/30 p-4">
                    <h4 className="font-bold text-sm text-foreground mb-2">{section.title}</h4>
                    <div className="space-y-1.5">
                      {section.items.map((item, j) => (
                        <p key={j} className="text-sm text-muted-foreground leading-relaxed pl-3 relative before:content-['~'] before:absolute before:left-0 before:text-blue-400">{item}</p>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* ════════ STEP 6: Show Visuals ════════ */}
          {summary && abnormalParams.length > 0 && !showVisuals && (
            <Button onClick={() => setShowVisuals(true)} className="w-full h-12 gap-2" variant="outline" size="lg">
              <BarChart3 className="h-4 w-4" /> Show Parameter Visuals
            </Button>
          )}

          {showVisuals && abnormalParams.length > 0 && (
            <Card className="border-border/50 shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                  <CardTitle className="text-base">Abnormal Parameter Visuals</CardTitle>
                  <Badge className="bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 border-0 text-[10px] font-bold">{abnormalParams.length} flagged</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {abnormalParams.map((p, i) => {
                    const { nmin, nmax } = parseRange(p)
                    const val = typeof p.value === "number" ? p.value : parseFloat(String(p.value))
                    const hasRange = nmin > 0 || nmax > 0
                    const isHigh = p.status === "high"
                    const deviation = hasRange ? (isHigh ? ((val - nmax) / nmax * 100).toFixed(1) : ((nmin - val) / nmin * 100).toFixed(1)) : "0"
                    return (
                      <div key={i} className={`rounded-2xl border bg-card p-5 shadow-sm transition-all duration-200 hover:shadow-md ${
                        isHigh ? "border-red-200/60 dark:border-red-900/40" : "border-amber-200/60 dark:border-amber-900/40"
                      }`}>
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <div className={`h-3 w-3 rounded-full animate-pulse ${isHigh ? "bg-red-500" : "bg-amber-500"}`} />
                            <span className="font-bold text-sm">{p.name}</span>
                          </div>
                          <Badge variant="outline" className={`text-[10px] font-bold border px-2 py-0.5 ${
                            isHigh ? "bg-red-50 text-red-600 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800"
                              : "bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800"
                          }`}>{isHigh ? "HIGH" : "LOW"}</Badge>
                        </div>
                        <div className="flex items-center gap-4">
                          <RadialGauge value={val} nmin={nmin} nmax={nmax} unit={p.unit} isHigh={isHigh} />
                          <div className="flex-1 space-y-2">
                            <div>
                              <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Your Value</p>
                              <p className={`text-xl font-bold ${isHigh ? "text-red-500" : "text-amber-500"}`}>{val} <span className="text-sm font-medium text-muted-foreground">{p.unit}</span></p>
                            </div>
                            {hasRange && (
                              <div>
                                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Normal</p>
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
                        <GaugeBar value={val} nmin={nmin} nmax={nmax} isHigh={isHigh} />
                        {p.insight && (
                          <div className="mt-1 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/30 p-2.5">
                            <p className="text-xs text-muted-foreground"><Sparkles className="h-3 w-3 inline mr-1 text-blue-400" />{p.insight}</p>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* ════════ STEP 7: Save Report ════════ */}
          {(showVisuals || (summary && abnormalParams.length === 0)) && !savedAt && (
            <Button onClick={handleSave} disabled={saving} className="w-full h-12 gap-2 bg-emerald-600 hover:bg-emerald-700" size="lg">
              {saving ? <><Loader2 className="h-4 w-4 animate-spin" /> Saving...</> : <><Save className="h-4 w-4" /> Save Report</>}
            </Button>
          )}

          {/* ════════ SAVED ════════ */}
          {savedAt && (
            <Card className="border-emerald-300 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/20 shadow-sm">
              <CardContent className="p-6 text-center">
                <CheckCircle2 className="h-10 w-10 text-emerald-500 mx-auto mb-3" />
                <h2 className="text-lg font-bold text-foreground mb-1">Report Saved!</h2>
                <p className="text-sm text-muted-foreground mb-3">
                  Saved to {ownerType === "myself" ? "Health Records" : "Family & Others"}
                </p>
                <div className="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-background rounded-full px-3 py-1.5 border mb-4">
                  <Clock className="h-3 w-3" />
                  {new Date(savedAt).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })} at {new Date(savedAt).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                </div>
                <div className="flex gap-3 justify-center">
                  <Button onClick={handleReset} size="sm" className="gap-2"><Upload className="h-3.5 w-3.5" /> Upload Another</Button>
                  <Button variant="outline" size="sm" className="gap-2" asChild>
                    <Link href={ownerType === "myself" ? "/dashboard/health-records" : "/dashboard/family-others"}>
                      View in {ownerType === "myself" ? "Records" : "Family"} <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </Button>
                  {savedReportId && (
                    <Button variant="outline" size="sm" className="gap-2" asChild>
                      <Link href={`/dashboard/report/${savedReportId}`}>View Report <ArrowRight className="h-3.5 w-3.5" /></Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error */}
          {error && (
            <Card className="border-destructive/30 bg-destructive/5">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" /> {error}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
