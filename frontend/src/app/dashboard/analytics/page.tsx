import { TrendingUp, PieChart, Calendar, DollarSign, BarChart3, Target, Activity } from 'lucide-react';

const stats = [
  { label: 'Total P&L', value: '$0.00', change: '--', icon: DollarSign, color: '#10B981', bg: 'bg-emerald-500/10' },
  { label: 'Win Rate', value: '0%', change: '--', icon: Target, color: '#3B82F6', bg: 'bg-blue-500/10' },
  { label: 'Avg R:R', value: '--', change: '--', icon: BarChart3, color: '#F59E0B', bg: 'bg-amber-500/10' },
  { label: 'Total Trades', value: '0', change: '--', icon: Activity, color: '#DC2626', bg: 'bg-red-500/10' },
];

export default function AnalyticsPage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-meridian-text-heading">Analytics</h1>
        <p className="text-meridian-text-muted text-sm mt-1">Insights and performance metrics for your trading activity.</p>
      </div>

      {/* Stats Summary Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="meridian-card-hover p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-meridian-text-muted text-sm font-medium">{stat.label}</span>
                <div
                  className={`w-9 h-9 rounded-lg flex items-center justify-center ${stat.bg}`}
                >
                  <Icon className="h-4 w-4" style={{ color: stat.color }} />
                </div>
              </div>
              <p className="text-2xl font-bold text-meridian-text-heading">{stat.value}</p>
              <p className="text-xs text-meridian-text-light mt-1">{stat.change}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* P&L Over Time */}
        <div className="meridian-card overflow-hidden">
          <div className="h-1 bg-meridian-crimson" />
          <div className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-lg bg-meridian-crimson/10 flex items-center justify-center">
                <TrendingUp className="h-4 w-4 text-meridian-crimson" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">P&L Over Time</h2>
                <p className="text-xs text-meridian-text-light">Cumulative profit and loss</p>
              </div>
            </div>
            <div className="h-56 flex flex-col items-center justify-center">
              {/* Placeholder chart bars */}
              <div className="w-full space-y-3 px-4 opacity-20">
                <div className="flex items-end gap-1 h-32">
                  {[40, 55, 35, 65, 45, 70, 50, 75, 60, 80, 55, 85].map((h, i) => (
                    <div key={i} className="flex-1 rounded-t bg-meridian-crimson" style={{ height: `${h}%` }} />
                  ))}
                </div>
                <div className="h-px bg-meridian-border" />
              </div>
              <p className="text-meridian-text-muted text-sm mt-4">Add trades to see your P&L chart</p>
            </div>
          </div>
        </div>

        {/* Strategy Breakdown */}
        <div className="meridian-card overflow-hidden">
          <div className="h-1 bg-meridian-steel" />
          <div className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-lg bg-meridian-steel/10 flex items-center justify-center">
                <PieChart className="h-4 w-4 text-meridian-steel" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">Strategy Breakdown</h2>
                <p className="text-xs text-meridian-text-light">Performance by strategy type</p>
              </div>
            </div>
            <div className="h-56 flex flex-col items-center justify-center">
              {/* Placeholder donut */}
              <div className="relative w-28 h-28 opacity-20">
                <div className="absolute inset-0 rounded-full border-[12px] border-meridian-steel" />
                <div className="absolute inset-0 rounded-full border-[12px] border-transparent border-t-emerald-500 border-r-emerald-500 rotate-45" />
                <div className="absolute inset-3 rounded-full bg-white" />
              </div>
              <p className="text-meridian-text-muted text-sm mt-4">Strategy data will appear here</p>
            </div>
          </div>
        </div>

        {/* Monthly Performance - Full Width */}
        <div className="meridian-card overflow-hidden lg:col-span-2">
          <div className="h-1 bg-emerald-500" />
          <div className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <Calendar className="h-4 w-4 text-emerald-600" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">Monthly Performance</h2>
                <p className="text-xs text-meridian-text-light">Monthly P&L heatmap view</p>
              </div>
            </div>
            <div className="h-40 flex flex-col items-center justify-center">
              {/* Placeholder heatmap grid */}
              <div className="grid grid-cols-12 gap-1.5 opacity-20 mb-4">
                {Array.from({ length: 48 }).map((_, i) => (
                  <div
                    key={i}
                    className="w-6 h-6 rounded-sm"
                    style={{
                      backgroundColor: ['#10B981', '#E2E8F0', '#DC2626', '#E2E8F0'][i % 4],
                    }}
                  />
                ))}
              </div>
              <p className="text-meridian-text-muted text-sm">Monthly heatmap will populate with your trading data</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
