"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  ShoppingBag, 
  CreditCard, 
  Smartphone, 
  Building, 
  Wallet, 
  Bot, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight,
  ShieldCheck,
  RefreshCw
} from "lucide-react";
import { api } from "@/lib/api";

export default function CheckoutPage() {
  const [product, setProduct] = useState<any>({
    id: "p_headphones",
    name: "Premium Wireless Headphones",
    description: "Active Noise-Cancelling Headphones with 40-hour battery life and spatial audio",
    price: 4999.0,
    image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80"
  });

  const [selectedMethod, setSelectedMethod] = useState("upi");
  const [processing, setProcessing] = useState(false);
  const [paymentResult, setPaymentResult] = useState<any>(null);
  const [recoveryModal, setRecoveryModal] = useState<any>(null);
  const [recoveredSuccess, setRecoveredSuccess] = useState<any>(null);

  const handlePay = async (methodOverride?: string, isRetry: boolean = false) => {
    setProcessing(true);
    setPaymentResult(null);
    setRecoveredSuccess(null);

    const methodToUse = methodOverride || selectedMethod;

    try {
      const res = await api.processCheckout({
        order_id: `ord_${Math.floor(100000 + Math.random() * 900000)}`,
        customer_id: "c_102",
        product_id: product.id,
        amount: product.price,
        payment_method: methodToUse,
        is_retry: isRetry,
        recovered_via: isRetry ? methodToUse : undefined
      });

      setPaymentResult(res);

      if (res.status === "failed" && res.recovery_recommendation) {
        setRecoveryModal(res.recovery_recommendation);
      } else if (res.status === "success" && isRetry) {
        setRecoveryModal(null);
        setRecoveredSuccess(res);
      }
    } catch (err: any) {
      console.error("Checkout error:", err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 selection:bg-blue-500 selection:text-white flex flex-col font-sans">
      
      {/* Checkout Navbar */}
      <header className="border-b border-slate-800 bg-slate-950/80 px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingBag className="h-6 w-6 text-emerald-400" />
            <span className="text-xl font-bold text-white">Apex Retail Store</span>
            <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">Checkout Sandbox</span>
          </div>

          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 bg-blue-500/10 px-3 py-1.5 rounded-lg border border-blue-500/20"
          >
            <span>Back to Merchant Dashboard</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </header>

      {/* Main Checkout Area */}
      <div className="flex-1 mx-auto w-full max-w-5xl px-4 py-8 sm:px-6">
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          
          {/* Product Summary Column */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <h2 className="text-lg font-bold text-white">Order Summary</h2>

            <div className="flex gap-4 items-center p-3 rounded-xl bg-slate-900 border border-slate-800">
              <img
                src={product.image_url}
                alt={product.name}
                className="h-20 w-20 object-cover rounded-lg border border-slate-700"
              />
              <div>
                <h3 className="font-bold text-white text-base">{product.name}</h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">{product.description}</p>
                <div className="mt-2 text-lg font-extrabold text-emerald-400">₹{product.price?.toLocaleString("en-IN")}</div>
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-800 text-xs text-slate-300">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>₹{product.price?.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between">
                <span>Shipping:</span>
                <span className="text-emerald-400 font-semibold">FREE</span>
              </div>
              <div className="flex justify-between text-sm font-extrabold text-white pt-2 border-t border-slate-800">
                <span>Total Amount Due:</span>
                <span className="text-emerald-400">₹{product.price?.toLocaleString("en-IN")}</span>
              </div>
            </div>
          </div>

          {/* Payment Method & Action Column */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
            <div>
              <h2 className="text-lg font-bold text-white">Select Payment Method</h2>
              <p className="text-xs text-slate-400 mt-0.5">Simulate payment attempt to test AI Recovery Agent</p>
            </div>

            <div className="space-y-3">
              
              {/* Option 1: UPI */}
              <label
                onClick={() => setSelectedMethod("upi")}
                className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedMethod === "upi"
                    ? "bg-blue-600/15 border-blue-500 text-white"
                    : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Smartphone className="h-5 w-5 text-blue-400" />
                  <div>
                    <div className="font-bold text-sm">UPI (GPay / PhonePe / Paytm)</div>
                    <div className="text-[10px] text-slate-400">Instant UPI transfer</div>
                  </div>
                </div>
                <input type="radio" name="pay_method" checked={selectedMethod === "upi"} onChange={() => {}} className="h-4 w-4 accent-blue-500" />
              </label>

              {/* Option 2: Card */}
              <label
                onClick={() => setSelectedMethod("card")}
                className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedMethod === "card"
                    ? "bg-blue-600/15 border-blue-500 text-white"
                    : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  <CreditCard className="h-5 w-5 text-emerald-400" />
                  <div>
                    <div className="font-bold text-sm">Credit / Debit Card</div>
                    <div className="text-[10px] text-slate-400">Visa, Mastercard, RuPay</div>
                  </div>
                </div>
                <input type="radio" name="pay_method" checked={selectedMethod === "card"} onChange={() => {}} className="h-4 w-4 accent-blue-500" />
              </label>

              {/* Option 3: Net Banking */}
              <label
                onClick={() => setSelectedMethod("netbanking")}
                className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedMethod === "netbanking"
                    ? "bg-blue-600/15 border-blue-500 text-white"
                    : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Building className="h-5 w-5 text-amber-400" />
                  <div>
                    <div className="font-bold text-sm">Net Banking</div>
                    <div className="text-[10px] text-slate-400">HDFC, SBI, ICICI, Axis</div>
                  </div>
                </div>
                <input type="radio" name="pay_method" checked={selectedMethod === "netbanking"} onChange={() => {}} className="h-4 w-4 accent-blue-500" />
              </label>

            </div>

            {/* Pay Button */}
            <button
              onClick={() => handlePay(selectedMethod, false)}
              disabled={processing}
              className="w-full rounded-xl bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-500 hover:to-blue-500 py-3.5 text-base font-extrabold text-white shadow-xl shadow-blue-600/25 transition-all active:scale-95 cursor-pointer disabled:opacity-50"
            >
              {processing ? "Processing Payment Gateway..." : `Pay ₹${product.price?.toLocaleString("en-IN")} via ${selectedMethod.toUpperCase()}`}
            </button>

            {/* Success Message Banner */}
            {(paymentResult?.status === "success" || recoveredSuccess) && (
              <div className="rounded-xl bg-emerald-500/20 border border-emerald-500/40 p-4 text-center space-y-2">
                <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-400" />
                <h3 className="text-base font-bold text-white">Payment Successful!</h3>
                <p className="text-xs text-emerald-200">
                  Transaction {paymentResult?.transaction_id} completed successfully via {paymentResult?.payment_method?.toUpperCase()}.
                </p>
                {recoveredSuccess && (
                  <div className="mt-2 text-xs font-semibold text-emerald-300 bg-[#0c1a2e] p-2 rounded border border-emerald-500/30 flex items-center justify-center gap-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Transaction recovered by Autonomous Recovery Agent. ₹4,999 credited to merchant ledger.</span>
                  </div>
                )}
              </div>
            )}

          </div>

        </div>

      </div>

      {/* Autonomous Recovery Agent Modal Overlay */}
      {recoveryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-xl bg-[#0d1322] p-6 border border-[#1e2a42] shadow-2xl space-y-5">
            
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20 uppercase tracking-wider">
                      AUTONOMOUS RECOVERY AGENT
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-0.5">UPI Gateway Latency Detected</h3>
                </div>
              </div>
            </div>

            {/* AI Reasoning & Message */}
            <div className="rounded-lg bg-[#131b2e] p-4 border border-[#1e2a42] text-xs text-slate-200 space-y-2">
              <p className="font-semibold text-xs text-slate-100 line-clamp-2">
                "{recoveryModal.customer_message}"
              </p>
              <div className="pt-2 border-t border-[#1e2a42] text-[11px] text-slate-400">
                Diagnosis: {recoveryModal.reasoning_summary}
              </div>
            </div>

            {/* Recovery Action Options */}
            <div className="space-y-2">
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Recommended Resolution Rail:</div>

              {/* Recommended Option: Try Card */}
              <button
                onClick={() => handlePay("card", true)}
                disabled={processing}
                className="w-full flex items-center justify-between p-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md transition-all active:scale-95 cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4" />
                  <span>Switch to Credit/Debit Card (Recommended)</span>
                </div>
                <ArrowRight className="h-4 w-4" />
              </button>

              {/* Alternative 2: Net Banking */}
              <button
                onClick={() => handlePay("netbanking", true)}
                disabled={processing}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <Building className="h-4 w-4 text-amber-400" />
                  <span>Try Net Banking</span>
                </div>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>

              {/* Alternative 3: Retry UPI */}
              <button
                onClick={() => handlePay("upi", true)}
                disabled={processing}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 text-xs font-medium border border-slate-800 transition-all cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <RefreshCw className="h-3.5 w-3.5" />
                  <span>Retry UPI (High failure rate right now)</span>
                </div>
              </button>
            </div>

            <div className="text-center pt-2">
              <button
                onClick={() => setRecoveryModal(null)}
                className="text-xs text-slate-500 hover:text-slate-400 font-medium cursor-pointer"
              >
                Dismiss & Cancel Order
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
