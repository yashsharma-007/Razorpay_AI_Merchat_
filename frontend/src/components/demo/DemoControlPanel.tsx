"use client";

import { useState } from "react";
import { Play, RotateCcw, AlertTriangle, CheckCircle2, SlidersHorizontal } from "lucide-react";
import { api } from "@/lib/api";

export default function DemoControlPanel({ onUpdate }: { onUpdate?: () => void }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSimulateIncident = async () => {
    setLoading(true);
    setMessage(null);
    setIsSuccess(false);
    try {
      const res = await api.simulateIncident("com.paytm.business", 25);
      setMessage(`Incident Triggered: Created Incident #${res.incident_id?.slice(-4)} (₹${(res.revenue_at_risk || 184800).toLocaleString("en-IN")} at risk)`);
      if (onUpdate) onUpdate();
    } catch (err: any) {
      setMessage(`Error: ${err.message || "Failed to trigger incident"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleResetDemo = async () => {
    setLoading(true);
    setMessage(null);
    setIsSuccess(true);
    try {
      await api.resetDemo();
      setMessage("Telemetry restored to baseline metrics.");
      if (onUpdate) onUpdate();
    } catch (err: any) {
      setMessage(`Error: ${err.message || "Failed to reset demo"}`);
      setIsSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full bg-slate-50 border-b border-slate-200 px-6 py-2.5">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 text-xs">
        
        {/* Left Indicator */}
        <div className="flex items-center gap-3 font-medium text-slate-700">
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-200 text-[11px] font-semibold">
            <SlidersHorizontal className="h-3 w-3 text-blue-700" />
            <span>Sandbox Mode</span>
          </div>
          
          <span className="text-slate-300 hidden sm:inline">•</span>
          
          {message ? (
            <div className="flex items-center gap-1.5 font-semibold">
              {isSuccess ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-amber-600" />
              )}
              <span className={isSuccess ? "text-emerald-800" : "text-amber-800"}>{message}</span>
            </div>
          ) : (
            <span className="text-slate-600 font-medium">Simulate payment gateway degradation & trigger autonomous AI recovery</span>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleSimulateIncident}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-md bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-1.5 text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            <Play className="h-3 w-3 fill-white text-white" />
            <span>{loading ? "Simulating..." : "Simulate Gateway Outage"}</span>
          </button>

          <button
            onClick={handleResetDemo}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-md bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 px-3.5 py-1.5 text-xs font-medium transition-colors cursor-pointer shadow-xs disabled:opacity-50"
          >
            <RotateCcw className="h-3 w-3 text-slate-500" />
            <span>Reset Telemetry</span>
          </button>
        </div>

      </div>
    </div>
  );
}
