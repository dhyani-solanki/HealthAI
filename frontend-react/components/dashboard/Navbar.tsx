"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useTheme } from "next-themes"
import { getUserName, getInitials, clearAuth } from "@/lib/auth"
import {
  LayoutDashboard,
  Bot,
  Scan,
  FileText,
  Users,
  Upload,
  BarChart3,
  Sun,
  Moon,
  Menu,
  X,
  Heart,
  LogOut,
  Clock,
} from "lucide-react"
import { useState, useEffect } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, highlight: false },
  { href: "/dashboard/medigenius", label: "MediGenius", icon: Bot, highlight: false },
  { href: "/dashboard/mediscan", label: "MediScan", icon: Scan, highlight: false },
  { href: "/dashboard/upload-report", label: "Upload", icon: Upload, highlight: false },
  { href: "/dashboard/health-records", label: "My Records", icon: FileText, highlight: false },
  { href: "/dashboard/family-others", label: "Family Records", icon: Users, highlight: false },
  { href: "/dashboard/data-insights", label: "Report Guide", icon: BarChart3, highlight: false },
  { href: "/dashboard/reminders", label: "Reminders", icon: Clock, highlight: false },
]

export default function Navbar() {
  const pathname = usePathname()
  const router = useRouter()
  const { theme, setTheme } = useTheme()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [userName, setUserName] = useState("User")
  const [initials, setInitials] = useState("U")

  useEffect(() => {
    setMounted(true)
    const n = getUserName()
    setUserName(n)
    setInitials(getInitials(n))
  }, [])

  function handleLogout() {
    clearAuth()
    router.push("/")
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-card/95 backdrop-blur-md shadow-sm" style={{ willChange: "transform", transform: "translateZ(0)" }}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <nav className="relative flex h-14 items-center justify-between">
          {/* Left — Logo */}
          <Link href="/dashboard" className="flex items-center gap-2 shrink-0">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary shadow-sm">
              <Heart className="h-4 w-4 text-primary-foreground" fill="currentColor" />
            </div>
            <span className="text-base font-bold tracking-tight text-foreground hidden sm:block">HealthAI</span>
          </Link>

          {/* Center — Nav links (absolutely centered) */}
          <div className="hidden lg:flex items-center gap-1 absolute left-1/2 -translate-x-1/2 rounded-xl bg-secondary/50 border border-border/40 p-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href))
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[13px] font-medium transition-all duration-150 whitespace-nowrap",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : item.highlight
                        ? "bg-primary/10 text-primary hover:bg-primary/20 font-semibold"
                        : "text-muted-foreground hover:bg-background hover:text-foreground"
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                  {item.label}
                </Link>
              )
            })}
          </div>

          {/* Right — Actions */}
          <div className="flex items-center gap-1 shrink-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
            >
              {mounted && (
                <>
                  <Sun className="h-3.5 w-3.5 rotate-0 scale-100 transition-transform dark:-rotate-90 dark:scale-0" />
                  <Moon className="absolute h-3.5 w-3.5 rotate-90 scale-0 transition-transform dark:rotate-0 dark:scale-100" />
                </>
              )}
              <span className="sr-only">Toggle theme</span>
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                  <Avatar className="h-7 w-7 border-2 border-primary/20">
                    <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-3 py-2">
                  <p className="text-sm font-medium">{userName}</p>
                  <p className="text-xs text-muted-foreground">HealthAI User</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 lg:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              <span className="sr-only">Toggle menu</span>
            </Button>
          </div>
        </nav>
      </div>

      {/* Mobile menu */}
      <div className={cn(
        "border-t border-border/50 bg-card lg:hidden overflow-hidden transition-all duration-200 ease-out",
        mobileMenuOpen ? "max-h-[28rem] opacity-100" : "max-h-0 opacity-0 border-t-0"
      )}>
        <div className="px-4 py-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href))
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : item.highlight
                      ? "bg-primary/10 text-primary font-semibold"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
              >
                <Icon className="h-4.5 w-4.5" />
                {item.label}
              </Link>
            )
          })}
        </div>
      </div>
    </header>
  )
}
