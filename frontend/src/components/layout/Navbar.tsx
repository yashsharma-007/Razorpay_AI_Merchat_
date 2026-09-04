"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  AlertTriangle, 
  CreditCard, 
  MessageSquare, 
  ShoppingBag,
  Building2,
  Settings
} from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { label: "Incidents", href: "/dashboard/incidents", icon: AlertTriangle },
    { label: "Customer Signals", href: "/dashboard/signals", icon: MessageSquare },
    { label: "Transactions", href: "/dashboard/transactions", icon: CreditCard },
    { label: "Settings", href: "/dashboard/settings", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-[#17375e] bg-[#0c2340] shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-2.5">
        
        {/* Brand & Logo */}
        <Link href="/" className="flex items-center gap-3 text-base font-bold text-white hover:opacity-95 transition-opacity">
          <div className="bg-white rounded-md px-2.5 py-1 flex items-center shadow-xs border border-slate-200/20">
            <img src="/logo.jpeg?v=2" alt="Razorpay Logo" className="h-6 sm:h-7 w-auto object-contain" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5 leading-tight">
              <span className="tracking-tight text-sm sm:text-base font-bold text-white">Merchant Pulse</span>
              <span className="bg-[#1d4ed8] text-blue-100 text-[10px] font-extrabold px-1.5 py-0.2 rounded border border-blue-400/30">AI</span>
            </div>
            <span className="text-[10px] text-slate-300 font-medium tracking-wide">Razorpay Revenue Intelligence</span>
          </div>
        </Link>

        {/* Clean Navigation Pills */}
        <nav className="flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 rounded-md px-3.5 py-1.5 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-[#193a63] text-white border border-[#2b588f] font-semibold shadow-xs"
                    : "text-slate-300 hover:bg-[#122e52] hover:text-white"
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? "text-blue-300" : "text-slate-400"}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Right Section: Merchant Account & Sandbox Action */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded bg-[#08182d] border border-[#1d406d] text-[11px] text-slate-200">
            <Building2 className="h-3.5 w-3.5 text-blue-400" />
            <span className="font-medium">Acme Retail Corp</span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-300 font-mono text-[10px]">MID_9842</span>
          </div>

          <Link
            href="/checkout"
            target="_blank"
            className="flex items-center gap-2 rounded-md bg-[#0c66e4] hover:bg-[#0052cc] px-3.5 py-1.5 text-xs font-semibold text-white transition-all shadow-xs"
          >
            <ShoppingBag className="h-3.5 w-3.5 text-white" />
            <span>Buyer Sandbox</span>
          </Link>
        </div>

      </div>
    </header>
  );
}
