"use client";

import { useEffect, useState } from "react";
import { Activity, Bot, Cpu, Zap, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";

export default function AIActivityPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const data = await api.getAgentEvents();
      setEvents(data);
    } catch (err) {
      console.error("Error loading agent events:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">CrewAI Agent Activity Feed</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Live multi-agent execution stream across CrewAI roles (Signal, Root Cause, Risk, Recovery)
          </p>
        </div>

        <div className="flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 px-3 py-1.5 rounded-lg text-xs font-semibold text-indigo-300">
          <Bot className="h-4 w-4 text-indigo-400" />
          <span>CrewAI Framework: Active</span>
        </div>
      </div>

      <div className="space-y-3">
        {loading ? (
          <div className="py-12 text-center text-slate-400 text-xs">Loading CrewAI Agent Log Stream...</div>
        ) : events.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            No agent events logged. Click <strong>Simulate UPI Incident</strong> to trigger CrewAI agents!
          </div>
        ) : (
          events.map((evt: any) => (
            <div key={evt.id} className="rounded-xl bg-slate-900/60 p-4 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-xs text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded border border-blue-500/20 flex items-center gap-1.5">
                    <Bot className="h-3.5 w-3.5 text-blue-400" />
                    <span>{evt.agent_name}</span>
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">{evt.event_type}</span>
                </div>
                <span className="text-[10px] text-slate-500">{new Date(evt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>

              <h3 className="text-xs font-semibold text-white">{evt.output_summary}</h3>
              <p className="text-xs text-slate-400">{evt.input_summary}</p>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[10px] text-slate-500">
                <span>Decision: <strong className="text-slate-300">{evt.decision}</strong></span>
                <span>Confidence: {(evt.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}
