"use client"

import { useEffect, useState, useRef, useCallback } from "react"
import {
  sendChatMessage,
  getChatSessions,
  createChatSession,
  deleteChatSession,
  getSessionMessages,
  clearChatHistory,
  type ChatHistoryItem,
  type ChatSessionItem,
} from "@/lib/api"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Bot,
  Send,
  User,
  Heart,
  Brain,
  Pill,
  Stethoscope,
  Plus,
  Trash2,
  Loader2,
  MessageSquare,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react"

const suggestedQuestions = [
  { icon: Heart, text: "What are the symptoms of high blood pressure?" },
  { icon: Brain, text: "How can I improve my sleep quality?" },
  { icon: Pill, text: "What are common side effects of aspirin?" },
  { icon: Stethoscope, text: "When should I see a doctor for a headache?" },
]

export default function MediGeniusPage() {
  const [sessions, setSessions] = useState<ChatSessionItem[]>([])
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null)
  const [messages, setMessages] = useState<ChatHistoryItem[]>([])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [loadingSessions, setLoadingSessions] = useState(true)
  const [loadingMessages, setLoadingMessages] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mounted, setMounted] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Load sessions on mount
  useEffect(() => {
    setMounted(true)
    getChatSessions()
      .then(setSessions)
      .catch(() => {})
      .finally(() => setLoadingSessions(false))
  }, [])

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  // Load messages for active session
  const loadSession = useCallback(async (sessionId: number) => {
    setActiveSessionId(sessionId)
    setLoadingMessages(true)
    try {
      const msgs = await getSessionMessages(sessionId)
      setMessages(msgs)
    } catch {
      setMessages([])
    } finally {
      setLoadingMessages(false)
    }
  }, [])

  // New chat
  function handleNewChat() {
    setActiveSessionId(null)
    setMessages([])
    setInput("")
    inputRef.current?.focus()
  }

  // Delete session
  async function handleDeleteSession(e: React.MouseEvent, sessionId: number) {
    e.stopPropagation()
    try {
      await deleteChatSession(sessionId)
      setSessions((prev) => prev.filter((s) => s.id !== sessionId))
      if (activeSessionId === sessionId) {
        setActiveSessionId(null)
        setMessages([])
      }
    } catch {}
  }

  // Send message
  async function handleSend(text?: string) {
    const msg = (text || input).trim()
    if (!msg || sending) return
    setInput("")
    setSending(true)

    const tempUser: ChatHistoryItem = {
      id: Date.now(),
      role: "user",
      content: msg,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUser])

    try {
      const res = await sendChatMessage(msg, activeSessionId || undefined)
      const aiMsg: ChatHistoryItem = {
        id: Date.now() + 1,
        role: "assistant",
        content: res.reply,
        source: res.source,
        timestamp: res.timestamp,
      }
      setMessages((prev) => [...prev, aiMsg])

      // If new session was created, update sidebar
      if (res.session_id && !activeSessionId) {
        setActiveSessionId(res.session_id)
        const refreshed = await getChatSessions()
        setSessions(refreshed)
      } else if (res.session_id) {
        // Refresh to update title/order
        const refreshed = await getChatSessions()
        setSessions(refreshed)
      }
    } catch (err) {
      const errMsg: ChatHistoryItem = {
        id: Date.now() + 1,
        role: "assistant",
        content: err instanceof Error ? err.message : "Failed to get response",
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setSending(false)
    }
  }

  // Handle textarea enter
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-[calc(100vh-64px)] bg-background overflow-hidden">
      {/* ── Sidebar ── */}
      <div className={`${sidebarOpen ? "w-72" : "w-0"} flex-shrink-0 transition-all duration-300 overflow-hidden`}>
        <div className="flex h-full w-72 flex-col border-r border-border/50 bg-secondary/30">
          {/* New Chat Button */}
          <div className="p-3">
            <button
              onClick={handleNewChat}
              className="flex w-full items-center gap-3 rounded-lg border border-border/50 px-3 py-3 text-sm font-medium text-foreground transition-colors hover:bg-secondary/80"
            >
              <Plus className="h-4 w-4" />
              New Chat
            </button>
          </div>

          {/* Session List */}
          <div className="flex-1 overflow-y-auto px-3 pb-3">
            {loadingSessions ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : sessions.length === 0 ? (
              <div className="py-8 text-center">
                <MessageSquare className="mx-auto h-8 w-8 text-muted-foreground/30 mb-2" />
                <p className="text-xs text-muted-foreground">No conversations yet</p>
              </div>
            ) : (
              <div className="space-y-1">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => loadSession(session.id)}
                    className={`group flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm cursor-pointer transition-colors ${
                      activeSessionId === session.id
                        ? "bg-secondary text-foreground"
                        : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                    }`}
                  >
                    <MessageSquare className="h-4 w-4 shrink-0" />
                    <span className="flex-1 truncate">{session.title}</span>
                    <button
                      onClick={(e) => handleDeleteSession(e, session.id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-destructive/10 hover:text-destructive"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Disclaimer at bottom */}
          <div className="border-t border-border/50 p-3">
            <p className="text-[10px] text-muted-foreground/60 leading-relaxed text-center">
              MediGenius provides general health info only. Not medical advice.
            </p>
          </div>
        </div>
      </div>

      {/* ── Main Chat Area ── */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Top Bar */}
        <div className="flex items-center gap-3 border-b border-border/50 px-4 py-3 bg-background">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="rounded-lg p-2 text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-colors"
          >
            {sidebarOpen ? <PanelLeftClose className="h-5 w-5" /> : <PanelLeft className="h-5 w-5" />}
          </button>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-foreground">MediGenius</h1>
              <p className="text-[11px] text-muted-foreground">AI Health Assistant</p>
            </div>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              Online
            </span>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto" ref={scrollRef}>
          {loadingMessages ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : messages.length === 0 ? (
            /* ── Empty State ── */
            <div className="flex flex-col items-center justify-center h-full px-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 mb-5">
                <Bot className="h-8 w-8 text-primary" />
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">How can I help you today?</h2>
              <p className="text-sm text-muted-foreground mb-8 max-w-md text-center">
                Ask me about symptoms, medications, health conditions, or any medical questions.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl w-full">
                {suggestedQuestions.map((q, i) => {
                  const Icon = q.icon
                  return (
                    <button
                      key={i}
                      onClick={() => handleSend(q.text)}
                      disabled={sending}
                      className="flex items-center gap-3 rounded-xl border border-border/50 bg-card p-4 text-left text-sm transition-all hover:bg-secondary/50 hover:border-primary/30 disabled:opacity-50"
                    >
                      <Icon className="h-5 w-5 text-primary shrink-0" />
                      <span className="text-foreground">{q.text}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          ) : (
            /* ── Chat Messages ── */
            <div className="mx-auto max-w-3xl px-4 py-6 space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
                  {msg.role === "assistant" && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 mt-1">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div className={`max-w-[75%] ${msg.role === "user" ? "" : ""}`}>
                    <div className={`rounded-2xl px-4 py-3 ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary/50"
                    }`}>
                      {msg.role === "assistant" && msg.source && (
                        <span className="inline-block text-[10px] font-medium text-primary bg-primary/10 rounded px-1.5 py-0.5 mb-1.5">
                          {msg.source}
                        </span>
                      )}
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
                    </div>
                    {mounted && (
                      <p className={`mt-1 text-[11px] px-1 ${
                        msg.role === "user" ? "text-right text-muted-foreground" : "text-muted-foreground"
                      }`}>
                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    )}
                  </div>
                  {msg.role === "user" && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary mt-1">
                      <User className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}
              {sending && (
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 mt-1">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex items-center gap-1.5 rounded-2xl bg-secondary/50 px-4 py-3">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-primary" style={{ animationDelay: "0ms" }} />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-primary" style={{ animationDelay: "150ms" }} />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-primary" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Input Area ── */}
        <div className="border-t border-border/50 bg-background px-4 py-3">
          <div className="mx-auto max-w-3xl">
            <form
              onSubmit={(e: React.FormEvent) => { e.preventDefault(); handleSend() }}
              className="relative flex items-end gap-2 rounded-2xl border border-border/50 bg-secondary/30 px-4 py-3 focus-within:border-primary/50 transition-colors"
            >
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message MediGenius..."
                rows={1}
                className="flex-1 resize-none bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none max-h-32"
                style={{ minHeight: "24px" }}
                disabled={sending}
              />
              <Button
                type="submit"
                size="icon"
                disabled={!input.trim() || sending}
                className="h-8 w-8 shrink-0 rounded-lg"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
            <p className="mt-2 text-center text-[11px] text-muted-foreground/50">
              MediGenius can make mistakes. Always verify with a healthcare professional.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
