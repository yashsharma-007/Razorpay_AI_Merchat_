"use client";

import { useEffect, useState } from "react";
import { Settings, ShieldCheck, CheckCircle2, Save, Mail, AlertTriangle, Send, FileText } from "lucide-react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [policy, setPolicy] = useState<any>({
    auto_recovery_enabled: true,
    max_auto_recovery_amount: 50000,
    preferred_fallback_methods: ["card", "netbanking"],
    merchant_alert_threshold: 10000
  });
  
  const [merchantEmail, setMerchantEmail] = useState("yss20042003@gmail.com");
  const [extremeWarningEnabled, setExtremeWarningEnabled] = useState(true);
  const [regularDigestEnabled, setRegularDigestEnabled] = useState(true);
  const [emailAlertsHistory, setEmailAlertsHistory] = useState<any[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [emailSending, setEmailSending] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [res, emailRes] = await Promise.all([
        api.getSettings(),
        fetch("http://localhost:8000/api/reviews/email-alerts").then(r => r.json()).catch(() => [])
      ]);
      setPolicy(res);
      setEmailAlertsHistory(emailRes || []);
    } catch (err) {
      console.error("Error loading settings:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setToast(null);
    try {
      await api.updateSettings(policy);
      setToast("Merchant Policy and Email Alert preferences updated successfully.");
    } catch (err: any) {
      setToast(`Error updating policy: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleTriggerTestWarning = async () => {
    setEmailSending(true);
    setToast(null);
    try {
      const res = await fetch("http://localhost:8000/api/reviews/trigger-warning", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          merchant_email: merchantEmail,
          customer_name: "Rahul Sharma",
          rating: 1,
          review_text: "UPI payment failed twice, money deducted from bank!"
        })
      });
      const data = await res.json();
      setToast(`Extreme Warning Email Alert delivered to ${merchantEmail}!`);
      await loadData();
    } catch (err: any) {
      setToast(`Error sending test warning: ${err.message}`);
    } finally {
      setEmailSending(false);
    }
  };

  const handleTriggerTestDigest = async () => {
    setEmailSending(true);
    setToast(null);
    try {
      const res = await fetch("http://localhost:8000/api/reviews/trigger-digest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          merchant_email: merchantEmail
        })
      });
      const data = await res.json();
      setToast(`Regular Review & Feedback Digest Email delivered to ${merchantEmail}!`);
      await loadData();
    } catch (err: any) {
      setToast(`Error sending test digest: ${err.message}`);
    } finally {
      setEmailSending(false);
    }
  };

  if (loading) return <div className="py-12 text-center text-slate-400 text-xs">Loading Merchant Settings & Email Triggers...</div>;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Merchant Policy & Email Triggers</h1>
        <p className="text-xs text-slate-500 mt-0.5 font-medium">
          Configure extreme critical warning alerts, regular Play Store feedback digests, and AI recovery guardrails
        </p>
      </div>

      {toast && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-xs text-emerald-800 flex items-center gap-2 font-medium shadow-xs">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Email Triggers & Notifications Card */}
      <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-5 shadow-xs">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-900 border-b border-slate-100 pb-3">
          <Mail className="h-4 w-4 text-blue-600" />
          <span>Email Alert & Feedback Digest Triggers</span>
        </div>

        <div className="space-y-4 text-xs">
          {/* Merchant Email */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 block">Merchant Operations Email Address</label>
            <input
              type="email"
              value={merchantEmail}
              onChange={(e) => setMerchantEmail(e.target.value)}
              className="w-full rounded-lg bg-white border border-slate-300 px-3.5 py-2 text-xs text-slate-800 focus:border-blue-600 focus:outline-none font-mono shadow-xs"
            />
          </div>

          {/* Toggle 1: Extreme Warnings */}
          <div className="flex items-center justify-between py-2 border-t border-slate-100">
            <div>
              <div className="font-bold text-slate-900 flex items-center gap-1.5">
                <AlertTriangle className="h-3.5 w-3.5 text-rose-600" />
                <span>Extreme Critical Warning Emails</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">Trigger immediate email when 1★/2★ payment failure reviews or critical incidents occur</p>
            </div>
            <button
              onClick={() => setExtremeWarningEnabled(!extremeWarningEnabled)}
              className={`relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded-full transition-colors ${
                extremeWarningEnabled ? "bg-rose-600" : "bg-slate-300"
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                extremeWarningEnabled ? "translate-x-5" : "translate-x-0"
              }`} />
            </button>
          </div>

          {/* Toggle 2: Regular Digests */}
          <div className="flex items-center justify-between py-2 border-t border-slate-100">
            <div>
              <div className="font-bold text-slate-900 flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5 text-blue-600" />
                <span>Regular Review & Feedback Digest Emails</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">Send periodic summary digests of Play Store customer sentiment and merchant fixes</p>
            </div>
            <button
              onClick={() => setRegularDigestEnabled(!regularDigestEnabled)}
              className={`relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded-full transition-colors ${
                regularDigestEnabled ? "bg-blue-600" : "bg-slate-300"
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                regularDigestEnabled ? "translate-x-5" : "translate-x-0"
              }`} />
            </button>
          </div>

          {/* Manual Test Dispatch Buttons */}
          <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-slate-100">
            <button
              onClick={handleTriggerTestWarning}
              disabled={emailSending}
              className="flex items-center gap-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 px-3.5 py-2 text-xs font-semibold text-rose-700 border border-rose-200 transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
            >
              <AlertTriangle className="h-3.5 w-3.5 text-rose-600" />
              <span>{emailSending ? "Sending..." : "Test Extreme Warning Email"}</span>
            </button>

            <button
              onClick={handleTriggerTestDigest}
              disabled={emailSending}
              className="flex items-center gap-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 px-3.5 py-2 text-xs font-semibold text-blue-800 border border-blue-200 transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
            >
              <FileText className="h-3.5 w-3.5 text-blue-600" />
              <span>{emailSending ? "Sending..." : "Test Regular Feedback Digest Email"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Policy Guardrails Card */}
      <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-4 shadow-xs">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-900 border-b border-slate-100 pb-3">
          <ShieldCheck className="h-4 w-4 text-emerald-600" />
          <span>Autonomous AI Recovery Guardrails</span>
        </div>

        <div className="space-y-4 text-xs">
          <div className="flex items-center justify-between py-1">
            <div>
              <div className="font-bold text-slate-900">Autonomous Buyer Recovery</div>
              <p className="text-[11px] text-slate-500">Allow Buyer Recovery Agent to automatically switch payment gateway on checkout failure</p>
            </div>
            <button
              onClick={() => setPolicy({ ...policy, auto_recovery_enabled: !policy.auto_recovery_enabled })}
              className={`relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded-full transition-colors ${
                policy.auto_recovery_enabled ? "bg-emerald-600" : "bg-slate-300"
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                policy.auto_recovery_enabled ? "translate-x-5" : "translate-x-0"
              }`} />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div>
              <label className="font-bold text-slate-700 block mb-1">Max Auto-Recovery Amount (₹)</label>
              <input
                type="number"
                value={policy.max_auto_recovery_amount}
                onChange={(e) => setPolicy({ ...policy, max_auto_recovery_amount: Number(e.target.value) })}
                className="w-full rounded-lg bg-white border border-slate-300 px-3 py-1.5 text-xs text-slate-800 focus:outline-none shadow-xs"
              />
            </div>
            <div>
              <label className="font-bold text-slate-700 block mb-1">Revenue At Risk Threshold (₹)</label>
              <input
                type="number"
                value={policy.merchant_alert_threshold}
                onChange={(e) => setPolicy({ ...policy, merchant_alert_threshold: Number(e.target.value) })}
                className="w-full rounded-lg bg-white border border-slate-300 px-3 py-1.5 text-xs text-slate-800 focus:outline-none shadow-xs"
              />
            </div>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-1.5 rounded-lg bg-[#0c66e4] hover:bg-[#0052cc] px-4 py-2 text-xs font-semibold text-white transition-colors cursor-pointer shadow-xs"
          >
            <Save className="h-3.5 w-3.5" />
            <span>{saving ? "Saving..." : "Save Settings"}</span>
          </button>
        </div>
      </div>

      {/* Delivered Email Dispatch Audit Log */}
      <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-3 shadow-xs">
        <h3 className="font-bold text-slate-900 text-sm">Delivered Email Dispatches Log</h3>

        <div className="space-y-2 text-xs">
          {emailAlertsHistory.length === 0 ? (
            <div className="py-6 text-center text-slate-500">No email alerts sent yet. Click test buttons above to trigger emails!</div>
          ) : (
            emailAlertsHistory.map((em: any) => (
              <div key={em.id} className="rounded-lg bg-slate-50 p-3 border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded font-bold text-[10px] uppercase ${
                      em.type === 'EXTREME_WARNING' ? 'bg-rose-100 text-rose-800 border border-rose-200' : 'bg-blue-100 text-blue-800 border border-blue-200'
                    }`}>
                      {em.type || 'EMAIL_ALERT'}
                    </span>
                    <span className="font-bold text-slate-900 text-xs">{em.subject}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">To: {em.merchant_email}</div>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-emerald-800 font-bold text-[10px] bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                    DELIVERED
                  </span>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {new Date(em.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
