"use client"

import { useEffect, useState, useRef, useCallback } from "react"
import { scanMedicineByName, scanMedicineByImage, getScanHistory, clearScanHistory, deleteScanItem, getMedicineSuggestions, type MediScanResult } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Scan,
  Camera,
  Upload,
  Image as ImageIcon,
  Pill,
  AlertTriangle,
  Info,
  X,
  Clock,
  Sparkles,
  Shield,
  Search,
  Loader2,
  Trash2,
  Eye,
  EyeOff,
} from "lucide-react"

function formatScanResult(text: string) {
  // Main section headings that get their own card
  const sectionKeywords = [
    "Medicine Name:",
    "Use:",
    "Uses:",
    "Dosage:",
    "Precautions:",
    "Common Side Effects:",
    "Side Effects:",
    "Disclaimer:",
  ]
  // Sub-info that stays inside the parent card
  const subKeywords = [
    "Source of Information:",
    "Trusted Source:",
    "From Image:",
    "From General Knowledge:",
    "Source:",
  ]
  const allKeywords = [...sectionKeywords, ...subKeywords]

  // Remove all markdown markers
  const cleaned = text.replace(/\*\*/g, "").replace(/\*/g, "").replace(/^#+\s*/gm, "")

  // Split into sections — sub-keywords merge into parent
  const lines = cleaned.split("\n")
  const sections: { heading: string; content: string[] }[] = []
  let current: { heading: string; content: string[] } | null = null

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue

    const isSectionHeading = sectionKeywords.some((kw) => trimmed.startsWith(kw))
    const isSubHeading = subKeywords.some((kw) => trimmed.startsWith(kw))

    if (isSectionHeading) {
      if (current) sections.push(current)
      const colonIdx = trimmed.indexOf(":")
      const heading = trimmed.slice(0, colonIdx + 1)
      const rest = trimmed.slice(colonIdx + 1).trim()
      current = { heading, content: rest ? [rest] : [] }
    } else if (isSubHeading) {
      // Merge sub-info into current section
      if (current) {
        current.content.push(trimmed)
      } else {
        current = { heading: "", content: [trimmed] }
      }
    } else if (current) {
      current.content.push(trimmed)
    } else {
      current = { heading: "", content: [trimmed] }
    }
  }
  if (current) sections.push(current)

  return sections.map((section, i) => {
    const isDisclaimer = section.heading.toLowerCase().startsWith("disclaimer")

    if (isDisclaimer) {
      return (
        <div key={i} className="rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 p-4">
          <p className="font-bold text-amber-700 dark:text-amber-400 mb-1">{section.heading}</p>
          {section.content.map((line, j) => (
            <p key={j} className="text-amber-800 dark:text-amber-300 text-sm leading-relaxed">{line}</p>
          ))}
        </div>
      )
    }

    return (
      <div key={i} className="rounded-xl bg-blue-50/60 dark:bg-slate-800/40 border border-blue-100 dark:border-slate-700 p-4">
        {section.heading && (
          <p className="font-bold text-foreground mb-2">{section.heading}</p>
        )}
        {section.content.map((line, j) => {
          const isSub = subKeywords.some((kw) => line.startsWith(kw))
          if (isSub) {
            return (
              <p key={j} className="text-xs text-muted-foreground/70 italic mb-1">{line}</p>
            )
          }
          return (
            <p key={j} className="text-muted-foreground text-sm leading-relaxed flex gap-2">
              <span className="text-primary/60 select-none">~</span>
              <span>{line.replace(/^[-•–]\s*/, "")}</span>
            </p>
          )
        })}
      </div>
    )
  })
}

export default function MediScanPage() {
  const [query, setQuery] = useState("")
  const [scanning, setScanning] = useState(false)
  const [result, setResult] = useState<MediScanResult | null>(null)
  const [history, setHistory] = useState<MediScanResult[]>([])
  const [error, setError] = useState("")
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [showImage, setShowImage] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => { getScanHistory().then(setHistory).catch(() => {}) }, [])

  // Fetch suggestions with debounce
  const fetchSuggestions = useCallback((searchQuery: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    
    if (!searchQuery.trim()) {
      setSuggestions([])
      setShowSuggestions(false)
      return
    }
    
    debounceRef.current = setTimeout(async () => {
      setLoadingSuggestions(true)
      try {
        const results = await getMedicineSuggestions(searchQuery, 8)
        setSuggestions(results)
        setShowSuggestions(results.length > 0)
      } catch {
        setSuggestions([])
      } finally {
        setLoadingSuggestions(false)
      }
    }, 300)
  }, [])

  // Handle query change
  const handleQueryChange = (value: string) => {
    setQuery(value)
    fetchSuggestions(value)
  }

  // Select suggestion
  const selectSuggestion = (suggestion: string) => {
    setQuery(suggestion)
    setShowSuggestions(false)
    setSuggestions([])
  }

  // Close suggestions on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target as Node)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  async function handleScanByName() {
    if (!query.trim() || scanning) return
    setScanning(true); setError(""); setResult(null)
    try {
      const res = await scanMedicineByName(query.trim())
      setResult(res)
      setHistory((prev) => [res, ...prev])
    } catch (err) { setError(err instanceof Error ? err.message : "Scan failed") }
    finally { setScanning(false) }
  }

  async function handleScanByImage() {
    if (!imageFile || scanning) return
    setScanning(true); setError(""); setResult(null)
    try {
      const res = await scanMedicineByImage(imageFile)
      setResult(res)
      setHistory((prev) => [res, ...prev])
    } catch (err) { setError(err instanceof Error ? err.message : "Image scan failed") }
    finally { setScanning(false) }
  }

  function handleImageSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (f) { setImageFile(f); setImagePreview(URL.createObjectURL(f)) }
  }

  function clearImage() { setImageFile(null); setImagePreview(null) }

  async function handleClearHistory() {
    if (!confirm("Clear all scan history?")) return
    try { await clearScanHistory(); setHistory([]) } catch {}
  }

  async function handleDeleteScan(scanId: number, e: React.MouseEvent) {
    e.stopPropagation()
    try {
      await deleteScanItem(scanId)
      setHistory((prev) => prev.filter((s) => s.id !== scanId))
      if (result?.id === scanId) setResult(null)
    } catch {}
  }

  function resetScan() { setResult(null); setQuery(""); clearImage(); setShowImage(false) }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-lg">
                <Scan className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-foreground">MediScan</h1>
                <p className="text-muted-foreground">AI-powered medication identification</p>
              </div>
            </div>
            <Badge variant="secondary" className="gap-1.5 py-1.5 w-fit">
              <Shield className="h-3.5 w-3.5" />
              AI-Powered Analysis
            </Badge>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Scanner Area */}
          <div className="lg:col-span-2 space-y-5">
            {!result ? (
              <>
                {/* Search by Name */}
                <Card className="border-border/50 shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Search className="h-4 w-4 text-primary" />
                      Search by Name
                    </CardTitle>
                    <CardDescription>Enter the medicine name to get detailed information</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={(e) => { e.preventDefault(); setShowSuggestions(false); handleScanByName() }} className="flex gap-3">
                      <div className="relative flex-1" ref={suggestionsRef}>
                        <Pill className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground z-10" />
                        <Input
                          value={query}
                          onChange={(e) => handleQueryChange(e.target.value)}
                          onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                          placeholder="Enter medicine name (e.g. Paracetamol)"
                          className="pl-10 h-11 bg-secondary/30 border-border/50"
                          disabled={scanning}
                          autoComplete="off"
                        />
                        {/* Suggestions Dropdown */}
                        {showSuggestions && suggestions.length > 0 && (
                          <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                            {loadingSuggestions && (
                              <div className="px-3 py-2 text-sm text-muted-foreground flex items-center gap-2">
                                <Loader2 className="h-3 w-3 animate-spin" />
                                Loading...
                              </div>
                            )}
                            {suggestions.map((suggestion, idx) => (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => selectSuggestion(suggestion)}
                                className="w-full px-3 py-2.5 text-left text-sm hover:bg-secondary/50 flex items-center gap-2 transition-colors border-b border-border/30 last:border-b-0"
                              >
                                <Pill className="h-3.5 w-3.5 text-primary shrink-0" />
                                <span className="truncate">{suggestion}</span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                      <Button type="submit" disabled={!query.trim() || scanning} className="h-11 px-5 gap-2">
                        {scanning && !imageFile ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                        <span className="hidden sm:inline">Search</span>
                      </Button>
                    </form>
                  </CardContent>
                </Card>

                {/* Scan by Image */}
                <Card className="border-border/50 shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Camera className="h-4 w-4 text-primary" />
                      Scan by Image
                    </CardTitle>
                    <CardDescription>Take a clear photo of your medication</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <input type="file" ref={fileRef} onChange={handleImageSelect} accept="image/*" className="hidden" />

                    {imagePreview ? (
                      <div className="flex items-center gap-4">
                        <div className="relative">
                          <img src={imagePreview} alt="Preview" className="h-24 w-24 rounded-xl object-cover shadow-md" />
                          <Button variant="ghost" size="icon" onClick={clearImage} className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-destructive text-destructive-foreground">
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                        <Button onClick={handleScanByImage} disabled={scanning} className="gap-2">
                          {scanning && imageFile ? <><Loader2 className="h-4 w-4 animate-spin" /> Scanning...</> : <><Scan className="h-4 w-4" /> Scan Image</>}
                        </Button>
                      </div>
                    ) : (
                      <div
                        onClick={() => fileRef.current?.click()}
                        className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-border/50 bg-secondary/20 p-12 transition-all hover:border-primary/40 hover:bg-secondary/40"
                      >
                        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                          <ImageIcon className="h-8 w-8 text-primary" />
                        </div>
                        <p className="mb-1 text-sm font-semibold text-foreground">Click to upload an image</p>
                        <p className="text-xs text-muted-foreground">Supports JPG, PNG, HEIC up to 10MB</p>
                      </div>
                    )}

                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      <Button variant="outline" className="h-auto py-3 border-border/50 hover:bg-secondary/50" onClick={() => fileRef.current?.click()}>
                        <div className="flex items-center gap-3">
                          <div className="rounded-lg bg-primary/10 p-2">
                            <Upload className="h-4 w-4 text-primary" />
                          </div>
                          <div className="text-left">
                            <p className="font-medium text-foreground text-sm">Upload Image</p>
                            <p className="text-xs text-muted-foreground">From your gallery</p>
                          </div>
                        </div>
                      </Button>
                      <Button variant="outline" className="h-auto py-3 border-border/50 hover:bg-secondary/50" onClick={() => fileRef.current?.click()}>
                        <div className="flex items-center gap-3">
                          <div className="rounded-lg bg-primary/10 p-2">
                            <Camera className="h-4 w-4 text-primary" />
                          </div>
                          <div className="text-left">
                            <p className="font-medium text-foreground text-sm">Take Photo</p>
                            <p className="text-xs text-muted-foreground">Use your camera</p>
                          </div>
                        </div>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              /* Result Display */
              <div className="space-y-5">
                <Card className="border-border/50 shadow-sm">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
                          <Pill className="h-7 w-7 text-primary" />
                        </div>
                        <div>
                          <h2 className="text-xl font-bold text-foreground">{result.medicine_name}</h2>
                          <p className="mt-1 text-sm text-muted-foreground">
                            Scanned on {new Date(result.scanned_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon" onClick={resetScan} className="rounded-full">
                        <X className="h-5 w-5" />
                      </Button>
                    </div>

                    {/* Show/Hide Image Button */}
                    {result.image_data && (
                      <div className="mt-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowImage(!showImage)}
                          className="gap-2"
                        >
                          {showImage ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          {showImage ? "Hide Image" : "Show Image"}
                        </Button>
                      </div>
                    )}

                    {/* Medicine Image Display */}
                    {showImage && result.image_data && (
                      <div className="mt-4">
                        <img
                          src={`data:image/jpeg;base64,${result.image_data}`}
                          alt="Medicine"
                          className="rounded-xl border border-border/50 max-h-80 w-auto object-contain"
                        />
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card className="border-border/50 shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <div className="rounded-lg bg-primary/10 p-1.5">
                        <Info className="h-4 w-4 text-primary" />
                      </div>
                      Scan Results
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {formatScanResult(result.scan_result)}
                    </div>
                  </CardContent>
                </Card>

                <div className="flex gap-4">
                  <Button onClick={resetScan} className="flex-1 gap-2">
                    <Scan className="h-4 w-4" />
                    Scan Another
                  </Button>
                </div>
              </div>
            )}

            {error && (
              <Card className="border-destructive/30 bg-destructive/5">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 text-sm text-destructive">
                    <AlertTriangle className="h-4 w-4" />
                    {error}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-5">
            {/* How it works */}
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-4 w-4 text-primary" />
                  How It Works
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-5">
                  {[
                    { step: "1", title: "Enter or Upload", desc: "Type medicine name or upload a photo" },
                    { step: "2", title: "AI Analysis", desc: "AI identifies and analyzes the medication" },
                    { step: "3", title: "Get Details", desc: "View uses, dosage, and warnings" },
                  ].map((item) => (
                    <li key={item.step} className="flex gap-4">
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                        {item.step}
                      </span>
                      <div>
                        <p className="font-medium text-foreground">{item.title}</p>
                        <p className="text-sm text-muted-foreground mt-0.5">{item.desc}</p>
                      </div>
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>

            {/* Recent Scans */}
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Clock className="h-4 w-4 text-primary" />
                    Recent Scans
                  </CardTitle>
                  {history.length > 0 && (
                    <Button variant="ghost" size="sm" onClick={handleClearHistory} className="text-destructive text-xs h-7">
                      <Trash2 className="h-3 w-3 mr-1" /> Clear
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {history.length > 0 ? (
                  <div className="space-y-3">
                    {history.slice(0, 5).map((scan) => (
                      <div
                        key={scan.id}
                        className="flex w-full items-center gap-3 rounded-xl border border-border/50 p-3 transition-all hover:bg-secondary/30"
                      >
                        <button
                          onClick={() => setResult(scan)}
                          className="flex flex-1 items-center gap-3 text-left min-w-0"
                        >
                          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 shrink-0">
                            <Pill className="h-5 w-5 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0 overflow-hidden">
                            <p className="text-sm font-medium text-foreground truncate max-w-[180px]">{scan.medicine_name}</p>
                            <p className="text-xs text-muted-foreground">{scan.scanned_at?.slice(0, 10)}</p>
                          </div>
                        </button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => handleDeleteScan(scan.id, e)}
                          className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 shrink-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <Scan className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">No scans yet</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Disclaimer */}
            <Card className="border-warning/30 bg-warning/5 shadow-sm">
              <CardContent className="p-4">
                <div className="flex gap-3">
                  <div className="rounded-lg bg-warning/10 p-2">
                    <AlertTriangle className="h-4 w-4 text-warning" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground text-sm">Important</p>
                    <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">
                      Always verify medication information with your pharmacist or healthcare provider.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
