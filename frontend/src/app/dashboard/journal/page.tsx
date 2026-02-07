import Link from 'next/link';

export default function JournalPage() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Trade Journal</h1>
        <Link
          href="/dashboard/journal/new"
          className="rounded-lg bg-blue-600 px-4 py-2 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          + New Trade
        </Link>
      </div>

      {/* Trade list placeholder */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-6 text-center text-gray-500 dark:text-gray-400">
          <p>No trades recorded yet.</p>
          <p className="text-sm mt-2">Start tracking your trades to build your journal.</p>
        </div>
      </div>
    </div>
  );
}
