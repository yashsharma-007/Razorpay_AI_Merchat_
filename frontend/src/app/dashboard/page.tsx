"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  TrendingUp, 
  AlertTriangle, 
  Clock, 
  ArrowUpRight, 
  Activity,
  CheckCircle2,
  Bot,
  ShieldAlert
} from "lucide-react";
import { api } from "@/lib/api";

export default function DashboardOverview() {
  const [data, setData] = useState<any>(null);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [dashRes, incRes] = await Promise.all([
        api.getDashboard(),
        api.getIncidents()
      ]);
      setData(dashRes);
      setIncidents(incRes);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400 text-sm">
        <span>Loading Merchant Telemetry...</span>
      </div>
    );
  }

  const kpis = data.kpis;
  const growth = data.growth_impact;
  const health = data.payment_health?.methods || [];
  const acquirers = data.payment_health?.acquirers || [];
  const activeIncident = incidents.find((i: any) => i.status === "recovering" || i.status === "active");

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* Incident Alert Banner */}
      {activeIncident ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-center gap-3.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-rose-100 border border-rose-200 shrink-0">
              <ShieldAlert className="h-5 w-5 text-rose-600" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold text-rose-700 uppercase tracking-wider bg-rose-100 px-2 py-0.5 rounded border border-rose-200">Incident #{activeIncident.id?.slice(-4)}</span>
                <span className="text-xs text-rose-700 font-semibold">Auto-Mitigation Active</span>
              </div>
              <h2 className="text-base font-bold text-slate-900 mt-1">{activeIncident.title}</h2>
            </div>
          </div>

          <div className="flex items-center gap-5 shrink-0">
            <div className="text-right">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Revenue At Risk</div>
              <div className="text-base font-bold text-amber-700">₹{activeIncident.revenue_at_risk?.toLocaleString("en-IN")}</div>
            </div>
            <Link
              href="/dashboard/incidents"
              className="rounded-lg bg-rose-600 hover:bg-rose-700 px-4 py-2 text-xs font-semibold text-white transition-colors shadow-xs flex items-center gap-1.5"
            >
              <span>Investigate Incident</span>
              <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3.5 flex items-center justify-between text-xs text-emerald-900 shadow-xs">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span className="font-semibold">All payment gateways operating normally. Zero active revenue incidents.</span>
          </div>
          <span className="font-mono text-[11px] text-slate-500 font-medium">System MTTD: {kpis.mttd}</span>
        </div>
      )}

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1: Revenue Recovered */}
        <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-2 shadow-xs hover:border-slate-300 transition-all">
          <div className="flex items-center justify-between text-[11px] text-slate-500 font-semibold uppercase tracking-wider">
            <span>Revenue Recovered</span>
            <TrendingUp className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 tracking-tight">
            ₹{kpis.revenue_recovered?.toLocaleString("en-IN")}
          </div>
          <div className="text-xs text-slate-500 flex items-center gap-1 font-medium">
            <span className="text-emerald-700 font-bold">+{kpis.ai_recoveries_count}</span> buyers saved by AI Agent
          </div>
        </div>

        {/* KPI 2: Revenue At Risk */}
        <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-2 shadow-xs hover:border-slate-300 transition-all">
          <div className="flex items-center justify-between text-[11px] text-slate-500 font-semibold uppercase tracking-wider">
            <span>Revenue At Risk</span>
            <AlertTriangle className="h-4 w-4 text-amber-600" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-600 tracking-tight">
            ₹{kpis.revenue_at_risk?.toLocaleString("en-IN")}
          </div>
          <div className="text-xs text-slate-500 font-medium">
            Active incident assessment
          </div>
        </div>

        {/* KPI 3: Payment Success Rate */}
        <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-2 shadow-xs hover:border-slate-300 transition-all">
          <div className="flex items-center justify-between text-[11px] text-slate-500 font-semibold uppercase tracking-wider">
            <span>Success Rate</span>
            <Activity className="h-4 w-4 text-blue-600" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {kpis.payment_success_rate}%
          </div>
          <div className="text-xs text-slate-500 font-medium">
            Conversion: <span className="text-slate-800 font-semibold">{kpis.checkout_conversion}%</span>
          </div>
        </div>

        {/* KPI 4: Mean Time To Detect */}
        <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-2 shadow-xs hover:border-slate-300 transition-all">
          <div className="flex items-center justify-between text-[11px] text-slate-500 font-semibold uppercase tracking-wider">
            <span>Detection Speed (MTTD)</span>
            <Clock className="h-4 w-4 text-blue-600" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#0c66e4] tracking-tight">
            {kpis.mttd}
          </div>
          <div className="text-xs text-slate-500 font-medium">
            Signal to incident creation
          </div>
        </div>

      </div>

      {/* 2 Clean Columns: AI Impact & Gateway Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: AI Growth Impact */}
        <div className="lg:col-span-2 rounded-xl bg-white p-6 border border-slate-200 space-y-5 shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">AI Revenue Recovery Impact</h2>
              <p className="text-xs text-slate-500 mt-0.5">Autonomous buyer recovery outcomes during payment gateway friction</p>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 border border-blue-200">
              <Bot className="h-4 w-4 text-blue-600" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3.5">
            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Revenue Saved</div>
              <div className="text-xl font-extrabold text-emerald-600 mt-1">
                ₹{growth.revenue_recovered?.toLocaleString("en-IN")}
              </div>
            </div>

            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Buyers Saved</div>
              <div className="text-xl font-extrabold text-blue-600 mt-1">
                {growth.customers_recovered}
              </div>
            </div>

            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Recovery Rate</div>
              <div className="text-xl font-extrabold text-indigo-600 mt-1">
                {growth.recovery_rate_pct}%
              </div>
            </div>
          </div>

          {/* Acquirer Switch Routing Health Matrix */}
          <div className="pt-4 border-t border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider">Bank Acquirer Switch Health & Traffic Allocation</h3>
              <span className="text-[10px] text-slate-500 font-mono font-medium">Dynamic Smart Routing</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {acquirers.map((acq: any) => (
                <div key={acq.code} className="rounded-lg bg-slate-50 p-3 border border-slate-200 flex items-center justify-between text-xs">
                  <div>
                    <div className="font-bold text-slate-800">{acq.bank}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">
                      Latency: <span className={acq.latency_ms > 1000 ? "text-rose-600 font-bold" : "text-emerald-700 font-medium"}>{acq.latency_ms}ms</span> • Traffic: <span className="text-slate-700 font-medium">{acq.recommended_traffic_pct}%</span>
                    </div>
                  </div>
                  <span className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                    acq.status === 'degraded' ? 'bg-rose-100 text-rose-700 border border-rose-200' : 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                  }`}>
                    {acq.status === 'degraded' ? 'Degraded' : '97% Success'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Payment Gateway Health */}
        <div className="rounded-xl bg-white p-6 border border-slate-200 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-base">Payment Gateway Health</h3>
            <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">Live Status</span>
          </div>

          <div className="space-y-2.5">
            {health.map((method: any) => {
              const isDegraded = method.status === "degraded" || method.status === "down";
              return (
                <div 
                  key={method.code} 
                  className={`rounded-lg p-3 border flex items-center justify-between text-xs transition-all ${
                    isDegraded ? "bg-rose-50 border-rose-200 text-rose-900" : "bg-slate-50 border-slate-200 text-slate-800"
                  }`}
                >
                  <span className="font-semibold text-slate-800">{method.name}</span>
                  <span className={`font-bold px-2.5 py-0.5 rounded text-[10px] flex items-center gap-1.5 ${
                    isDegraded ? 'bg-rose-100 text-rose-700 border border-rose-200' : 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                  }`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${isDegraded ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'}`}></span>
                    {isDegraded ? "Degraded" : "Operational"}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

      </div>

    </div>
  );
}
