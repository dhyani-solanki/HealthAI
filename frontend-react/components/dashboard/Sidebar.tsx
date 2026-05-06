"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { clearAuth, getUserName, getInitials } from "@/lib/auth";
import {
  LayoutDashboard,
  MessageSquare,
  Pill,
  FileHeart,
  Users,
  BarChart3,
  Upload,
  LogOut,
  ChevronLeft,
  ChevronRight,
  HeartPulse,
} from "lucide-react";

interface NavItem {
  label: string;
  icon: React.ReactNode;
  href: string;
  gradient: string;
  highlight?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  {
    label: "Dashboard",
    icon: <LayoutDashboard className="w-5 h-5" />,
    href: "/dashboard",
    gradient: "from-blue-500/20 to-blue-600/5",
  },
  {
    label: "MediGenius",
    icon: <MessageSquare className="w-5 h-5" />,
    href: "/dashboard/medigenius",
    gradient: "from-blue-500/20 to-cyan-500/5",
  },
  {
    label: "MediScan",
    icon: <Pill className="w-5 h-5" />,
    href: "/dashboard/mediscan",
    gradient: "from-purple-500/20 to-purple-600/5",
  },
  {
    label: "Upload Report",
    icon: <Upload className="w-5 h-5" />,
    href: "/dashboard/upload-report",
    gradient: "from-indigo-500/20 to-indigo-600/5",
    highlight: true,
  },
  {
    label: "My Records",
    icon: <FileHeart className="w-5 h-5" />,
    href: "/dashboard/health-records",
    gradient: "from-emerald-500/20 to-emerald-600/5",
  },
  {
    label: "Family Records",
    icon: <Users className="w-5 h-5" />,
    href: "/dashboard/family-others",
    gradient: "from-orange-500/20 to-orange-600/5",
  },
  {
    label: "Report Guide",
    icon: <BarChart3 className="w-5 h-5" />,
    href: "/dashboard/data-insights",
    gradient: "from-pink-500/20 to-pink-600/5",
  },
  {
    label: "Reminders",
    icon: <HeartPulse className="w-5 h-5" />,
    href: "/dashboard/reminders",
    gradient: "from-cyan-500/20 to-cyan-600/5",
  },
];

export function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const userName = getUserName();
  const initials = getInitials(userName);
  const [collapsed, setCollapsed] = useState(false);

  function handleLogout() {
    clearAuth();
    router.push("/");
  }

  function isActive(href: string) {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  }

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="fixed left-0 top-0 h-screen z-50 flex flex-col border-r overflow-hidden"
      style={{
        background: "linear-gradient(180deg, #0d1117 0%, #111827 100%)",
        borderColor: "rgba(255,255,255,0.07)",
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 flex-shrink-0" style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: "linear-gradient(135deg, #667eea, #764ba2)" }}
        >
          <HeartPulse className="w-5 h-5 text-white" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              <span className="text-sm font-bold text-white tracking-tight whitespace-nowrap">HealthAI</span>
              <p className="text-[10px] text-slate-500 whitespace-nowrap">AI-Powered Health Insights</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {!collapsed && (
          <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500 px-3 mb-3">
            Health Modules
          </p>
        )}
        {NAV_ITEMS.map((item) => {
          const active = isActive(item.href);
          return (
            <motion.button
              key={item.label}
              whileTap={{ scale: 0.97 }}
              onClick={() => router.push(item.href)}
              className={`w-full flex items-center gap-3 rounded-xl transition-all duration-200 ${
                collapsed ? "justify-center px-2 py-3" : "px-3 py-2.5"
              }`}
              style={{
                background: active
                  ? "linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.1))"
                  : item.highlight
                    ? "linear-gradient(135deg, rgba(99,102,241,0.12), rgba(99,102,241,0.04))"
                    : "transparent",
                border: active
                  ? "1px solid rgba(102,126,234,0.3)"
                  : item.highlight
                    ? "1px solid rgba(99,102,241,0.25)"
                    : "1px solid transparent",
                color: active ? "#fff" : item.highlight ? "#a5b4fc" : "#8b949e",
              }}
              title={collapsed ? item.label : undefined}
            >
              <span className="flex-shrink-0" style={{ color: active ? "#667eea" : "#8b949e" }}>
                {item.icon}
              </span>
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: "auto" }}
                    exit={{ opacity: 0, width: 0 }}
                    className="text-sm font-medium whitespace-nowrap overflow-hidden"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          );
        })}
      </nav>

      {/* User profile + collapse toggle */}
      <div className="flex-shrink-0 px-3 pb-4 space-y-3" style={{ borderTop: "1px solid rgba(255,255,255,0.07)", paddingTop: "12px" }}>
        {/* Profile */}
        <div className={`flex items-center gap-3 ${collapsed ? "justify-center" : ""}`}>
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
            style={{ background: "linear-gradient(135deg, #667eea, #764ba2)" }}
          >
            {initials}
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <p className="text-sm font-medium text-white truncate">{userName}</p>
                <p className="text-[10px] text-slate-500">Health Dashboard</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Actions */}
        <div className={`flex ${collapsed ? "flex-col items-center" : "items-center"} gap-2`}>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleLogout}
            className={`flex items-center gap-2 rounded-lg text-xs font-medium transition-all ${
              collapsed ? "p-2" : "px-3 py-2 flex-1"
            }`}
            style={{
              background: "rgba(239,68,68,0.1)",
              border: "1px solid rgba(239,68,68,0.2)",
              color: "#F87171",
            }}
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
            {!collapsed && <span>Logout</span>}
          </motion.button>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => setCollapsed(!collapsed)}
            className="p-2 rounded-lg transition-all"
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.07)",
              color: "#8b949e",
            }}
            title={collapsed ? "Expand" : "Collapse"}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </motion.button>
        </div>
      </div>
    </motion.aside>
  );
}
