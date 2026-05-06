"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getDashboardStats, type DashboardStats } from "@/lib/api"
import { getUserName } from "@/lib/auth"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Loader2,
  ArrowRight,
  Bot,
  Scan,
  FileText,
  Users,
  BarChart3,
  Upload,
  MessageSquare,
  Clock,
  Activity,
  Heart,
  Shield,
  TrendingUp,
} from "lucide-react"
import Link from "next/link"

const quickActions = [
  { title: "MediGenius", desc: "AI health assistant", icon: Bot, href: "/dashboard/medigenius" },
  { title: "MediScan", desc: "Scan medications", icon: Scan, href: "/dashboard/mediscan" },
  { title: "My Records", desc: "View medical records", icon: FileText, href: "/dashboard/health-records" },
  { title: "Family Records", desc: "Family health tracking", icon: Users, href: "/dashboard/family-others" },
  { title: "Upload Report", desc: "AI-powered analysis", icon: Upload, href: "/dashboard/upload-report" },
  { title: "Report Guide", desc: "Health analytics", icon: BarChart3, href: "/dashboard/data-insights" },
  { title: "Reminders", desc: "Medicine & test reminders", icon: Clock, href: "/dashboard/reminders" },
]

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const userName = getUserName()

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .catch((err) => setError(err.message || "Failed to load"))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center gap-4">
        <Activity className="h-12 w-12 text-muted-foreground" />
        <p className="text-lg font-medium">Unable to load dashboard</p>
        <p className="text-sm text-muted-foreground max-w-sm">{error || "Could not reach the backend."}</p>
        <Button onClick={() => window.location.reload()}>Try Again</Button>
      </div>
    )
  }

  const statCards = [
    { label: "AI Conversations", value: stats.total_chats, icon: MessageSquare, color: "text-primary" },
    { label: "Medicine Scans", value: stats.total_scans, icon: Scan, color: "text-chart-2" },
    { label: "Health Records", value: stats.total_records, icon: FileText, color: "text-success" },
    { label: "Family Records", value: stats.total_family_reports, icon: Users, color: "text-warning" },
  ]

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              Welcome back, {userName}
            </h1>
            <p className="mt-1 text-muted-foreground">
              Your health dashboard overview
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="gap-1.5 py-1.5 border-success/30 bg-success/5 text-success">
              <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
              System Online
            </Badge>
            <Badge variant="secondary" className="gap-1.5 py-1.5">
              <Shield className="h-3.5 w-3.5" />
              Secure
            </Badge>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.label} className="border-border/50 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                    <p className="mt-2 text-3xl font-bold tabular-nums">{stat.value}</p>
                  </div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-secondary">
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Health Score + Quick Actions */}
      <div className="mb-8 grid gap-6 lg:grid-cols-3">
        {/* Health Overview */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Heart className="h-5 w-5 text-primary" />
              Health Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Records analyzed</span>
              <span className="font-semibold">{stats.total_records}</span>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-muted-foreground">Data completeness</span>
                <span className="font-semibold">{Math.min(100, Math.round((stats.total_records / 10) * 100))}%</span>
              </div>
              <Progress value={Math.min(100, Math.round((stats.total_records / 10) * 100))} className="h-2" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Active reminders</span>
              <Badge variant="secondary">{stats.active_reminders}</Badge>
            </div>
            <div className="rounded-lg bg-primary/5 border border-primary/20 p-3">
              <div className="flex items-center gap-2 text-sm">
                <TrendingUp className="h-4 w-4 text-primary" />
                <span className="font-medium text-foreground">Keep it up!</span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Regular health tracking helps you stay on top of your wellness.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="lg:col-span-2 border-border/50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {quickActions.map((action) => {
                const Icon = action.icon
                return (
                  <Link key={action.title} href={action.href}>
                    <div className="flex items-center gap-3 rounded-xl border border-border/50 bg-card p-4 transition-all hover:bg-secondary/50 hover:border-primary/30 hover:shadow-sm cursor-pointer">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                        <Icon className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-foreground">{action.title}</p>
                        <p className="text-xs text-muted-foreground">{action.desc}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </Link>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Chats */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-base">
                <MessageSquare className="h-4 w-4 text-primary" />
                Recent Conversations
              </CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard/medigenius">
                  View All
                  <ArrowRight className="ml-1 h-3 w-3" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {stats.recent_chats.length > 0 ? (
              <div className="space-y-3">
                {stats.recent_chats.slice(0, 4).map((chat, i) => (
                  <div key={i} className="flex items-start gap-3 rounded-lg border border-border/50 p-3">
                    <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                      chat.role === "user" ? "bg-primary text-primary-foreground" : "bg-primary/10"
                    }`}>
                      {chat.role === "user" ? (
                        <Users className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4 text-primary" />
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                      {chat.content}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8">
                <MessageSquare className="h-10 w-10 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground">No conversations yet</p>
                <Button variant="outline" size="sm" className="mt-3" asChild>
                  <Link href="/dashboard/medigenius">Start a Chat</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Upcoming Reminders */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Clock className="h-4 w-4 text-primary" />
              Upcoming Reminders
            </CardTitle>
          </CardHeader>
          <CardContent>
            {stats.upcoming_reminders.length > 0 ? (
              <div className="space-y-3">
                {stats.upcoming_reminders.slice(0, 5).map((r, i) => (
                  <div key={i} className="flex items-center gap-3 rounded-lg border border-border/50 p-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-warning/10">
                      <Clock className="h-4 w-4 text-warning" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{r.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {r.reminder_time?.slice(0, 16).replace("T", " ")}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8">
                <Clock className="h-10 w-10 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground">No upcoming reminders</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
