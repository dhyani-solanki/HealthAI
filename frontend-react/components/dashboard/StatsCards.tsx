"use client";

import { motion, type Variants } from "framer-motion";
import Image from "next/image";

interface Stat {
  key:        string;
  label:      string;
  icon:       string;   // path inside /assets/
  color:      string;   // text accent
  gradFrom:   string;
  gradTo:     string;
}

const STATS: Stat[] = [
  { key: "total_chats",             label: "Chats",     icon: "/assets/chat.png",        color: "#60A5FA", gradFrom: "rgba(59,130,246,0.15)",  gradTo: "rgba(59,130,246,0.04)"  },
  { key: "total_scans",             label: "Scans",     icon: "/assets/medicine.png",    color: "#C084FC", gradFrom: "rgba(192,132,252,0.15)", gradTo: "rgba(192,132,252,0.04)" },
  { key: "total_records",           label: "Records",   icon: "/assets/record.png",      color: "#34D399", gradFrom: "rgba(52,211,153,0.15)",  gradTo: "rgba(52,211,153,0.04)"  },
  { key: "total_family_conditions", label: "Family",    icon: "/assets/family.png",      color: "#FB923C", gradFrom: "rgba(251,146,60,0.15)",  gradTo: "rgba(251,146,60,0.04)"  },
  { key: "active_reminders",        label: "Reminders", icon: "/assets/datainsight.png", color: "#F472B6", gradFrom: "rgba(244,114,182,0.15)", gradTo: "rgba(244,114,182,0.04)" },
];

const containerVariants: Variants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.07, delayChildren: 0.1 },
  },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20, scale: 0.97 },
  show:   { opacity: 1, y: 0,  scale: 1, transition: { duration: 0.4, ease: "easeOut" } },
};

interface StatsCardsProps {
  data: Record<string, number>;
}

export function StatsCards({ data }: StatsCardsProps) {
  return (
    <div className="mb-9">
      <SectionLabel>Overview</SectionLabel>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4"
      >
        {STATS.map((stat) => (
          <StatCard key={stat.key} stat={stat} value={data[stat.key] ?? 0} />
        ))}
      </motion.div>
    </div>
  );
}

function StatCard({ stat, value }: { stat: Stat; value: number }) {
  return (
    <motion.div
      variants={cardVariants}
      whileHover={{ scale: 1.03, y: -3, transition: { duration: 0.18 } }}
      whileTap={{ scale: 0.98 }}
      style={{
        background: `linear-gradient(145deg, ${stat.gradFrom}, ${stat.gradTo})`,
        border: `1px solid ${stat.gradFrom}`,
        borderRadius: "1.25rem",
        backdropFilter: "blur(12px)",
      }}
      className="relative overflow-hidden p-5 cursor-default"
    >
      {/* Subtle glow blob */}
      <div
        className="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-25 blur-xl pointer-events-none"
        style={{ background: stat.color }}
      />

      {/* Icon */}
      <div
        className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
        style={{ background: `${stat.gradFrom}`, border: `1px solid ${stat.color}30` }}
      >
        <Image src={stat.icon} alt={stat.label} width={22} height={22} className="object-contain" />
      </div>

      {/* Number */}
      <div
        className="text-3xl font-extrabold tabular-nums leading-none mb-1"
        style={{ color: stat.color }}
      >
        {value}
      </div>

      {/* Label */}
      <div className="text-xs font-semibold uppercase tracking-widest" style={{ color: "#64748B" }}>
        {stat.label}
      </div>
    </motion.div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <span
        className="text-[10px] font-bold uppercase tracking-[0.15em]"
        style={{ color: "#64748B" }}
      >
        {children}
      </span>
      <div className="flex-1 h-px" style={{ background: "rgba(255,255,255,0.06)" }} />
    </div>
  );
}
