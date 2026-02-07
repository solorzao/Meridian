export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Settings</h1>

      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Account</h2>
          <p className="text-gray-500 dark:text-gray-400">Account settings will be available after authentication is configured.</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Subscription</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-900 dark:text-white font-medium">Free Plan</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Upgrade to Premium for real-time data and advanced agents.</p>
            </div>
            <button className="rounded-lg bg-blue-600 px-4 py-2 text-white text-sm font-medium hover:bg-blue-700 transition-colors">
              Upgrade
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Agent Configuration</h2>
          <p className="text-gray-500 dark:text-gray-400">Configure your AI agents&apos; behavior and preferences.</p>
        </div>
      </div>
    </div>
  );
}
