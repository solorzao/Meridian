export default function AnalyticsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">P&L Over Time</h2>
          <div className="h-64 flex items-center justify-center text-gray-400">
            Chart will render here with trade data
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Strategy Breakdown</h2>
          <div className="h-64 flex items-center justify-center text-gray-400">
            Strategy performance chart will render here
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Monthly Performance</h2>
          <div className="h-48 flex items-center justify-center text-gray-400">
            Monthly P&L heatmap will render here
          </div>
        </div>
      </div>
    </div>
  );
}
