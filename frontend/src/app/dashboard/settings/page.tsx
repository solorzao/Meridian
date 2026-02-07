import { User, CreditCard, Cpu, Shield, Bell, Trash2 } from 'lucide-react';

function ToggleSwitch({ enabled = false }: { enabled?: boolean }) {
  return (
    <div
      className={`relative w-11 h-6 rounded-full transition-colors cursor-pointer ${
        enabled ? 'bg-meridian-crimson' : 'bg-meridian-surface-400'
      }`}
    >
      <div
        className={`absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${
          enabled ? 'left-6' : 'left-1'
        }`}
      />
    </div>
  );
}

export default function SettingsPage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-meridian-text-heading">Settings</h1>
        <p className="text-meridian-text-muted text-sm mt-1">Manage your account, subscription, and agent preferences.</p>
      </div>

      <div className="max-w-3xl space-y-6">
        {/* Account Section */}
        <div className="meridian-card overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-meridian-steel/10 flex items-center justify-center">
                <User className="h-5 w-5 text-meridian-steel" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">Account</h2>
                <p className="text-xs text-meridian-text-light">Manage your profile and preferences</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-meridian-border/50">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Email</p>
                  <p className="text-xs text-meridian-text-light">Your login email address</p>
                </div>
                <span className="text-sm text-meridian-text-muted">Not configured</span>
              </div>
              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Display Name</p>
                  <p className="text-xs text-meridian-text-light">Shown on your journal entries</p>
                </div>
                <span className="text-sm text-meridian-text-muted">Not configured</span>
              </div>
            </div>
            <p className="text-meridian-text-muted text-sm mt-4 p-3 rounded-lg bg-meridian-surface-200 border border-meridian-border">
              Account settings will be fully available after authentication is configured.
            </p>
          </div>
        </div>

        {/* Subscription Section */}
        <div className="meridian-card overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                <CreditCard className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">Subscription</h2>
                <p className="text-xs text-meridian-text-light">Manage your plan and billing</p>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 rounded-xl bg-meridian-surface-200 border border-meridian-border">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <p className="text-meridian-text-heading font-semibold">Free Plan</p>
                  <span className="px-2 py-0.5 rounded-full bg-meridian-surface-300 text-meridian-text-muted text-xs font-medium">
                    Current
                  </span>
                </div>
                <p className="text-sm text-meridian-text-muted">
                  Upgrade to Premium for real-time data, advanced agents, and unlimited history.
                </p>
              </div>
              <button className="meridian-btn-primary text-sm px-5 py-2.5 whitespace-nowrap ml-4">
                Upgrade
              </button>
            </div>
          </div>
        </div>

        {/* Agent Configuration Section */}
        <div className="meridian-card overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                <Cpu className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">Agent Configuration</h2>
                <p className="text-xs text-meridian-text-light">Customize your AI agents&apos; behavior</p>
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between py-3.5 px-1 border-b border-meridian-border/50">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Auto-analyze new trades</p>
                  <p className="text-xs text-meridian-text-light">Run analysis agent on every new journal entry</p>
                </div>
                <ToggleSwitch enabled={true} />
              </div>
              <div className="flex items-center justify-between py-3.5 px-1 border-b border-meridian-border/50">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Weekly performance digest</p>
                  <p className="text-xs text-meridian-text-light">Receive a coaching summary every Sunday</p>
                </div>
                <ToggleSwitch enabled={true} />
              </div>
              <div className="flex items-center justify-between py-3.5 px-1 border-b border-meridian-border/50">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Risk alerts</p>
                  <p className="text-xs text-meridian-text-light">Get notified when positions exceed risk parameters</p>
                </div>
                <ToggleSwitch enabled={false} />
              </div>
              <div className="flex items-center justify-between py-3.5 px-1">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Market screener notifications</p>
                  <p className="text-xs text-meridian-text-light">Alert when screener finds matching opportunities</p>
                </div>
                <ToggleSwitch enabled={false} />
              </div>
            </div>
          </div>
        </div>

        {/* Notifications Section */}
        <div className="meridian-card overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center">
                <Bell className="h-5 w-5 text-violet-600" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">Notifications</h2>
                <p className="text-xs text-meridian-text-light">Control how you receive alerts</p>
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between py-3.5 px-1 border-b border-meridian-border/50">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Email notifications</p>
                  <p className="text-xs text-meridian-text-light">Receive alerts via email</p>
                </div>
                <ToggleSwitch enabled={false} />
              </div>
              <div className="flex items-center justify-between py-3.5 px-1">
                <div>
                  <p className="text-sm font-medium text-meridian-text-heading">Browser notifications</p>
                  <p className="text-xs text-meridian-text-light">Desktop push notifications for alerts</p>
                </div>
                <ToggleSwitch enabled={false} />
              </div>
            </div>
          </div>
        </div>

        {/* Security Section */}
        <div className="meridian-card overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-meridian-surface-300 flex items-center justify-center">
                <Shield className="h-5 w-5 text-meridian-text-muted" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-text-heading">Security</h2>
                <p className="text-xs text-meridian-text-light">Protect your account</p>
              </div>
            </div>
            <div className="flex items-center justify-between py-3.5 px-1">
              <div>
                <p className="text-sm font-medium text-meridian-text-heading">Two-factor authentication</p>
                <p className="text-xs text-meridian-text-light">Add an extra layer of security to your account</p>
              </div>
              <button className="meridian-btn-secondary text-sm px-4 py-2">
                Enable
              </button>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-xl border border-meridian-crimson/30 overflow-hidden shadow-meridian-card">
          <div className="h-1 bg-meridian-crimson" />
          <div className="p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-meridian-crimson/10 flex items-center justify-center">
                <Trash2 className="h-5 w-5 text-meridian-crimson" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-meridian-crimson">Danger Zone</h2>
                <p className="text-xs text-meridian-text-light">Irreversible actions</p>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 rounded-xl bg-meridian-crimson-50 border border-meridian-crimson/20">
              <div>
                <p className="text-sm font-medium text-meridian-text-heading">Delete Account</p>
                <p className="text-xs text-meridian-text-light">
                  Permanently delete your account and all associated data. This cannot be undone.
                </p>
              </div>
              <button className="rounded-lg border border-meridian-crimson/50 bg-transparent px-4 py-2 text-sm text-meridian-crimson font-medium hover:bg-meridian-crimson/10 transition-colors whitespace-nowrap ml-4">
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
