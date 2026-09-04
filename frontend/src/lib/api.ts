const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }
    return await res.json();
  } catch (err: any) {
    // If backend is briefly restarting, attempt one retry after 300ms
    if (err.name === "TypeError" || err.message?.includes("Failed to fetch")) {
      await new Promise((resolve) => setTimeout(resolve, 350));
      try {
        const retryRes = await fetch(`${API_BASE}${endpoint}`, {
          headers: {
            "Content-Type": "application/json",
            ...(options?.headers || {}),
          },
          ...options,
        });
        if (retryRes.ok) {
          return await retryRes.json();
        }
      } catch (retryErr) {
        console.warn(`Backend connection pending at ${endpoint}:`, retryErr);
      }
    }
    throw new Error(err.message || "Failed to communicate with Merchant Pulse backend server.");
  }
}

export const api = {
  // Dashboard
  getDashboard: () => fetchApi<any>("/dashboard"),
  
  // Incidents
  getIncidents: () => fetchApi<any[]>("/incidents"),
  getIncidentDetail: (id: string) => fetchApi<any>(`/incidents/${id}`),
  resolveIncident: (id: string) => fetchApi<any>(`/incidents/${id}/resolve`, { method: "POST" }),
  applyRecovery: (id: string) => fetchApi<any>(`/incidents/${id}/apply-recovery`, { method: "POST" }),
  notifyCustomers: (id: string) => fetchApi<any>(`/incidents/${id}/notify-customers`, { method: "POST" }),
  
  // Transactions
  getTransactions: () => fetchApi<any[]>("/transactions"),
  
  // Reviews / Signals
  getReviews: (params?: { category?: string; severity?: string; payment_only?: boolean; max_rating?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.append("category", params.category);
    if (params?.severity) searchParams.append("severity", params.severity);
    if (params?.payment_only) searchParams.append("payment_only", "true");
    if (params?.max_rating) searchParams.append("max_rating", params.max_rating.toString());
    const queryStr = searchParams.toString() ? `?${searchParams.toString()}` : "";
    return fetchApi<any[]>(`/reviews${queryStr}`);
  },
  getLowRatingReviews: () => fetchApi<any[]>("/reviews/low-rating"),
  getLowRatingSummary: () => fetchApi<any>("/reviews/summary"),
  getEmailAlerts: () => fetchApi<any[]>("/reviews/email-alerts"),
  triggerTestEmailAlert: (reviewText?: string, rating: number = 1) =>
    fetchApi<any>("/reviews/trigger-email-alert", {
      method: "POST",
      body: JSON.stringify({ review_text: reviewText || "UPI payment failed twice, amount deducted from bank!", rating })
    }),
  fetchLiveReviews: (appId?: string, count: number = 30) => 
    fetchApi<any>(`/reviews/fetch-live?app_id=${encodeURIComponent(appId || "com.razorpay.merchant")}&count=${count}`, { method: "POST" }),
  resetReviews: () => fetchApi<any>("/reviews/reset", { method: "POST" }),

  // Recovery & Refunds
  getRecoveryAnalytics: () => fetchApi<any>("/recovery"),
  getRefunds: () => fetchApi<any[]>("/refunds"),
  autoReconcileRefund: (transactionId?: string) =>
    fetchApi<any>("/refunds/auto-reconcile", { method: "POST", body: JSON.stringify({ transaction_id: transactionId }) }),
  getSlaChurnAnalytics: () => fetchApi<any>("/sla-churn"),

  // Agent Events
  getAgentEvents: () => fetchApi<any[]>("/agent-events"),

  // Checkout
  getProducts: () => fetchApi<any[]>("/checkout/products"),
  processCheckout: (body: {
    order_id: string;
    customer_id: string;
    product_id: string;
    amount: number;
    payment_method: string;
    is_retry?: boolean;
    recovered_via?: string;
  }) => fetchApi<any>("/checkout/process", { method: "POST", body: JSON.stringify(body) }),

  // Settings
  getSettings: () => fetchApi<any>("/settings"),
  updateSettings: (body: any) => fetchApi<any>("/settings", { method: "POST", body: JSON.stringify(body) }),

  // Demo Controls
  simulateIncident: (appId?: string, reviewsCount: number = 25) =>
    fetchApi<any>("/demo/simulate-incident", {
      method: "POST",
      body: JSON.stringify({ app_id: appId || "com.razorpay.merchant", reviews_count: reviewsCount })
    }),
  setPaymentHealth: (method: string, status: string, successRate: number) =>
    fetchApi<any>("/demo/set-health", {
      method: "POST",
      body: JSON.stringify({ method, status, success_rate: successRate })
    }),
  resetDemo: () => fetchApi<any>("/demo/reset", { method: "POST" })
};
