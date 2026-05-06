const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("health_token");
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  authenticated = true
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (authenticated) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export interface LoginResponse {
  access_token: string;
  user_name: string;
  token_type: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  }, false);
}

export interface SignupPayload {
  full_name: string;
  email: string;
  password: string;
  phone?: string;
  gender?: string;
  date_of_birth?: string;
  blood_group?: string;
}

export async function signup(payload: SignupPayload): Promise<{ message: string }> {
  return request("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  }, false);
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export interface DashboardStats {
  total_chats: number;
  total_scans: number;
  total_records: number;
  total_family_conditions: number;
  total_family_reports: number;
  active_reminders: number;
  recent_chats: { role: string; content: string }[];
  upcoming_reminders: { title: string; reminder_time: string }[];
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return request<DashboardStats>("/dashboard/stats");
}

// ── Health Records ───────────────────────────────────────────────────────────
export interface HealthRecord {
  id: number;
  record_type: string;
  title: string;
  description: string | null;
  doctor_name: string | null;
  hospital_name: string | null;
  record_date: string;
  file_path: string | null;
  created_at: string;
}

export async function getHealthRecords(): Promise<HealthRecord[]> {
  return request<HealthRecord[]>("/health-records/");
}

export async function deleteHealthRecord(id: number): Promise<{ message: string }> {
  return request(`/health-records/${id}`, { method: "DELETE" });
}

// ── MedReport Analyzer ──────────────────────────────────────────────────────
export interface MedReportParam {
  name: string;
  value: number;
  unit: string;
  status: string;
  normal_range?: string;
  normal_min?: number | null;
  normal_max?: number | null;
  source?: string;
  insight?: string;
}

export interface MedReportResult {
  report_id: number;
  report_type: string;
  report_label: string;
  confidence: string;
  classification_reasoning?: string;
  parameters: MedReportParam[];
  summary: string;
  owner_type: string;
  owner_name: string | null;
  health_record_id: number | null;
  status: string;
  message: string;
}

export async function uploadMedReport(
  file: File,
  ownerType: string,
  ownerName: string | null
): Promise<MedReportResult> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);
  formData.append("owner_type", ownerType);
  if (ownerName) formData.append("owner_name", ownerName);

  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}/medreport/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export interface ClassifyResult {
  file_name: string;
  file_path: string;
  raw_text: string;
  report_type: string;
  report_label: string;
  confidence: string;
  classification_reasoning?: string;
}

export async function classifyMedReport(file: File): Promise<ClassifyResult> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);

  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}/medreport/classify`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Classification failed" }));
    throw new Error(err.detail || "Classification failed");
  }
  return res.json();
}

export interface ExtractParamsResult {
  parameters: MedReportParam[];
  param_count: number;
}

export async function extractMedReportParams(raw_text: string, report_type: string): Promise<ExtractParamsResult> {
  return request<ExtractParamsResult>("/medreport/extract-params", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text, report_type }),
  });
}

export interface GenerateSummaryResult {
  summary: string;
}

export async function generateMedReportSummary(report_type: string, parameters: MedReportParam[]): Promise<GenerateSummaryResult> {
  return request<GenerateSummaryResult>("/medreport/generate-summary", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report_type, parameters }),
  });
}

export interface SaveReportPayload {
  file_name: string;
  file_path: string;
  report_type: string;
  report_label: string;
  confidence: string;
  parameters: MedReportParam[];
  summary: string;
  owner_type: string;
  owner_name?: string | null;
}

export interface SaveReportResult {
  report_id: number;
  health_record_id: number | null;
  saved_at: string;
  message: string;
}

export async function saveMedReport(payload: SaveReportPayload): Promise<SaveReportResult> {
  return request<SaveReportResult>("/medreport/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export interface MedReportListItem {
  id: number;
  file_name: string;
  report_type: string;
  report_label: string;
  confidence: string;
  parameters: MedReportParam[];
  owner_type: string;
  owner_name: string | null;
  summary: string;
  upload_date: string;
  status: string;
}

export async function listMedReports(
  ownerType?: string,
  ownerName?: string
): Promise<MedReportListItem[]> {
  const params = new URLSearchParams();
  if (ownerType) params.set("owner_type", ownerType);
  if (ownerName) params.set("owner_name", ownerName);
  const qs = params.toString();
  return request<MedReportListItem[]>(`/medreport/reports${qs ? `?${qs}` : ""}`);
}

export async function getMedReport(id: number): Promise<MedReportListItem> {
  return request<MedReportListItem>(`/medreport/reports/${id}`);
}

export async function deleteMedReport(id: number): Promise<{ message: string }> {
  return request(`/medreport/reports/${id}`, { method: "DELETE" });
}

export async function bulkDeleteMedReports(ids: number[]): Promise<{ message: string; deleted: number }> {
  return request("/medreport/reports/bulk-delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report_ids: ids }),
  });
}

export async function fetchReportPdfBlob(reportId: number): Promise<string> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${BASE_URL}/medreport/pdf/${reportId}`, { headers });
  if (!res.ok) throw new Error("Failed to load PDF");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function fetchPdfByPathBlob(filePath: string): Promise<string> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${BASE_URL}/medreport/pdf-by-path?file_path=${encodeURIComponent(filePath)}`, { headers });
  if (!res.ok) throw new Error("Failed to load PDF");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export interface FamilyMember {
  name: string;
  report_count: number;
  reports: MedReportListItem[];
}

export async function getFamilyReports(): Promise<{ family_members: FamilyMember[] }> {
  return request<{ family_members: FamilyMember[] }>("/medreport/family-reports");
}

// ── Data Insights ────────────────────────────────────────────────────────────
export interface ReportInfoItem {
  key: string;
  label: string;
  icon: string;
  description: string;
  parameters: string[];
  what_it_tells: string;
  when_needed: string;
}

export async function getReportInfo(): Promise<ReportInfoItem[]> {
  return request<ReportInfoItem[]>("/data-insights/report-info");
}

// ── MediGenius (Chat) ───────────────────────────────────────────────────────
export interface ChatHistoryItem {
  id: number;
  role: string;
  content: string;
  source?: string;
  timestamp: string;
}

export interface ChatResponse {
  reply: string;
  source: string;
  timestamp: string;
  session_id?: number;
}

export interface ChatSessionItem {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export async function sendChatMessage(message: string, sessionId?: number): Promise<ChatResponse> {
  return request<ChatResponse>("/medigenius/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId || null }),
  });
}

export async function getChatHistory(limit = 50): Promise<ChatHistoryItem[]> {
  return request<ChatHistoryItem[]>(`/medigenius/history?limit=${limit}`);
}

export async function clearChatHistory(): Promise<{ message: string }> {
  return request("/medigenius/history", { method: "DELETE" });
}

export async function getChatSessions(): Promise<ChatSessionItem[]> {
  return request<ChatSessionItem[]>("/medigenius/sessions");
}

export async function createChatSession(): Promise<ChatSessionItem> {
  return request<ChatSessionItem>("/medigenius/sessions", { method: "POST" });
}

export async function deleteChatSession(sessionId: number): Promise<{ message: string }> {
  return request(`/medigenius/sessions/${sessionId}`, { method: "DELETE" });
}

export async function getSessionMessages(sessionId: number): Promise<ChatHistoryItem[]> {
  return request<ChatHistoryItem[]>(`/medigenius/sessions/${sessionId}/messages`);
}

// ── MediScan ────────────────────────────────────────────────────────────────
export interface MediScanResult {
  id: number;
  medicine_name: string;
  scan_result: string;
  scanned_at: string;
  image_data?: string | null;
}

export async function scanMedicineByName(medicineName: string): Promise<MediScanResult> {
  return request<MediScanResult>("/mediscan/scan", {
    method: "POST",
    body: JSON.stringify({ medicine_name: medicineName }),
  });
}

export async function scanMedicineByImage(file: File): Promise<MediScanResult> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);

  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}/mediscan/scan-image`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Scan failed" }));
    throw new Error(err.detail || "Scan failed");
  }
  return res.json();
}

export async function getScanHistory(): Promise<MediScanResult[]> {
  return request<MediScanResult[]>("/mediscan/history");
}

export async function clearScanHistory(): Promise<{ message: string }> {
  return request("/mediscan/history", { method: "DELETE" });
}

export async function deleteScanItem(scanId: number): Promise<{ message: string }> {
  return request(`/mediscan/history/${scanId}`, { method: "DELETE" });
}

export async function getMedicineSuggestions(query: string, limit: number = 10): Promise<string[]> {
  const result = await request<{ suggestions: string[] }>(`/mediscan/suggest?q=${encodeURIComponent(query)}&limit=${limit}`);
  return result.suggestions || [];
}

// ── Reminders ───────────────────────────────────────────────────────────────
export interface Reminder {
  id: number;
  whatsapp_number: string | null;
  title: string;
  description: string | null;
  reminder_type: string;
  reminder_time: string;
  is_recurring: boolean;
  recurrence_pattern: string | null;
  is_active: boolean;
  status: string;
  created_at: string;
}

export interface ReminderCreate {
  whatsapp_number?: string;
  title: string;
  description?: string;
  reminder_type: string;
  reminder_time: string;
  is_recurring?: boolean;
  recurrence_pattern?: string;
}

export interface ReminderUpdate {
  whatsapp_number?: string;
  title?: string;
  description?: string;
  reminder_time?: string;
  is_active?: boolean;
  status?: string;
  is_recurring?: boolean;
  recurrence_pattern?: string;
}

export async function getReminders(): Promise<Reminder[]> {
  return request<Reminder[]>("/reminders/");
}

export async function getUpcomingReminders(): Promise<Reminder[]> {
  return request<Reminder[]>("/reminders/upcoming");
}

export async function createReminder(data: ReminderCreate): Promise<Reminder> {
  return request<Reminder>("/reminders/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateReminder(reminderId: number, data: ReminderUpdate): Promise<Reminder> {
  return request<Reminder>(`/reminders/${reminderId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteReminder(reminderId: number): Promise<{ message: string }> {
  return request(`/reminders/${reminderId}`, { method: "DELETE" });
}

export async function saveWhatsAppNumber(whatsappNumber: string): Promise<{ message: string; whatsapp_number: string }> {
  return request<{ message: string; whatsapp_number: string }>("/reminders/whatsapp-number", {
    method: "POST",
    body: JSON.stringify({ whatsapp_number: whatsappNumber }),
  });
}

export async function getWhatsAppNumber(): Promise<{ whatsapp_number: string | null; has_number: boolean }> {
  return request<{ whatsapp_number: string | null; has_number: boolean }>("/reminders/whatsapp-number");
}

export interface ReportsResponse {
  reports: string[];
  total: number;
}

export async function getAvailableReports(): Promise<ReportsResponse> {
  return request<ReportsResponse>("/reminders/reports");
}

export interface ReportDetails {
  name: string;
  details: {
    category: string;
    description: string;
    best_time: string;
    fasting_required: string;
    fasting_hours: string;
    sample_type: string;
    preparation: string[];
    avoid_before_test: string[];
    instructions: string[];
    who_should_take: string[];
    frequency: string;
    notes: string;
  };
}

export async function getReportDetails(reportName: string): Promise<ReportDetails> {
  return request<ReportDetails>(`/reminders/reports/${reportName}`);
}

// Phone Verification
export interface PhoneStatus {
  phone_number: string | null;
  phone_verified: boolean;
}

export async function getPhoneStatus(): Promise<PhoneStatus> {
  return request<PhoneStatus>("/reminders/phone/status");
}

export interface SendCodeResponse {
  message: string;
  phone_number: string;
  already_verified: boolean;
  validation_code: string | null;
}

export async function sendVerificationCode(phoneNumber: string): Promise<SendCodeResponse> {
  return request<SendCodeResponse>("/reminders/phone/send-code", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber }),
  });
}

export async function confirmPhoneVerification(phoneNumber: string): Promise<{ message: string; phone_verified: boolean }> {
  return request<{ message: string; phone_verified: boolean }>("/reminders/phone/confirm", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber }),
  });
}
