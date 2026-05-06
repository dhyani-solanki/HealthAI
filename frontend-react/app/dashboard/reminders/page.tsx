"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import {
  getReminders,
  createReminder,
  deleteReminder,
  updateReminder,
  getAvailableReports,
  getReportDetails,
  getPhoneStatus,
  sendVerificationCode,
  confirmPhoneVerification,
  type Reminder,
  type ReminderCreate,
  type ReportDetails,
} from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Loader2,
  Bell,
  Plus,
  Trash2,
  Edit,
  Clock,
  Smartphone,
  CheckCircle2,
  XCircle,
  Pill,
  FileText,
  Calendar,
  AlertCircle,
} from "lucide-react"
import Link from "next/link"

export default function RemindersPage() {
  const router = useRouter()
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [phoneNumber, setPhoneNumber] = useState<string | null>(null)
  const [phoneVerified, setPhoneVerified] = useState(false)
  const [loading, setLoading] = useState(true)
  const [sendingCode, setSendingCode] = useState(false)
  const [confirmingVerification, setConfirmingVerification] = useState(false)
  const [creatingReminder, setCreatingReminder] = useState(false)
  const [showPhoneDialog, setShowPhoneDialog] = useState(false)
  const [showReminderDialog, setShowReminderDialog] = useState(false)
  const [editingReminder, setEditingReminder] = useState<Reminder | null>(null)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [updatingReminder, setUpdatingReminder] = useState(false)

  // Edit form state
  const [editTitle, setEditTitle] = useState("")
  const [editDescription, setEditDescription] = useState("")
  const [editDate, setEditDate] = useState("")
  const [editHour, setEditHour] = useState("12")
  const [editMinute, setEditMinute] = useState("00")
  const [editPeriod, setEditPeriod] = useState<"AM" | "PM">("AM")
  const [editIsRecurring, setEditIsRecurring] = useState(false)
  const [editRecurrencePattern, setEditRecurrencePattern] = useState<"daily" | "weekly" | "monthly">("daily")
  const [newPhoneNumber, setNewPhoneNumber] = useState("")
  const [validationCode, setValidationCode] = useState<string | null>(null)
  const [verificationStep, setVerificationStep] = useState<"phone" | "call">("phone")
  const [availableReports, setAvailableReports] = useState<string[]>([])
  const [selectedReportDetails, setSelectedReportDetails] = useState<ReportDetails | null>(null)

  // Form state
  const [reminderType, setReminderType] = useState<"medicine" | "report">("medicine")
  const [medicineName, setMedicineName] = useState("")
  const [medicineNotes, setMedicineNotes] = useState("")
  const [selectedReport, setSelectedReport] = useState("")
  const [reminderDate, setReminderDate] = useState("")
  const [reminderHour, setReminderHour] = useState("12")
  const [reminderMinute, setReminderMinute] = useState("00")
  const [reminderPeriod, setReminderPeriod] = useState<"AM" | "PM">("AM")
  const [isRecurring, setIsRecurring] = useState(false)
  const [recurrencePattern, setRecurrencePattern] = useState<"daily" | "weekly" | "monthly">("daily")

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [remindersData, phoneData, reportsData] = await Promise.all([
        getReminders(),
        getPhoneStatus(),
        getAvailableReports(),
      ])
      setReminders(remindersData)
      setPhoneNumber(phoneData.phone_number)
      setPhoneVerified(phoneData.phone_verified)
      setAvailableReports(reportsData.reports)
    } catch (error) {
      console.error("Failed to load data:", error)
    } finally {
      setLoading(false)
    }
  }

  // Step 1: Enter phone → Twilio calls the number
  const handleSendCode = async () => {
    if (!newPhoneNumber.trim()) return
    setSendingCode(true)
    try {
      const result = await sendVerificationCode(newPhoneNumber)
      if (result.already_verified) {
        setPhoneNumber(newPhoneNumber)
        setPhoneVerified(true)
        setShowPhoneDialog(false)
        resetVerificationState()
        alert("This phone number is already verified!")
      } else {
        setValidationCode(result.validation_code)
        setVerificationStep("call")
      }
    } catch (error: any) {
      alert(error.message || "Failed to initiate verification.")
    } finally {
      setSendingCode(false)
    }
  }

  // Step 2: User completed the call → check if verified
  const handleConfirmVerification = async () => {
    setConfirmingVerification(true)
    try {
      const result = await confirmPhoneVerification(newPhoneNumber)
      if (result.phone_verified) {
        setPhoneNumber(newPhoneNumber)
        setPhoneVerified(true)
        setShowPhoneDialog(false)
        resetVerificationState()
        alert("Phone number verified! You will now receive SMS reminders.")
      } else {
        alert("Not yet verified. Please answer the call and enter the code on your phone keypad.")
      }
    } catch (error: any) {
      alert(error.message || "Verification check failed.")
    } finally {
      setConfirmingVerification(false)
    }
  }

  const resetVerificationState = () => {
    setNewPhoneNumber("")
    setValidationCode(null)
    setVerificationStep("phone")
  }

  const handleReportChange = async (reportName: string) => {
    setSelectedReport(reportName)
    if (reportName) {
      try {
        const details = await getReportDetails(reportName)
        setSelectedReportDetails(details)
      } catch (error) {
        console.error("Failed to fetch report details:", error)
        setSelectedReportDetails(null)
      }
    } else {
      setSelectedReportDetails(null)
    }
  }

  const handleCreateReminder = async () => {
    if (!reminderDate) {
      alert("Please select date and time for the reminder")
      return
    }

    if (reminderType === "medicine" && !medicineName.trim()) {
      alert("Please enter medicine name")
      return
    }

    if (reminderType === "report" && !selectedReport) {
      alert("Please select a report")
      return
    }

    const reminderData: ReminderCreate = {
      title: reminderType === "medicine" ? medicineName : selectedReport,
      description: reminderType === "medicine" ? medicineNotes : undefined,
      reminder_type: reminderType,
      reminder_time: (() => {
        let h = parseInt(reminderHour)
        if (reminderPeriod === "AM" && h === 12) h = 0
        if (reminderPeriod === "PM" && h !== 12) h += 12
        const localDate = new Date(`${reminderDate}T${String(h).padStart(2, "0")}:${reminderMinute}:00`)
        return localDate.toISOString()
      })(),
      is_recurring: isRecurring,
      recurrence_pattern: isRecurring ? recurrencePattern : undefined,
    }

    setCreatingReminder(true)
    try {
      await createReminder(reminderData)
      setShowReminderDialog(false)
      // Reset form
      setMedicineName("")
      setMedicineNotes("")
      setSelectedReport("")
      setSelectedReportDetails(null)
      setReminderDate("")
      setReminderHour("12")
      setReminderMinute("00")
      setReminderPeriod("AM")
      setIsRecurring(false)
      setRecurrencePattern("daily")
      // Reload reminders
      await loadData()
    } catch (error) {
      console.error("Failed to create reminder:", error)
      alert("Failed to create reminder. Please try again.")
    } finally {
      setCreatingReminder(false)
    }
  }

  const openEditDialog = (reminder: Reminder) => {
    setEditingReminder(reminder)
    setEditTitle(reminder.title)
    setEditDescription(reminder.description || "")
    // Parse the reminder time
    const dt = new Date(reminder.reminder_time)
    const year = dt.getFullYear()
    const month = String(dt.getMonth() + 1).padStart(2, "0")
    const day = String(dt.getDate()).padStart(2, "0")
    setEditDate(`${year}-${month}-${day}`)
    let hours = dt.getHours()
    const minutes = dt.getMinutes()
    if (hours === 0) { setEditHour("12"); setEditPeriod("AM") }
    else if (hours < 12) { setEditHour(String(hours)); setEditPeriod("AM") }
    else if (hours === 12) { setEditHour("12"); setEditPeriod("PM") }
    else { setEditHour(String(hours - 12)); setEditPeriod("PM") }
    setEditMinute(String(minutes).padStart(2, "0"))
    setEditIsRecurring(reminder.is_recurring)
    setEditRecurrencePattern((reminder.recurrence_pattern as "daily" | "weekly" | "monthly") || "daily")
    setShowEditDialog(true)
  }

  const handleUpdateReminder = async () => {
    if (!editingReminder || !editDate) return
    setUpdatingReminder(true)
    try {
      let h = parseInt(editHour)
      if (editPeriod === "AM" && h === 12) h = 0
      if (editPeriod === "PM" && h !== 12) h += 12
      const localDate = new Date(`${editDate}T${String(h).padStart(2, "0")}:${editMinute}:00`)
      await updateReminder(editingReminder.id, {
        title: editTitle,
        description: editDescription || undefined,
        reminder_time: localDate.toISOString(),
        is_active: true,
        status: "pending",
        is_recurring: editIsRecurring,
        recurrence_pattern: editIsRecurring ? editRecurrencePattern : undefined,
      })
      setShowEditDialog(false)
      setEditingReminder(null)
      await loadData()
    } catch (error) {
      console.error("Failed to update reminder:", error)
      alert("Failed to update reminder.")
    } finally { setUpdatingReminder(false) }
  }

  const handleDeleteReminder = async (id: number) => {
    if (!confirm("Are you sure you want to delete this reminder?")) return

    try {
      await deleteReminder(id)
      await loadData()
    } catch (error) {
      console.error("Failed to delete reminder:", error)
      alert("Failed to delete reminder. Please try again.")
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("en-IN", {
      timeZone: "Asia/Kolkata",
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "sent":
        return <Badge className="bg-green-500 hover:bg-green-600">Sent</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">Back</Button>
              </Link>
              <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                Reminders
              </h1>
            </div>
            <p className="mt-1 text-muted-foreground">
              Manage your medicine and medical test reminders
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Dialog open={showPhoneDialog} onOpenChange={(open) => {
              setShowPhoneDialog(open)
              if (!open) resetVerificationState()
            }}>
              <DialogTrigger asChild>
                <Button variant="outline" className="gap-2">
                  <Smartphone className="h-4 w-4" />
                  {phoneVerified ? (
                    <span className="flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3 text-green-500" />
                      Verified
                    </span>
                  ) : "Verify Phone"}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Phone Verification</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  {/* Step 1: Enter phone number */}
                  {verificationStep === "phone" && (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="phone">Phone Number (with country code)</Label>
                        <Input
                          id="phone"
                          placeholder="+919876543210"
                          value={newPhoneNumber}
                          onChange={(e) => setNewPhoneNumber(e.target.value)}
                        />
                        <p className="text-xs text-muted-foreground">
                          Include country code (e.g., +91 for India). Twilio will call this number to verify it.
                        </p>
                      </div>
                      <Button onClick={handleSendCode} disabled={sendingCode || !newPhoneNumber.trim()} className="w-full">
                        {sendingCode ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                        {sendingCode ? "Calling..." : "Verify Phone Number"}
                      </Button>
                    </>
                  )}

                  {/* Step 2: Answer Twilio call */}
                  {verificationStep === "call" && (
                    <>
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 text-center">
                        <p className="text-sm text-blue-700 mb-2 font-medium">
                          Twilio is calling {newPhoneNumber}
                        </p>
                        <p className="text-sm text-blue-600 mb-3">
                          Answer the call and enter this code on your phone keypad:
                        </p>
                        <p className="text-4xl font-bold text-blue-800 tracking-widest">
                          {validationCode}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" onClick={() => setVerificationStep("phone")} className="flex-1">
                          Change Number
                        </Button>
                        <Button onClick={handleConfirmVerification} disabled={confirmingVerification} className="flex-1">
                          {confirmingVerification ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                          {confirmingVerification ? "Checking..." : "I've Completed the Call"}
                        </Button>
                      </div>
                    </>
                  )}

                  {phoneVerified && phoneNumber && (
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <p className="text-sm text-green-700 flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4" />
                        Current verified number: {phoneNumber}
                      </p>
                    </div>
                  )}
                </div>
              </DialogContent>
            </Dialog>

            <Dialog open={showReminderDialog} onOpenChange={setShowReminderDialog}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  New Reminder
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Create New Reminder</DialogTitle>
                </DialogHeader>
                <div className="space-y-6 py-4">
                  {/* Reminder Type Selection */}
                  <div className="space-y-2">
                    <Label>Reminder Type</Label>
                    <Select value={reminderType} onValueChange={(value: "medicine" | "report") => setReminderType(value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="medicine">
                          <div className="flex items-center gap-2">
                            <Pill className="h-4 w-4" />
                            Medicine Reminder
                          </div>
                        </SelectItem>
                        <SelectItem value="report">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            Medical Test/Report Reminder
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Medicine Input */}
                  {reminderType === "medicine" && (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="medicine-name">Medicine Name *</Label>
                        <Input
                          id="medicine-name"
                          placeholder="e.g., Paracetamol 500mg"
                          value={medicineName}
                          onChange={(e) => setMedicineName(e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="medicine-notes">Notes (Optional)</Label>
                        <Textarea
                          id="medicine-notes"
                          placeholder="e.g., Take after meals"
                          value={medicineNotes}
                          onChange={(e) => setMedicineNotes(e.target.value)}
                          rows={2}
                        />
                      </div>
                    </div>
                  )}

                  {/* Report Selection */}
                  {reminderType === "report" && (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="report-select">Select Report *</Label>
                        <Select value={selectedReport} onValueChange={handleReportChange}>
                          <SelectTrigger id="report-select">
                            <SelectValue placeholder="Choose a medical test" />
                          </SelectTrigger>
                          <SelectContent>
                            {availableReports.map((report) => (
                              <SelectItem key={report} value={report}>
                                {report}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      {selectedReportDetails && (
                        <Card className="bg-secondary/50">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-base flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              {selectedReportDetails.name}
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-3 text-sm">
                            <div className="grid grid-cols-2 gap-3">
                              <div>
                                <p className="font-medium text-muted-foreground">Best Time</p>
                                <p>{selectedReportDetails.details.best_time}</p>
                              </div>
                              <div>
                                <p className="font-medium text-muted-foreground">Fasting Required</p>
                                <p>{selectedReportDetails.details.fasting_required}</p>
                              </div>
                            </div>
                            <div>
                              <p className="font-medium text-muted-foreground mb-1">Preparation</p>
                              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                                {selectedReportDetails.details.preparation.map((prep, i) => (
                                  <li key={i}>{prep}</li>
                                ))}
                              </ul>
                            </div>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  )}

                  {/* Date and Time */}
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="reminder-date">Date *</Label>
                      <Input
                        id="reminder-date"
                        type="date"
                        value={reminderDate}
                        onChange={(e) => setReminderDate(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Time *</Label>
                      <div className="grid grid-cols-3 gap-2">
                        <Select value={reminderHour} onValueChange={setReminderHour}>
                          <SelectTrigger>
                            <SelectValue placeholder="Hour" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.from({ length: 12 }, (_, i) => i + 1).map((h) => (
                              <SelectItem key={h} value={String(h)}>{h}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Select value={reminderMinute} onValueChange={setReminderMinute}>
                          <SelectTrigger>
                            <SelectValue placeholder="Min" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.from({ length: 60 }, (_, i) => i).map((m) => (
                              <SelectItem key={m} value={String(m).padStart(2, "0")}>
                                {String(m).padStart(2, "0")}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Select value={reminderPeriod} onValueChange={(v: "AM" | "PM") => setReminderPeriod(v)}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="AM">AM</SelectItem>
                            <SelectItem value="PM">PM</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>

                  {/* Recurrence */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="recurring"
                        checked={isRecurring}
                        onChange={(e) => setIsRecurring(e.target.checked)}
                        className="h-4 w-4"
                      />
                      <Label htmlFor="recurring" className="cursor-pointer">
                        Repeat this reminder
                      </Label>
                    </div>

                    {isRecurring && (
                      <Select value={recurrencePattern} onValueChange={(value: "daily" | "weekly" | "monthly") => setRecurrencePattern(value)}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="daily">Daily</SelectItem>
                          <SelectItem value="weekly">Weekly</SelectItem>
                          <SelectItem value="monthly">Monthly</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  </div>

                  <Button onClick={handleCreateReminder} disabled={creatingReminder} className="w-full">
                    {creatingReminder ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    {creatingReminder ? "Creating..." : "Create Reminder"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      {/* Phone Verification Status */}
      {!phoneVerified && (
        <Card className="mb-6 border-warning/50 bg-warning/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-warning" />
              <div className="flex-1">
                <p className="font-medium text-foreground">Phone not verified</p>
                <p className="text-sm text-muted-foreground">
                  Verify your phone number to receive SMS reminder notifications
                </p>
              </div>
              <Button size="sm" onClick={() => setShowPhoneDialog(true)}>
                Verify Phone
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reminders List */}
      <div className="space-y-4">
        {reminders.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Bell className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium text-foreground mb-2">No reminders yet</p>
              <p className="text-sm text-muted-foreground mb-4">
                Create your first reminder to get started
              </p>
              <Button onClick={() => setShowReminderDialog(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Reminder
              </Button>
            </CardContent>
          </Card>
        ) : (
          reminders.map((reminder) => (
            <Card key={reminder.id} className="border-border/50">
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-4 flex-1">
                    <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${
                      reminder.reminder_type === "medicine" ? "bg-primary/10" : "bg-chart-2/10"
                    }`}>
                      {reminder.reminder_type === "medicine" ? (
                        <Pill className="h-6 w-6 text-primary" />
                      ) : (
                        <FileText className="h-6 w-6 text-chart-2" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-foreground">{reminder.title}</h3>
                        {getStatusBadge(reminder.status)}
                      </div>
                      {reminder.description && (
                        <p className="text-sm text-muted-foreground mb-2">{reminder.description}</p>
                      )}
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>{formatDate(reminder.reminder_time)}</span>
                        </div>
                        {reminder.is_recurring && (
                          <Badge variant="outline" className="text-xs">
                            {reminder.recurrence_pattern}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditDialog(reminder)}
                      className="text-muted-foreground hover:text-primary"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteReminder(reminder.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Edit Reminder Dialog */}
      <Dialog open={showEditDialog} onOpenChange={(open) => { setShowEditDialog(open); if (!open) setEditingReminder(null) }}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Reminder</DialogTitle>
          </DialogHeader>
          {editingReminder && (
            <div className="space-y-6 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-title">Title *</Label>
                <Input
                  id="edit-title"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  rows={2}
                />
              </div>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-date">Date *</Label>
                  <Input
                    id="edit-date"
                    type="date"
                    value={editDate}
                    onChange={(e) => setEditDate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Time *</Label>
                  <div className="grid grid-cols-3 gap-2">
                    <Select value={editHour} onValueChange={setEditHour}>
                      <SelectTrigger><SelectValue placeholder="Hour" /></SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 12 }, (_, i) => i + 1).map((h) => (
                          <SelectItem key={h} value={String(h)}>{h}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select value={editMinute} onValueChange={setEditMinute}>
                      <SelectTrigger><SelectValue placeholder="Min" /></SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 60 }, (_, i) => i).map((m) => (
                          <SelectItem key={m} value={String(m).padStart(2, "0")}>
                            {String(m).padStart(2, "0")}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select value={editPeriod} onValueChange={(v: "AM" | "PM") => setEditPeriod(v)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="AM">AM</SelectItem>
                        <SelectItem value="PM">PM</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="edit-recurring"
                    checked={editIsRecurring}
                    onChange={(e) => setEditIsRecurring(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <Label htmlFor="edit-recurring" className="cursor-pointer">
                    Repeat this reminder
                  </Label>
                </div>
                {editIsRecurring && (
                  <Select value={editRecurrencePattern} onValueChange={(value: "daily" | "weekly" | "monthly") => setEditRecurrencePattern(value)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              </div>
              <Button onClick={handleUpdateReminder} disabled={updatingReminder || !editTitle.trim() || !editDate} className="w-full">
                {updatingReminder ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                {updatingReminder ? "Updating..." : "Update Reminder"}
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
