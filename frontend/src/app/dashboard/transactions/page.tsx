"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, XCircle, Search, Zap, Code, Send } from "lucide-react";
import { api } from "@/lib/api";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [webhookModalOpen, setWebhookModalOpen] = useState(false);
  const [webhookSending, setWebhookSending] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const [webhookJson, setWebhookJson] = useState(JSON.stringify({
    event: "payment.failed",
    payload: {
      payment: {
        entity: {
          id: `pay_${Math.floor(100000000 + Math.random() * 900000000)}`,
          amount: 499900,
          currency: "INR",
          status: "failed",
          method: "upi",
          email: "customer.live@example.com",
          contact: "+919876543210",
          error_description: "UPI payment gateway timeout error 504"
        }
      }
    }
  }, null, 2));

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const data = await api.getTransactions();
      setTransactions(data);
    } catch (err) {
      console.error("Error loading transactions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, []);

  const handleSendWebhook = async () => {
    setWebhookSending(true);
    setToast(null);
    try {
      const parsedPayload = JSON.parse(webhookJson);
      const res = await fetch("http://localhost:8000/api/webhooks/payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsedPayload)
      });
      const data = await res.json();
      setToast(`Webhook Processed! Ingested Transaction ${data.payment_id} into DB.`);
      setWebhookModalOpen(false);
      await loadTransactions();
    } catch (err: any) {
      setToast(`Error sending webhook: ${err.message}`);
    } finally {
      setWebhookSending(false);
    }
  };

  const [refundReconciling, setRefundReconciling] = useState(false);

  const handleAutoReconcileRefund = async (txnId?: string) => {
    setRefundReconciling(true);
    setToast(null);
    try {
      const res = await api.autoReconcileRefund(txnId);
      setToast(`Instant Refund #${res.refund?.refund_id} processed for ₹${res.refund?.amount?.toLocaleString("en-IN")}! Customer notified via WhatsApp.`);
      await loadTransactions();
    } catch (err: any) {
      setToast(`Error processing auto-refund: ${err.message}`);
    } finally {
      setRefundReconciling(false);
    }
  };

  const filtered = transactions.filter((t: any) =>
    t.external_id?.toLowerCase().includes(search.toLowerCase()) ||
    t.customer_name?.toLowerCase().includes(search.toLowerCase()) ||
    t.payment_method?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Merchant Transactions</h1>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">Real-time payment telemetry & AI recovery status</p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => handleAutoReconcileRefund()}
            disabled={refundReconciling}
            className="flex items-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 px-3.5 py-2 text-xs font-semibold text-white transition-colors cursor-pointer shadow-xs disabled:opacity-50"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>{refundReconciling ? "Reconciling..." : "Auto-Reconcile Instant Refund"}</span>
          </button>

          <button
            onClick={() => setWebhookModalOpen(true)}
            className="flex items-center gap-1.5 rounded-lg bg-[#0c66e4] hover:bg-[#0052cc] px-3.5 py-2 text-xs font-semibold text-white transition-colors cursor-pointer shadow-xs"
          >
            <Zap className="h-3.5 w-3.5 text-amber-300 fill-amber-300" />
            <span>Ingest Webhook</span>
          </button>

          <div className="relative w-full sm:w-48">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search txn..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg bg-white border border-slate-300 pl-8 pr-3 py-1.5 text-xs text-slate-800 focus:border-blue-600 focus:outline-none shadow-xs"
            />
          </div>
        </div>
      </div>

      {toast && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-3 text-xs text-blue-800 flex items-center gap-2 font-medium shadow-xs">
          <CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Clean Transactions Table */}
      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-3.5">Txn ID</th>
                <th className="px-4 py-3.5">Customer</th>
                <th className="px-4 py-3.5">Amount</th>
                <th className="px-4 py-3.5">Method</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Failure Reason</th>
                <th className="px-4 py-3.5">AI Recovery</th>
                <th className="px-4 py-3.5">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-500">Loading transactions...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-500">No transactions found.</td>
                </tr>
              ) : (
                filtered.map((tx: any) => (
                  <tr key={tx.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-slate-900">{tx.external_id}</td>
                    <td className="px-4 py-3 text-slate-800 font-medium">{tx.customer_name}</td>
                    <td className="px-4 py-3 font-bold text-slate-900">₹{tx.amount?.toLocaleString("en-IN")}</td>
                    <td className="px-4 py-3 uppercase font-bold text-slate-600 text-[11px]">{tx.payment_method}</td>
                    <td className="px-4 py-3">
                      {tx.status === "success" ? (
                        <span className="text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-bold text-[10px]">SUCCESS</span>
                      ) : (
                        <span className="text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded font-bold text-[10px]">FAILED</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-[11px]">{tx.failure_reason || "—"}</td>
                    <td className="px-4 py-3">
                      {tx.is_recovered ? (
                        <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold text-[10px] border border-emerald-200">
                          Recovered via {tx.recovery_method}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-500">{new Date(tx.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Webhook Modal */}
      {webhookModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-xl bg-white border border-slate-200 p-5 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <Code className="h-4 w-4 text-blue-600" />
                <span>Razorpay Payment Webhook Ingestion</span>
              </h3>
              <button onClick={() => setWebhookModalOpen(false)} className="text-slate-400 hover:text-slate-700 font-bold text-sm">✕</button>
            </div>
            <textarea
              value={webhookJson}
              onChange={(e) => setWebhookJson(e.target.value)}
              rows={9}
              className="w-full rounded-lg bg-slate-900 font-mono text-xs text-emerald-400 border border-slate-800 p-3 focus:outline-none"
            />
            <div className="flex justify-end gap-2 pt-1">
              <button onClick={() => setWebhookModalOpen(false)} className="px-3.5 py-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium">Cancel</button>
              <button onClick={handleSendWebhook} disabled={webhookSending} className="bg-[#0c66e4] hover:bg-[#0052cc] px-4 py-1.5 text-xs font-semibold text-white rounded-lg transition-colors shadow-xs">
                {webhookSending ? "Sending..." : "Send Webhook"}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
