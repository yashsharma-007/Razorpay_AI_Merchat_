"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, ShieldAlert, Cpu, ArrowRight, DollarSign, Activity, FileText, Check, Bot } from "lucide-react";
import { api } from "@/lib/api";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState(false);
  const [applying, setApplying] = useState(false);
  const [notifying, setNotifying] = useState(false);
  const [showAgentLogs, setShowAgentLogs] = useState(false);

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await api.getIncidents();
      setIncidents(data);
      if (data.length > 0) {
        // Fetch detail for first incident
        const detail = await api.getIncidentDetail(data[0].id);
        setSelectedIncident(detail);
      }
    } catch (err) {
      console.error("Error loading incidents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIncidents();
  }, []);

  const handleResolve = async (id: string) => {
    setResolving(true);
    try {
      await api.resolveIncident(id);
      await loadIncidents();
    } catch (err) {
      console.error("Error resolving incident:", err);
    } finally {
      setResolving(false);
    }
  };

  const handleApplyRecovery = async (id: string) => {
    setApplying(true);
    try {
      await api.applyRecovery(id);
      const detail = await api.getIncidentDetail(id);
      setSelectedIncident(detail);
    } catch (err) {
      console.error("Error applying recovery:", err);
    } finally {
      setApplying(false);
    }
  };

  const handleNotifyCustomers = async (id: string) => {
    setNotifying(true);
    try {
      await api.notifyCustomers(id);
      const detail = await api.getIncidentDetail(id);
      setSelectedIncident(detail);
    } catch (err) {
      console.error("Error notifying customers:", err);
    } finally {
      setNotifying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex items-center gap-3">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"></div>
          <span>Loading Payment Incidents...</span>
        </div>
      </div>
    );
  }

  if (!selectedIncident || incidents.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-12 text-center space-y-4 shadow-xs">
        <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-600" />
        <h2 className="text-xl font-bold text-slate-900">No Active Payment Incidents</h2>
        <p className="text-sm text-slate-500 max-w-md mx-auto font-medium">
          All payment gateways and customer feedback telemetry are fully operational. Use <strong>"Simulate Gateway Outage"</strong> in the top sandbox bar to trigger an incident.
        </p>
      </div>
    );
  }

  const inc = selectedIncident.incident;
  const timeline = selectedIncident.timeline || [];
  const isResolved = inc.status === "resolved";

  return (
    <div className="space-y-6">
      
      {/* Page Title & Resolution Action Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Payment Reliability Incidents</h1>
          <p className="text-xs sm:text-sm text-slate-500 font-medium">
            Real-time payment gateway incident tracking, evidence correlation, and automated mitigation
          </p>
        </div>
        
        <div className="flex flex-wrap items-center gap-2">
          {/* Agent Execution Logs Button */}
          <button
            onClick={() => setShowAgentLogs(!showAgentLogs)}
            className={`flex items-center gap-2 rounded-lg border px-3.5 py-2 text-xs font-semibold transition-colors cursor-pointer shadow-xs ${
              showAgentLogs
                ? "bg-blue-50 border-blue-300 text-blue-800 font-bold"
                : "bg-white border-slate-300 text-slate-700 hover:bg-slate-50"
            }`}
          >
            <Activity className="h-4 w-4 text-blue-600" />
            <span>{showAgentLogs ? "Hide Agent Trace Logs" : "View Agent Execution History"}</span>
          </button>

          {!isResolved && (
            <>
              <button
                onClick={() => handleApplyRecovery(inc.id)}
                disabled={applying}
                className="flex items-center gap-2 rounded-lg bg-[#0c66e4] hover:bg-[#0052cc] px-4 py-2 text-xs font-semibold text-white shadow-xs transition-colors cursor-pointer"
              >
                <Bot className="h-4 w-4" />
                <span>{applying ? "Applying..." : "Auto-Reroute (UPI → Card)"}</span>
              </button>

              <button
                onClick={() => handleNotifyCustomers(inc.id)}
                disabled={notifying}
                className="flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 px-4 py-2 text-xs font-semibold text-white shadow-xs transition-colors cursor-pointer"
              >
                <FileText className="h-4 w-4" />
                <span>{notifying ? "Sending..." : "Notify Buyers"}</span>
              </button>

              <button
                onClick={() => handleResolve(inc.id)}
                disabled={resolving}
                className="flex items-center gap-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 px-4 py-2 text-xs font-semibold text-white shadow-xs transition-colors cursor-pointer"
              >
                <Check className="h-4 w-4" />
                <span>{resolving ? "Resolving..." : "Resolve Incident"}</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main Incident Card Header */}
      <div className={`rounded-xl border p-6 shadow-xs bg-white ${isResolved ? 'border-emerald-200' : 'border-rose-200'}`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${isResolved ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-rose-100 text-rose-800 border border-rose-200'}`}>
                {isResolved ? "RESOLVED" : "CRITICAL INCIDENT"} #{inc.id?.slice(-4)}
              </span>
              <span className="text-xs font-medium text-slate-500">
                Started at {new Date(inc.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                MTTD: {inc.mttd_seconds ? `${Math.floor(inc.mttd_seconds/60)}m ${inc.mttd_seconds%60}s` : '2m 41s'}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mt-2">{inc.title}</h2>
            <p className="text-sm text-slate-600 mt-1">{inc.ai_summary}</p>
          </div>

          <div className="flex items-center gap-6 bg-slate-50 p-4 rounded-xl border border-slate-200 shrink-0">
            <div>
              <div className="text-xs text-slate-500 font-bold uppercase tracking-wider">Revenue At Risk</div>
              <div className="text-2xl font-extrabold text-amber-700">₹{inc.revenue_at_risk?.toLocaleString("en-IN")}</div>
            </div>
            <div className="border-l border-slate-200 pl-6">
              <div className="text-xs text-slate-500 font-bold uppercase tracking-wider">2-Hour Forecast</div>
              <div className="text-xl font-extrabold text-rose-600">₹{inc.projected_revenue_impact?.toLocaleString("en-IN")}</div>
            </div>
          </div>
        </div>

        {/* 3 Grid Columns: Evidence, Business Impact, AI Reasoning */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          
          {/* Column 1: Evidence Correlation */}
          <div className="rounded-xl bg-slate-50 p-5 border border-slate-200 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
              <FileText className="h-4 w-4 text-blue-600" />
              <span>Evidence Correlation</span>
            </div>

            <ul className="space-y-2.5 text-xs text-slate-700">
              <li className="flex items-start gap-2 bg-white p-3 rounded-lg border border-slate-200 shadow-xs">
                <span className="text-blue-600 font-bold">•</span>
                <span><strong>27 customer complaints</strong> in last 15 mins (13 specifically report UPI failures)</span>
              </li>
              <li className="flex items-start gap-2 bg-white p-3 rounded-lg border border-slate-200 shadow-xs">
                <span className="text-rose-600 font-bold">•</span>
                <span>UPI failure rate spiked <strong>2.85x</strong> (4.8% → 13.7%)</span>
              </li>
              <li className="flex items-start gap-2 bg-white p-3 rounded-lg border border-slate-200 shadow-xs">
                <span className="text-amber-600 font-bold">•</span>
                <span>Checkout conversion dropped <strong>8.4%</strong> (74.1% → 65.7%)</span>
              </li>
            </ul>
          </div>

          {/* Column 2: Business Impact Breakdown */}
          <div className="rounded-xl bg-slate-50 p-5 border border-slate-200 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
              <DollarSign className="h-4 w-4 text-emerald-600" />
              <span>Business Impact Analysis</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-200 text-slate-700">
                <span>Affected Transactions:</span>
                <span className="font-bold text-slate-900">{inc.affected_transactions_count || 42} checkouts</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-200 text-slate-700">
                <span>Average Order Value:</span>
                <span className="font-bold text-slate-900">₹4,400</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-200 text-slate-700">
                <span>Potential Loss:</span>
                <span className="font-bold text-amber-700">₹1,84,800</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-200 text-slate-700">
                <span>Estimated Recoverability:</span>
                <span className="font-bold text-emerald-700">60%</span>
              </div>
              <div className="flex justify-between py-2 text-slate-900 font-bold">
                <span>Revenue at Risk:</span>
                <span className="text-amber-700 text-sm font-extrabold">₹{inc.revenue_at_risk?.toLocaleString("en-IN")}</span>
              </div>
            </div>
          </div>

          {/* Column 3: AI Action Explanation */}
          <div className="rounded-xl bg-blue-50/70 p-5 border border-blue-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-blue-900 uppercase tracking-wider">
                <Cpu className="h-4 w-4 text-blue-700" />
                <span>AI Action & Strategy</span>
              </div>
              <span className="text-[10px] font-semibold bg-blue-100 text-blue-800 px-2 py-0.5 rounded border border-blue-300">
                Confidence 93%
              </span>
            </div>

            <div className="space-y-2.5 text-xs">
              <div>
                <span className="font-bold text-slate-700">Root Cause Diagnosis:</span>
                <p className="text-slate-900 font-medium mt-0.5">{inc.root_cause}</p>
              </div>
              <div className="pt-2 border-t border-blue-200">
                <span className="font-bold text-slate-700">Recommended Action:</span>
                <p className="text-emerald-800 font-bold mt-0.5">{inc.recommended_action}</p>
              </div>
              <div className="pt-2 border-t border-blue-200 flex items-center justify-between">
                <span className="text-slate-700 font-bold">Status:</span>
                <span className={`font-bold flex items-center gap-1.5 ${isResolved ? 'text-emerald-700' : 'text-amber-800'}`}>
                  {isResolved ? (
                    <span>Resolved</span>
                  ) : (
                    <>
                      <Bot className="h-3.5 w-3.5 text-amber-700" />
                      <span>Recovery Agent Active</span>
                    </>
                  )}
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Multi-Agent Event Stream Timeline (Collapsible / On-Demand Log View) */}
      {showAgentLogs && (
        <div className="rounded-xl bg-white p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-600" />
              <h3 className="font-bold text-slate-900 text-base">Multi-Agent Execution Trace Logs</h3>
              <span className="text-[10px] font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">{timeline.length} agent steps logged</span>
            </div>
            <button
              onClick={() => setShowAgentLogs(false)}
              className="text-xs text-slate-500 hover:text-slate-800 font-bold px-2 py-1 rounded bg-slate-100 border border-slate-200 transition-colors"
            >
              Close Logs
            </button>
          </div>

          <div className="relative border-l-2 border-slate-200 ml-3 space-y-5 pl-6 pt-1">
            {timeline.map((evt: any, idx: number) => (
              <div key={evt.id || idx} className="relative">
                <div className="absolute -left-[31px] top-1.5 h-3.5 w-3.5 rounded-full bg-blue-600 border-2 border-white"></div>
                
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-blue-800 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200 flex items-center gap-1">
                    <Bot className="h-3 w-3 text-blue-600" />
                    <span>{evt.agent_name}</span>
                  </span>
                  <span className="text-xs text-slate-500 font-mono">
                    {new Date(evt.created_at).toLocaleTimeString()}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-slate-900 mt-1">{evt.output_summary}</h4>
                <p className="text-xs text-slate-600 mt-0.5">{evt.input_summary}</p>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
