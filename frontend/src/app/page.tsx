import Link from "next/link";
import { Zap, ShieldCheck, TrendingUp, AlertTriangle, Cpu, ArrowRight, CheckCircle2, ShoppingBag, BarChart3, RefreshCw } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 selection:bg-blue-500 selection:text-white">
      
      {/* Header Navigation */}
      <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 border-b border-slate-800/60">
        <div className="flex items-center gap-3">
          <div className="bg-white rounded-lg px-3 py-1.5 flex items-center shadow-md border border-slate-200/20">
            <img src="/logo.jpeg?v=2" alt="Razorpay Logo" className="h-7 sm:h-8 w-auto max-w-[160px] object-contain" />
          </div>
          <span className="text-xl sm:text-2xl font-bold tracking-tight text-white">Merchant Pulse <span className="text-blue-500 font-extrabold">AI</span></span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/checkout"
            target="_blank"
            className="hidden sm:flex items-center gap-2 rounded-lg bg-slate-800 hover:bg-slate-700 px-4 py-2 text-sm font-medium text-slate-200 border border-slate-700 transition-all"
          >
            <ShoppingBag className="h-4 w-4 text-emerald-400" />
            <span>Buyer Checkout Demo</span>
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 transition-all"
          >
            <span>Open Merchant Dashboard</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative mx-auto max-w-7xl px-6 pt-16 pb-20 text-center lg:pt-24">
        
        {/* Glow backdrop */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 h-96 w-96 rounded-full bg-blue-600/20 blur-[120px] pointer-events-none"></div>

        {/* Badge */}
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-semibold text-blue-400 mb-8 shadow-sm">
          <Cpu className="h-4 w-4 text-blue-400" />
          <span>Razorpay Hackathon Entry — AI Growth & Agentic Commerce</span>
        </div>

        {/* Headline & Tagline */}
        <h1 className="mx-auto max-w-4xl text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          From customer signal to <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400 bg-clip-text text-transparent">recovered revenue.</span>
        </h1>
        
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400 leading-relaxed">
          An autonomous multi-agent AI revenue intelligence and recovery platform for Razorpay merchants. Continuously detects emerging payment friction, correlates Google Play Store reviews with checkout telemetry, quantifies revenue at risk, and autonomously helps affected buyers complete their purchases.
        </p>

        {/* CTAs */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="flex items-center gap-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 px-7 py-3.5 text-base font-bold text-white shadow-xl shadow-blue-600/30 transition-all active:scale-95"
          >
            <span>Launch Merchant Command Center</span>
            <ArrowRight className="h-5 w-5" />
          </Link>

          <Link
            href="/checkout"
            target="_blank"
            className="flex items-center gap-2.5 rounded-xl bg-slate-800/90 hover:bg-slate-700/90 border border-slate-700 px-7 py-3.5 text-base font-semibold text-slate-200 shadow-md transition-all active:scale-95"
          >
            <ShoppingBag className="h-5 w-5 text-emerald-400" />
            <span>Test Interactive Buyer Checkout</span>
          </Link>
        </div>

        {/* Metric Banner */}
        <div className="mx-auto mt-16 max-w-4xl grid grid-cols-2 sm:grid-cols-4 gap-4 p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-2xl glass-card">
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-blue-400">2m 41s</div>
            <div className="text-xs text-slate-400 font-medium mt-1">Mean Time to Detect (MTTD)</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-emerald-400">₹1,42,800</div>
            <div className="text-xs text-slate-400 font-medium mt-1">Revenue Recovered</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-amber-400">₹1,10,880</div>
            <div className="text-xs text-slate-400 font-medium mt-1">Revenue At Risk Identified</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-extrabold text-indigo-400">71.1%</div>
            <div className="text-xs text-slate-400 font-medium mt-1">Recovery Conversion Rate</div>
          </div>
        </div>

      </section>

      {/* Core Autonomous Loop Section */}
      <section className="mx-auto max-w-7xl px-6 py-16 border-t border-slate-800/80">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">The Central Autonomous Loop</h2>
          <p className="text-slate-400 mt-2 text-sm sm:text-base">DETECT → DIAGNOSE → PREDICT → ACT → RECOVER → LEARN</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-blue-500/40 transition-all">
            <div className="h-10 w-10 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-4 font-bold">1</div>
            <h3 className="text-lg font-semibold text-white">Signal Intelligence Agent</h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Scrapes real-time Google Play Store reviews and customer feedback, analyzing sentiment, payment keywords, and time-window clustering to detect emerging problems in minutes.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-amber-500/40 transition-all">
            <div className="h-10 w-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4 font-bold">2</div>
            <h3 className="text-lg font-semibold text-white">Root Cause & Revenue Risk</h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Correlates customer review complaints with payment telemetry and checkout conversion drops. Quantifies exact revenue at risk and projects 2-hour business impact.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/40 transition-all">
            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4 font-bold">3</div>
            <h3 className="text-lg font-semibold text-white">Buyer Recovery Agent</h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Intervenes during failed buyer checkouts with context-aware assistance, intelligently routing customers to healthy alternative gateways (e.g. Card vs degraded UPI).
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500">
        <p>Merchant Pulse AI — Built for Razorpay Hackathon | Detect. Diagnose. Recover. Grow.</p>
      </footer>

    </div>
  );
}
