"use client";

import { motion, type Variants } from "framer-motion";
import Image from "next/image";
import { ArrowRight } from "lucide-react";
import { IllustrationMediGenius } from "@/components/illustrations/IllustrationMediGenius";
import { IllustrationMediScan }   from "@/components/illustrations/IllustrationMediScan";
import { IllustrationRecords }    from "@/components/illustrations/IllustrationRecords";

interface FeatureCard {
  title:        string;
  desc:         string;
  illustration: React.ReactNode;
  iconSrc:      string;
  gradient:     string;
  borderGrad:   string;
  btnGrad:      string;
  href:         string;
}

const FEATURE_CARDS: FeatureCard[] = [
  {
    title:        "MediGenius",
    desc:         "Ask your AI health assistant anything — symptoms, medications, and more.",
    illustration: <IllustrationMediGenius />,
    iconSrc:      "/assets/chat.png",
    gradient:     "linear-gradient(145deg,rgba(59,130,246,0.18),rgba(59,130,246,0.04))",
    borderGrad:   "rgba(59,130,246,0.3)",
    btnGrad:      "linear-gradient(135deg,#3B82F6,#60A5FA)",
    href:         "#",
  },
  {
    title:        "MediScan",
    desc:         "Identify medicines by name or photo — usage, dosage, and interactions.",
    illustration: <IllustrationMediScan />,
    iconSrc:      "/assets/medicine.png",
    gradient:     "linear-gradient(145deg,rgba(167,139,250,0.18),rgba(167,139,250,0.04))",
    borderGrad:   "rgba(167,139,250,0.3)",
    btnGrad:      "linear-gradient(135deg,#8B5CF6,#A78BFA)",
    href:         "#",
  },
  {
    title:        "Health Records",
    desc:         "Securely manage all your medical records, tests, and prescriptions.",
    illustration: <IllustrationRecords />,
    iconSrc:      "/assets/record.png",
    gradient:     "linear-gradient(145deg,rgba(52,211,153,0.18),rgba(52,211,153,0.04))",
    borderGrad:   "rgba(52,211,153,0.3)",
    btnGrad:      "linear-gradient(135deg,#10B981,#34D399)",
    href:         "#",
  },
];

const containerVariants: Variants = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.1, delayChildren: 0.05 } },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
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

export function FeatureCards() {
  return (
    <div className="mb-9">
      <SectionLabel>Quick Access</SectionLabel>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5"
      >
        {FEATURE_CARDS.map((card) => (
          <FeatureCardItem key={card.title} card={card} />
        ))}
      </motion.div>
    </div>
  );
}

function FeatureCardItem({ card }: { card: FeatureCard }) {
  return (
    <motion.div
      variants={cardVariants}
      whileHover={{ scale: 1.025, y: -5, transition: { duration: 0.2 } }}
      whileTap={{ scale: 0.98, transition: { duration: 0.1 } }}
      className="flex flex-col overflow-hidden cursor-pointer group"
      style={{
        background:    card.gradient,
        border:        `1px solid ${card.borderGrad}`,
        borderRadius:  "1.5rem",
        backdropFilter: "blur(12px)",
      }}
    >
      {/* Illustration */}
      <div
        className="h-40 overflow-hidden flex-shrink-0 relative"
        style={{ borderBottom: `1px solid ${card.borderGrad}` }}
      >
        {card.illustration}
      </div>

      {/* Body */}
      <div className="flex flex-col flex-1 p-5 gap-3">
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: "rgba(255,255,255,0.07)", border: `1px solid ${card.borderGrad}` }}
          >
            <Image src={card.iconSrc} alt={card.title} width={18} height={18} className="object-contain" />
          </div>
          <h3 className="text-base font-bold text-white tracking-tight">{card.title}</h3>
        </div>

        <p className="text-xs leading-relaxed" style={{ color: "#64748B" }}>{card.desc}</p>

        <motion.a
          href={card.href}
          whileTap={{ scale: 0.96 }}
          className="mt-auto flex items-center justify-between px-4 py-2.5 rounded-xl text-sm font-semibold text-white"
          style={{
            background:    card.btnGrad,
            boxShadow:     "0 2px 12px rgba(0,0,0,0.25)",
          }}
        >
          Open {card.title}
          <motion.span
            className="inline-block"
            animate={{ x: 0 }}
            whileHover={{ x: 4 }}
            transition={{ duration: 0.15 }}
          >
            <ArrowRight className="w-4 h-4" />
          </motion.span>
        </motion.a>
      </div>
    </motion.div>
  );
}
