"use client";

import { motion } from "framer-motion";

interface Chat {
  role:    string;
  content: string;
}

interface Reminder {
  title:         string;
  reminder_time: string;
}

interface ActivityFeedProps {
  recentChats:       Chat[];
  upcomingReminders: Reminder[];
}

const containerVariants = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.06 } },
};

const rowVariants = {
  hidden: { opacity: 0, x: -10 },
  show:   { opacity: 1, x: 0, transition: { duration: 0.35 } },
};

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <span className="text-[10px] font-bold uppercase tracking-[0.15em]" style={{ color: "#64748B" }}>
        {children}
      </span>
      <div className="flex-1 h-px" style={{ background: "rgba(255,255,255,0.06)" }} />
    </div>
  );
}

export function ActivityFeed({ recentChats, upcomingReminders }: ActivityFeedProps) {
  return (
    <div>
      <SectionLabel>Recent Activity</SectionLabel>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <ActivityCard title="💬 Recent Conversations" accentColor="rgba(59,130,246,0.2)" border="rgba(59,130,246,0.2)">
          <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-2">
            {recentChats.length > 0 ? recentChats.slice(0, 5).map((chat, i) => (
              <motion.div
                key={i}
                variants={rowVariants}
                className="flex items-start gap-3 p-3 rounded-xl"
                style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)" }}
              >
                <span className="text-base flex-shrink-0">{chat.role === "user" ? "🧑" : "🤖"}</span>
                <p className="text-xs leading-relaxed line-clamp-2" style={{ color: "#94A3B8" }}>{chat.content}</p>
              </motion.div>
            )) : <EmptyState icon="💬" label="No conversations yet." />}
          </motion.div>
        </ActivityCard>

        <ActivityCard title="⏰ Upcoming Reminders" accentColor="rgba(251,146,60,0.15)" border="rgba(251,146,60,0.2)">
          <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-2">
            {upcomingReminders.length > 0 ? upcomingReminders.slice(0, 5).map((r, i) => (
              <motion.div
                key={i}
                variants={rowVariants}
                className="flex items-center gap-3 p-3 rounded-xl"
                style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)" }}
              >
                <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: "#FB923C" }} />
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium truncate text-white">{r.title}</div>
                  <div className="text-[10px] mt-0.5" style={{ color: "#64748B" }}>
                    {r.reminder_time?.slice(0, 16).replace("T", " ")}
                  </div>
                </div>
              </motion.div>
            )) : <EmptyState icon="⏰" label="No upcoming reminders." />}
          </motion.div>
        </ActivityCard>
      </div>
    </div>
  );
}

function ActivityCard({
  title, accentColor, border, children,
}: {
  title: string; accentColor: string; border: string; children: React.ReactNode;
}) {
  return (
    <div
      className="p-5 rounded-2xl"
      style={{ background: accentColor, border: `1px solid ${border}`, backdropFilter: "blur(12px)" }}
    >
      <h3 className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: "#64748B" }}>{title}</h3>
      {children}
    </div>
  );
}

function EmptyState({ icon, label }: { icon: string; label: string }) {
  return (
    <div className="text-center py-8" style={{ color: "#475569" }}>
      <div className="text-2xl mb-2 opacity-40">{icon}</div>
      <p className="text-xs">{label}</p>
    </div>
  );
}
