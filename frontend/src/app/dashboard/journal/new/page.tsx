'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function NewTradePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    ticker: '',
    direction: 'Long' as 'Long' | 'Short',
    entryDate: new Date().toISOString().split('T')[0],
    entryPrice: '',
    positionSize: '',
    stopLoss: '',
    takeProfit: '',
    thesis: '',
    emotionalState: '',
    notes: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/trades`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          entryPrice: parseFloat(formData.entryPrice),
          positionSize: parseFloat(formData.positionSize),
          stopLoss: formData.stopLoss ? parseFloat(formData.stopLoss) : undefined,
          takeProfit: formData.takeProfit ? parseFloat(formData.takeProfit) : undefined,
        }),
      });

      if (response.ok) {
        router.push('/dashboard/journal');
      }
    } catch (error) {
      console.error('Failed to create trade:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputClass = "w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500";
  const labelClass = "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1";

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">New Trade</h1>

      <form onSubmit={handleSubmit} className="max-w-2xl space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Trade Details</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Ticker</label>
              <input type="text" required className={inputClass} placeholder="AAPL"
                value={formData.ticker}
                onChange={(e) => setFormData({ ...formData, ticker: e.target.value.toUpperCase() })} />
            </div>
            <div>
              <label className={labelClass}>Direction</label>
              <select className={inputClass}
                value={formData.direction}
                onChange={(e) => setFormData({ ...formData, direction: e.target.value as 'Long' | 'Short' })}>
                <option value="Long">Long</option>
                <option value="Short">Short</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className={labelClass}>Entry Date</label>
              <input type="date" required className={inputClass}
                value={formData.entryDate}
                onChange={(e) => setFormData({ ...formData, entryDate: e.target.value })} />
            </div>
            <div>
              <label className={labelClass}>Entry Price</label>
              <input type="number" step="0.01" required className={inputClass} placeholder="0.00"
                value={formData.entryPrice}
                onChange={(e) => setFormData({ ...formData, entryPrice: e.target.value })} />
            </div>
            <div>
              <label className={labelClass}>Position Size</label>
              <input type="number" step="1" required className={inputClass} placeholder="100"
                value={formData.positionSize}
                onChange={(e) => setFormData({ ...formData, positionSize: e.target.value })} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Stop Loss</label>
              <input type="number" step="0.01" className={inputClass} placeholder="Optional"
                value={formData.stopLoss}
                onChange={(e) => setFormData({ ...formData, stopLoss: e.target.value })} />
            </div>
            <div>
              <label className={labelClass}>Take Profit</label>
              <input type="number" step="0.01" className={inputClass} placeholder="Optional"
                value={formData.takeProfit}
                onChange={(e) => setFormData({ ...formData, takeProfit: e.target.value })} />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Journal Entry</h2>

          <div>
            <label className={labelClass}>Thesis</label>
            <textarea rows={3} className={inputClass} placeholder="Why are you taking this trade?"
              value={formData.thesis}
              onChange={(e) => setFormData({ ...formData, thesis: e.target.value })} />
          </div>

          <div>
            <label className={labelClass}>Emotional State</label>
            <input type="text" className={inputClass} placeholder="e.g., Confident, Anxious, FOMO"
              value={formData.emotionalState}
              onChange={(e) => setFormData({ ...formData, emotionalState: e.target.value })} />
          </div>

          <div>
            <label className={labelClass}>Notes</label>
            <textarea rows={3} className={inputClass} placeholder="Additional notes..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })} />
          </div>
        </div>

        <div className="flex gap-3">
          <button type="submit" disabled={isSubmitting}
            className="rounded-lg bg-blue-600 px-6 py-2 text-white font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {isSubmitting ? 'Creating...' : 'Create Trade'}
          </button>
          <button type="button" onClick={() => router.back()}
            className="rounded-lg border border-gray-300 dark:border-gray-600 px-6 py-2 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
