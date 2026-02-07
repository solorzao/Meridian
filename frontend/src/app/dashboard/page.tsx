export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Dashboard</h1>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Open Trades', value: '--', color: 'blue' },
          { label: 'Total P&L', value: '--', color: 'green' },
          { label: 'Win Rate', value: '--', color: 'purple' },
          { label: 'Profit Factor', value: '--', color: 'orange' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Placeholder sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Trades</h2>
          <p className="text-gray-500 dark:text-gray-400">No trades yet. Start by adding a trade in the Journal.</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Agent Insights</h2>
          <p className="text-gray-500 dark:text-gray-400">Chat with your AI agents to get personalized insights.</p>
        </div>
      </div>
    </div>
  );
}
