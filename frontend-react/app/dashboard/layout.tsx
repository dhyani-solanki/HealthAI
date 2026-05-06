"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { isLoggedIn } from "@/lib/auth"
import Navbar from "@/components/dashboard/Navbar"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/")
    } else {
      setReady(true)
    }
  }, [router])

  if (!ready) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pt-14">
        {children}
      </main>
    </div>
  )
}
