"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { login, signup } from "@/lib/api"
import { setAuth } from "@/lib/auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  Loader2,
  Heart,
  Shield,
  Bot,
  FileText,
  Scan,
  AlertCircle,
  CheckCircle2,
  LogIn,
  UserPlus,
} from "lucide-react"

type Tab = "login" | "signup"

export default function AuthPage() {
  const router = useRouter()
  const [tab, setTab] = useState<Tab>("login")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [loginEmail, setLoginEmail] = useState("")
  const [loginPassword, setLoginPassword] = useState("")
  const [name, setName] = useState("")
  const [signupEmail, setSignupEmail] = useState("")
  const [signupPassword, setSignupPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError(""); setLoading(true)
    try {
      const data = await login(loginEmail, loginPassword)
      setAuth(data.access_token, data.user_name)
      router.push("/dashboard")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally { setLoading(false) }
  }

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault()
    setError(""); setSuccess("")
    if (signupPassword !== confirmPassword) { setError("Passwords don't match"); return }
    if (signupPassword.length < 6) { setError("Password must be at least 6 characters"); return }
    setLoading(true)
    try {
      await signup({ full_name: name, email: signupEmail, password: signupPassword })
      setSuccess("Account created! Please login.")
      setTab("login")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Signup failed")
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex bg-background">
      {/* Left side - branding (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary relative overflow-hidden flex-col items-center justify-center p-12 text-primary-foreground">
        <div className="absolute inset-0 bg-gradient-to-br from-primary via-primary to-primary/80" />
        <div className="relative z-10 max-w-md text-center">
          <div className="mb-8 flex h-20 w-20 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm mx-auto border border-white/20">
            <Heart className="h-10 w-10" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight mb-4">HealthAI</h1>
          <p className="text-lg text-primary-foreground/80 mb-10">
            Your AI-powered personal health companion
          </p>
          <div className="grid gap-4 text-left">
            {[
              { icon: Bot, text: "AI-powered health assistant" },
              { icon: Scan, text: "Medicine identification & scanning" },
              { icon: FileText, text: "Smart report analysis with Gemini" },
              { icon: Shield, text: "Secure & private health tracking" },
            ].map((feature, i) => {
              const Icon = feature.icon
              return (
                <div key={i} className="flex items-center gap-3 rounded-xl bg-white/10 backdrop-blur-sm p-3 border border-white/10">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15">
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="text-sm font-medium">{feature.text}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Right side - auth form */}
      <div className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-[440px]">
          {/* Mobile brand header */}
          <div className="text-center mb-8 lg:hidden">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-primary mb-5 shadow-lg">
              <Heart className="h-8 w-8 text-primary-foreground" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">HealthAI</h1>
            <p className="text-sm mt-2 text-muted-foreground">Your personal AI health companion</p>
          </div>

          <Card className="border-border/50 shadow-lg">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl">
                {tab === "login" ? "Welcome back" : "Create an account"}
              </CardTitle>
              <CardDescription>
                {tab === "login" ? "Sign in to access your health dashboard" : "Get started with your health journey"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Tab switcher */}
              <div className="flex rounded-xl bg-secondary p-1 gap-1 mb-6">
                {(["login", "signup"] as Tab[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => { setTab(t); setError(""); setSuccess("") }}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                      tab === t
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {t === "login" ? <><LogIn className="h-4 w-4" /> Login</> : <><UserPlus className="h-4 w-4" /> Sign Up</>}
                  </button>
                ))}
              </div>

              {/* Messages */}
              {error && (
                <div className="mb-4 flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {error}
                </div>
              )}
              {success && (
                <div className="mb-4 flex items-center gap-2 rounded-xl border border-success/30 bg-success/5 px-4 py-3 text-sm text-success">
                  <CheckCircle2 className="h-4 w-4 shrink-0" />
                  {success}
                </div>
              )}

              {tab === "login" ? (
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      placeholder="you@example.com"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      required
                      className="h-11 bg-secondary/30 border-border/50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Password</Label>
                    <Input
                      type="password"
                      placeholder="Enter your password"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      required
                      className="h-11 bg-secondary/30 border-border/50"
                    />
                  </div>
                  <Button type="submit" disabled={loading} className="w-full h-11 gap-2 mt-2">
                    {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Signing in...</> : <><LogIn className="h-4 w-4" /> Sign In</>}
                  </Button>
                </form>
              ) : (
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Full Name</Label>
                    <Input
                      placeholder="John Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      className="h-11 bg-secondary/30 border-border/50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      placeholder="you@example.com"
                      value={signupEmail}
                      onChange={(e) => setSignupEmail(e.target.value)}
                      required
                      className="h-11 bg-secondary/30 border-border/50"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label>Password</Label>
                      <Input
                        type="password"
                        placeholder="Min 6 chars"
                        value={signupPassword}
                        onChange={(e) => setSignupPassword(e.target.value)}
                        required
                        className="h-11 bg-secondary/30 border-border/50"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Confirm</Label>
                      <Input
                        type="password"
                        placeholder="Repeat password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        className="h-11 bg-secondary/30 border-border/50"
                      />
                    </div>
                  </div>
                  <Button type="submit" disabled={loading} className="w-full h-11 gap-2 mt-2">
                    {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating account...</> : <><UserPlus className="h-4 w-4" /> Create Account</>}
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>

          <p className="text-center text-xs mt-6 text-muted-foreground flex items-center justify-center gap-2">
            <Heart className="h-3.5 w-3.5 text-primary" />
            AI-powered health intelligence
          </p>
        </div>
      </div>
    </div>
  )
}
