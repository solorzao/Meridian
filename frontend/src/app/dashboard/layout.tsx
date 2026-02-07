'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  BookOpen,
  BarChart3,
  Bot,
  Settings,
  User,
  LogOut,
} from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Overview', icon: LayoutDashboard, exact: true },
  { href: '/dashboard/journal', label: 'Journal', icon: BookOpen, exact: false },
  { href: '/dashboard/analytics', label: 'Analytics', icon: BarChart3, exact: false },
  { href: '/dashboard/agents', label: 'AI Agents', icon: Bot, exact: false },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings, exact: false },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const isActive = (href: string, exact: boolean) => {
    if (exact) return pathname === href;
    return pathname.startsWith(href);
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar - dark navy */}
      <aside className="w-64 flex-shrink-0 bg-[#17304e] border-r border-white/5 flex flex-col">
        {/* Logo */}
        <div className="px-4 py-5 flex items-center justify-center">
<Image src="/logo.png" alt="Meridian" width={150} height={82} className="rounded-lg" style={{ boxShadow: '0 0 20px 10px #17304e' }} />
        </div>

        <div className="meridian-divider-dark mx-4" />

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href, item.exact);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`meridian-nav-link ${active ? 'meridian-nav-link-active' : ''}`}
              >
                <Icon className="w-[18px] h-[18px] flex-shrink-0" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="meridian-divider-dark mx-4" />

        {/* User profile section */}
        <div className="px-3 py-4 space-y-1">
          <div className="flex items-center gap-3 px-3 py-2.5">
            <div className="w-8 h-8 rounded-full bg-meridian-navy-50 flex items-center justify-center flex-shrink-0">
              <User className="w-4 h-4 text-meridian-slate-300" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">Trader</p>
              <p className="text-xs text-meridian-slate-400 truncate">Free Plan</p>
            </div>
          </div>
          <button className="meridian-nav-link w-full text-meridian-slate-400 hover:text-meridian-crimson-300">
            <LogOut className="w-[18px] h-[18px] flex-shrink-0" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main content area - light background */}
      <main className="flex-1 overflow-auto bg-meridian-surface">
        {/* Thin decorative top bar with wave accent */}
        <div className="h-1 bg-gradient-to-r from-meridian-navy via-meridian-steel to-meridian-crimson" />

        <div className="p-8 max-w-[1400px]">
          {children}
        </div>
      </main>
    </div>
  );
}
