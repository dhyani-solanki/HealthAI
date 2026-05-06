"use client";

import { motion } from "framer-motion";
import { getUserName } from "@/lib/auth";

interface HeaderProps {
  userName?: string;
}

export function Header({ userName }: HeaderProps) {
  const name = userName || getUserName();

  return (
    <motion.div
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className="mb-2"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: "#F1F5F9" }}>
            Welcome back,{" "}
            <span
              style={{
                background: "linear-gradient(90deg,#60A5FA,#A78BFA)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              {name}
            </span>{" "}
            👋
          </h1>
          <p className="text-sm mt-1" style={{ color: "#64748B" }}>
            Your personal health overview in one place.
          </p>
        </div>

        {/* Avatar */}
        <div className="flex items-center gap-3">
          <div
            className="w-11 h-11 rounded-2xl flex items-center justify-center text-base font-bold text-white shadow-lg"
            style={{
              background: "linear-gradient(135deg,#3B82F6,#8B5CF6)",
              boxShadow: "0 4px 16px rgba(59,130,246,0.3)",
            }}
          >
            {name[0]?.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Divider */}
      <div
        className="mt-5 mb-7 h-px"
        style={{ background: "linear-gradient(90deg,rgba(59,130,246,0.4),rgba(139,92,246,0.2),transparent)" }}
      />
    </motion.div>
  );
}
