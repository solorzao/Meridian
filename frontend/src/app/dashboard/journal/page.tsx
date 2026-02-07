import Link from 'next/link';
import { BookOpen, Plus, Filter } from 'lucide-react';

const tabs = ['All Trades', 'Open', 'Closed'];

const tableHeaders = [
  'Date',
  'Ticker',
  'Direction',
  'Entry Price',
  'Exit Price',
  'P&L',
  'Status',
];

export default function JournalPage() {
  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-meridian-text-heading">Trade Journal</h1>
          <p className="text-meridian-text-muted text-sm mt-1">Track, review, and learn from every trade.</p>
        </div>
        <Link
          href="/dashboard/journal/new"
          className="meridian-btn-primary text-sm px-5 py-2.5 gap-2"
        >
          <Plus className="h-4 w-4" />
          New Trade
        </Link>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1 mb-6 bg-meridian-surface-200 rounded-lg p-1 w-fit border border-meridian-border">
        {tabs.map((tab, i) => (
          <button
            key={tab}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              i === 0
                ? 'bg-white text-meridian-navy shadow-sm'
                : 'text-meridian-text-muted hover:text-meridian-navy hover:bg-white/50'
            }`}
          >
            {tab}
          </button>
        ))}
        <div className="w-px h-5 bg-meridian-border mx-1" />
        <button className="p-2 rounded-md text-meridian-text-muted hover:text-meridian-navy hover:bg-white/50 transition-colors">
          <Filter className="h-4 w-4" />
        </button>
      </div>

      {/* Table */}
      <div className="meridian-card overflow-hidden">
        {/* Table Header */}
        <div className="grid grid-cols-7 gap-4 px-6 py-3 border-b border-meridian-border bg-meridian-surface-200">
          {tableHeaders.map((header) => (
            <div key={header} className="text-xs font-semibold text-meridian-text-muted uppercase tracking-wider">
              {header}
            </div>
          ))}
        </div>

        {/* Empty State */}
        <div className="flex flex-col items-center justify-center py-20 px-6">
          <div className="w-16 h-16 rounded-2xl bg-meridian-surface-200 border border-meridian-border flex items-center justify-center mb-5">
            <BookOpen className="h-8 w-8 text-meridian-text-light" />
          </div>
          <h3 className="text-meridian-text-heading font-semibold text-lg mb-2">No trades recorded yet</h3>
          <p className="text-meridian-text-muted text-sm text-center max-w-sm mb-6">
            Your journal is empty. Start logging trades to track your performance, identify patterns, and improve your strategy.
          </p>
          <Link
            href="/dashboard/journal/new"
            className="meridian-btn-primary text-sm px-5 py-2.5 gap-2"
          >
            <Plus className="h-4 w-4" />
            Log Your First Trade
          </Link>
        </div>
      </div>
    </div>
  );
}
