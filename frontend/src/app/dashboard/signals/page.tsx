"use client";

import { useEffect, useState } from "react";
import { MessageSquare, RefreshCw, Star, Cpu, CheckCircle2, AlertCircle, RotateCcw } from "lucide-react";
import { api } from "@/lib/api";

export default function SignalsPage() {
  const [summary, setSummary] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [appId, setAppId] = useState("com.paytm.business");
  const [toast, setToast] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, revRes] = await Promise.all([
        api.getLowRatingSummary(),
        api.getLowRatingReviews()
      ]);
      setSummary(sumRes);
      setReviews(revRes);
    } catch (err) {
      console.error("Error loading signals data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFetchLive = async () => {
    setScraping(true);
    setToast(null);
    try {
      const res = await api.fetchLiveReviews(appId, 30);
      setToast(`Scraped ${res.scraped_summary?.new_reviews_count || 25} new reviews from Google Play Store (${appId})`);
      await loadData();
    } catch (err: any) {
      setToast(`Error scraping Play Store: ${err.message}`);
    } finally {
      setScraping(false);
    }
  };

  const handleResetReviews = async () => {
    setResetting(true);
    setToast(null);
    try {
      await api.resetReviews();
      setToast("Customer reviews reset successfully.");
      await loadData();
    } catch (err: any) {
      setToast(`Error resetting reviews: ${err.message}`);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Play Store Customer Signals (&lt; 4 Stars)</h1>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">
            Real-time payment gateway friction feedback filtered for merchant action
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={appId}
            onChange={(e) => setAppId(e.target.value)}
            className="bg-white px-3 py-1.5 rounded-lg text-xs font-mono text-slate-800 border border-slate-300 focus:outline-none w-44 shadow-xs"
          />
          <button
            onClick={handleFetchLive}
            disabled={scraping || resetting}
            className="flex items-center gap-1.5 rounded-lg bg-[#0c66e4] hover:bg-[#0052cc] px-4 py-2 text-xs font-semibold text-white transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${scraping ? 'animate-spin' : ''}`} />
            <span>{scraping ? "Scraping..." : "Scrape Play Store"}</span>
          </button>

          <button
            onClick={handleResetReviews}
            disabled={resetting || scraping}
            className="flex items-center gap-1.5 rounded-lg bg-white hover:bg-slate-100 px-3.5 py-2 text-xs font-semibold text-slate-700 border border-slate-300 transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
          >
            <RotateCcw className={`h-3.5 w-3.5 text-slate-500 ${resetting ? 'animate-spin' : ''}`} />
            <span>{resetting ? "Resetting..." : "Reset Reviews"}</span>
          </button>
        </div>
      </div>

      {toast && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-3 text-xs text-blue-800 flex items-center gap-2 font-medium shadow-xs">
          <CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* AI Summary Box */}
      {summary && (
        <div className="rounded-xl bg-white p-5 border border-slate-200 space-y-3 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
              <Cpu className="h-4 w-4 text-blue-600" />
              <span>AI Review Intelligence Digest</span>
            </div>
            <span className="text-xs text-slate-500 font-semibold">{summary.total_low_rating_count} Reviews Analyzed</span>
          </div>

          <p className="text-xs text-slate-700 leading-relaxed font-medium">
            "{summary.executive_summary}"
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
            <div className="rounded-lg bg-slate-50 p-3.5 border border-slate-200 space-y-1.5">
              <div className="font-bold text-rose-700 uppercase text-[10px] tracking-wider">Top Recurring Issues</div>
              <ul className="space-y-1 text-slate-700">
                {summary.top_recurring_pain_points?.map((pt: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-rose-600 font-bold">•</span>
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-lg bg-slate-50 p-3.5 border border-slate-200 space-y-1.5">
              <div className="font-bold text-emerald-700 uppercase text-[10px] tracking-wider">Recommended Merchant Fixes</div>
              <ul className="space-y-1 text-slate-700">
                {summary.recommended_merchant_actions?.map((act: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-emerald-600 font-bold">•</span>
                    <span>{act}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Clean Reviews List Stream */}
      <div className="space-y-2.5">
        {loading ? (
          <div className="py-12 text-center text-slate-500 text-xs">Loading Play Store customer reviews...</div>
        ) : reviews.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs">No reviews rated &lt; 4 stars. Click Scrape Play Store above!</div>
        ) : (
          reviews.map((rev: any) => (
            <div key={rev.id} className="rounded-xl bg-white p-4 border border-slate-200 space-y-2 shadow-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="font-bold text-xs text-slate-900">{rev.customer_name}</span>
                  <div className="flex items-center gap-0.5 text-amber-500">
                    {[...Array(rev.rating || 1)].map((_, i) => (
                      <Star key={i} className="h-3 w-3 fill-amber-400 text-amber-400" />
                    ))}
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">{rev.app_version}</span>
                </div>

                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  rev.severity === 'critical' ? 'bg-rose-100 text-rose-800 border border-rose-200' : 'bg-amber-100 text-amber-800 border border-amber-200'
                }`}>
                  {rev.severity}
                </span>
              </div>

              <p className="text-xs text-slate-700 leading-relaxed font-medium">
                "{rev.review_text}"
              </p>

              <div className="flex items-center justify-between pt-2 text-[10px] text-slate-500 border-t border-slate-100">
                <span>Category: <strong className="text-slate-800">{rev.category}</strong></span>
                <span>{new Date(rev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}
