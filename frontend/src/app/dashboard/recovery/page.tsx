"use client";

import { useEffect, useState } from "react";
import { TrendingUp, Cpu, CheckCircle2, ArrowUpRight, BarChart3, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";

export default function RecoveryAnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [slaData, setSlaData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [res, slaRes] = await Promise.all([
        api.getRecoveryAnalytics(),
        api.getSlaChurnAnalytics()
      ]);
      setData(res);
      setSlaData(slaRes);
    } catch (err) {
      console.error("Error loading recovery analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex items-center gap-3">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"></div>
          <span>Loading Recovery Strategy Analytics...</span>
        </div>
      </div>
    );
  }

  const summary = data.summary;
  const strategies = data.strategy_performance || [];
  const slaPerf = slaData?.sla_performance || {};
  const churnRisk = slaData?.churn_risk_assessment || {};
  const kamActions = slaData?.proactive_kam_actions || [];
  const accountsAtRisk = slaData?.enterprise_merchants_at_risk || [];

  return (
    <div className="space-y-6">
      
      <div>
        <h1 className="text-2xl font-bold text-white">AI Buyer Recovery Analytics</h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Historical strategy performance breakdown and autonomous agent conversion learning
        </p>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <div className="text-xs font-medium text-slate-400">Transactions Attempted</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white mt-2">{summary.transactions_attempted}</div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <div className="text-xs font-medium text-slate-400">Successful Recoveries</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-400 mt-2">{summary.successful_recoveries}</div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <div className="text-xs font-medium text-slate-400">Overall Recovery Rate</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-blue-400 mt-2">{summary.recovery_rate_pct}%</div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800">
          <div className="text-xs font-medium text-slate-400">Total Revenue Recovered</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-400 mt-2">
            ₹{summary.revenue_recovered?.toLocaleString("en-IN")}
          </div>
        </div>
      </div>

      {/* AI Learning Loop Highlight */}
      <div className="rounded-2xl bg-gradient-to-r from-indigo-950/80 via-slate-900 to-indigo-950/60 p-6 border border-indigo-500/30 shadow-xl">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">
          <Cpu className="h-4 w-4" />
          <span>Continuous Agentic Learning Loop</span>
        </div>
        <h2 className="text-xl font-bold text-white">AI Strategy Performance Insight</h2>
        <p className="text-sm text-indigo-200 mt-2 leading-relaxed max-w-3xl">
          "{data.learning_loop_insight}"
        </p>
      </div>

      {/* Strategy Performance Table */}
      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden shadow-xl p-6">
        <h3 className="font-bold text-white text-base mb-4 flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-emerald-400" />
          <span>Recovery Strategy Efficiency Breakdown</span>
        </h3>

        <div className="space-y-4">
          {strategies.map((st: any) => (
            <div key={st.code} className="rounded-xl bg-slate-950/60 p-4 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-base text-white">{st.strategy}</span>
                  <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold px-2 py-0.5 rounded">
                    {st.efficiency_multiplier}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {st.successful} successful out of {st.attempts} attempts
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div>
                  <div className="text-xs text-slate-400">Conversion Rate</div>
                  <div className="text-lg font-extrabold text-blue-400">{st.recovery_rate_pct}%</div>
                </div>

                <div className="border-l border-slate-800 pl-6">
                  <div className="text-xs text-slate-400">Revenue Saved</div>
                  <div className="text-lg font-extrabold text-emerald-400">₹{st.revenue_recovered?.toLocaleString("en-IN")}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Feature 3: Enterprise Merchant SLA Breach & Churn Predictor */}
      <div className="rounded-2xl bg-[#0d1322] border border-[#1e2a42] p-6 shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1e2a42] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 uppercase tracking-wider">
                ENTERPRISE CHURN PREDICTOR
              </span>
              <span className="text-xs text-slate-400">SLA Guarantee: {slaPerf.sla_target_pct}%</span>
            </div>
            <h2 className="text-lg font-bold text-white mt-1">Enterprise Merchant SLA Compliance & Churn Risk</h2>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] text-slate-400 font-medium">Uptime vs Target</div>
              <div className={`text-base font-extrabold ${slaPerf.sla_breached ? 'text-red-400' : 'text-emerald-400'}`}>
                {slaPerf.actual_uptime_pct}% <span className="text-xs text-slate-400 font-normal">/ {slaPerf.sla_target_pct}%</span>
              </div>
            </div>
            <div className="border-l border-[#1e2a42] pl-3 text-right">
              <div className="text-[10px] text-slate-400 font-medium">Churn Probability</div>
              <div className="text-base font-extrabold text-amber-400">{churnRisk.churn_risk_score_pct}% ({churnRisk.risk_level})</div>
            </div>
          </div>
        </div>

        {/* Enterprise Accounts at Risk Table */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">High-Value Enterprise Merchant Accounts at Churn Risk</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {accountsAtRisk.map((acc: any, i: number) => (
              <div key={i} className="rounded-xl bg-[#070b14] p-4 border border-[#172033] space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-white text-sm">{acc.merchant_name}</div>
                  <span className="text-[10px] font-bold text-red-300 bg-red-500/20 px-2 py-0.5 rounded border border-red-500/30">
                    {acc.churn_probability} Churn Probability
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs text-slate-400 pt-1 border-t border-[#172033]">
                  <div>
                    <span>Monthly GMV:</span>
                    <div className="font-bold text-slate-200">{acc.monthly_gmv}</div>
                  </div>
                  <div>
                    <span>Uptime:</span>
                    <div className="font-bold text-red-400">{acc.actual_uptime}</div>
                  </div>
                  <div>
                    <span>24h Exposure:</span>
                    <div className="font-bold text-amber-400">{acc.financial_exposure_24h}</div>
                  </div>
                </div>
                <div className="text-[11px] text-slate-400 pt-1 italic">
                  Primary Issue: "{acc.primary_complaint}"
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Proactive KAM Actions */}
        <div className="pt-2">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Proactive Key Account Manager (KAM) Retention Actions</h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {kamActions.map((act: any, idx: number) => (
              <div key={idx} className="rounded-lg bg-[#121b2d] p-3 border border-[#1e2a42] space-y-1 text-xs">
                <div className="font-bold text-blue-300">{act.title}</div>
                <div className="text-[11px] text-emerald-400 font-semibold">{act.impact}</div>
                <p className="text-[11px] text-slate-400">{act.action}</p>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
