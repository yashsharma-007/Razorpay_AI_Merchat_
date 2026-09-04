"use client";

import Navbar from "@/components/layout/Navbar";
import DemoControlPanel from "@/components/demo/DemoControlPanel";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white text-slate-900 flex flex-col font-sans">
      <Navbar />
      <DemoControlPanel />
      <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-6 sm:px-6">
        {children}
      </main>
    </div>
  );
}
