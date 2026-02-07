import {
  TrendingUp,
  TrendingDown,
  Target,
  Scale,
  Plus,
  MessageSquare,
  BookOpen,
  ArrowRight,
  FileBarChart,
  Compass,
} from 'lucide-react';
import Link from 'next/link';

const stats = [
  {
    label: 'Open Trades',
    value: '--',
    change: null,
    icon: Target,
    accentColor: 'bg-meridian-steel',
    iconBg: 'bg-meridian-steel/10',
    iconColor: 'text-meridian-steel',
  },
  {
    label: 'Total P&L',
    value: '--',
    change: null,
    icon: TrendingUp,
    accentColor: 'bg-emerald-500',
    iconBg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-600',
  },
  {
    label: 'Win Rate',
    value: '--',
    change: null,
    icon: TrendingDown,
    accentColor: 'bg-meridian-crimson',
    iconBg: 'bg-meridian-crimson/10',
    iconColor: 'text-meridian-crimson',
  },
  {
    label: 'Profit Factor',
    value: '--',
    change: null,
    icon: Scale,
    accentColor: 'bg-amber-500',
    iconBg: 'bg-amber-500/10',
    iconColor: 'text-amber-600',
  },
];

const quickActions = [
  {
    label: 'Log a Trade',
    description: 'Record a new trade entry',
    href: '/dashboard/journal',
    icon: Plus,
    accent: 'bg-meridian-crimson/10 text-meridian-crimson',
  },
  {
    label: 'Chat with Agent',
    description: 'Get AI-powered insights',
    href: '/dashboard/agents',
    icon: MessageSquare,
    accent: 'bg-meridian-steel/10 text-meridian-steel',
  },
  {
    label: 'View Analytics',
    description: 'Check your performance',
    href: '/dashboard/analytics',
    icon: FileBarChart,
    accent: 'bg-emerald-500/10 text-emerald-600',
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="text-2xl font-bold text-meridian-text-heading mb-1">Good evening, Trader</h1>
        <p className="text-meridian-text-muted text-sm">
          Here is your trading overview. Start by logging your first trade.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="meridian-card relative overflow-hidden p-5"
            >
              <div className={`meridian-stat-accent ${stat.accentColor}`} />
              <div className="flex items-start justify-between">
                <div className="pl-3">
                  <p className="text-xs font-medium text-meridian-text-muted uppercase tracking-wider">
                    {stat.label}
                  </p>
                  <p className="text-2xl font-bold text-meridian-text-heading mt-1">{stat.value}</p>
                </div>
                <div className={`w-9 h-9 rounded-lg ${stat.iconBg} flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 ${stat.iconColor}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-sm font-semibold text-meridian-text-muted uppercase tracking-wider mb-3">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.label}
                href={action.href}
                className="meridian-card-hover p-5 group"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${action.accent}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm text-meridian-text-heading group-hover:text-meridian-navy transition-colors">
                      {action.label}
                    </p>
                    <p className="text-xs text-meridian-text-muted">{action.description}</p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-meridian-text-light group-hover:text-meridian-text-muted transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Trades */}
        <div className="meridian-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold text-meridian-text-heading">Recent Trades</h2>
            <Link
              href="/dashboard/journal"
              className="text-xs text-meridian-steel hover:text-meridian-steel-600 transition-colors font-medium"
            >
              View All
            </Link>
          </div>
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <div className="w-14 h-14 rounded-2xl bg-meridian-surface-200 flex items-center justify-center mb-4">
              <BookOpen className="w-6 h-6 text-meridian-text-light" />
            </div>
            <p className="text-sm font-medium text-meridian-text-body mb-1">No trades yet</p>
            <p className="text-xs text-meridian-text-muted mb-5 max-w-[220px]">
              Start building your trading journal by logging your first trade.
            </p>
            <Link href="/dashboard/journal" className="meridian-btn-primary text-xs px-4 py-2">
              Log Your First Trade
            </Link>
          </div>
        </div>

        {/* Agent Insights */}
        <div className="meridian-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold text-meridian-text-heading">Agent Insights</h2>
            <Link
              href="/dashboard/agents"
              className="text-xs text-meridian-steel hover:text-meridian-steel-600 transition-colors font-medium"
            >
              Open Chat
            </Link>
          </div>
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <div className="w-14 h-14 rounded-2xl bg-meridian-crimson/10 flex items-center justify-center mb-4">
              <Compass className="w-6 h-6 text-meridian-crimson" />
            </div>
            <p className="text-sm font-medium text-meridian-text-body mb-1">Your AI co-pilot awaits</p>
            <p className="text-xs text-meridian-text-muted mb-5 max-w-[240px]">
              Chat with Meridian&apos;s AI agents to get personalized analysis and trading insights.
            </p>
            <Link href="/dashboard/agents" className="meridian-btn-secondary text-xs px-4 py-2">
              Start a Conversation
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
