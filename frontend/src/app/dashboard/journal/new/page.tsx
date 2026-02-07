'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

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

  return (
    <div>
      {/* Back link + Header */}
      <div className="mb-8">
        <Link
          href="/dashboard/journal"
          className="inline-flex items-center gap-2 text-meridian-text-muted hover:text-meridian-navy text-sm font-medium transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Journal
        </Link>
        <h1 className="text-2xl font-bold text-meridian-text-heading">New Trade</h1>
        <p className="text-meridian-text-muted text-sm mt-1">Record a new trade entry in your journal.</p>
      </div>

      <form onSubmit={handleSubmit} className="max-w-2xl space-y-6">
        {/* Trade Details Card */}
        <div className="meridian-card p-6 space-y-5">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-1 h-6 rounded-full bg-meridian-crimson" />
            <h2 className="text-lg font-semibold text-meridian-text-heading">Trade Details</h2>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="meridian-label">Ticker</label>
              <input
                type="text"
                required
                className="meridian-input"
                placeholder="AAPL"
                value={formData.ticker}
                onChange={(e) => setFormData({ ...formData, ticker: e.target.value.toUpperCase() })}
              />
            </div>
            <div>
              <label className="meridian-label">Direction</label>
              <select
                className="meridian-input"
                value={formData.direction}
                onChange={(e) => setFormData({ ...formData, direction: e.target.value as 'Long' | 'Short' })}
              >
                <option value="Long">Long</option>
                <option value="Short">Short</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="meridian-label">Entry Date</label>
              <input
                type="date"
                required
                className="meridian-input"
                value={formData.entryDate}
                onChange={(e) => setFormData({ ...formData, entryDate: e.target.value })}
              />
            </div>
            <div>
              <label className="meridian-label">Entry Price</label>
              <input
                type="number"
                step="0.01"
                required
                className="meridian-input"
                placeholder="0.00"
                value={formData.entryPrice}
                onChange={(e) => setFormData({ ...formData, entryPrice: e.target.value })}
              />
            </div>
            <div>
              <label className="meridian-label">Position Size</label>
              <input
                type="number"
                step="1"
                required
                className="meridian-input"
                placeholder="100"
                value={formData.positionSize}
                onChange={(e) => setFormData({ ...formData, positionSize: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="meridian-label">Stop Loss</label>
              <input
                type="number"
                step="0.01"
                className="meridian-input"
                placeholder="Optional"
                value={formData.stopLoss}
                onChange={(e) => setFormData({ ...formData, stopLoss: e.target.value })}
              />
            </div>
            <div>
              <label className="meridian-label">Take Profit</label>
              <input
                type="number"
                step="0.01"
                className="meridian-input"
                placeholder="Optional"
                value={formData.takeProfit}
                onChange={(e) => setFormData({ ...formData, takeProfit: e.target.value })}
              />
            </div>
          </div>
        </div>

        {/* Journal Entry Card */}
        <div className="meridian-card p-6 space-y-5">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-1 h-6 rounded-full bg-meridian-steel" />
            <h2 className="text-lg font-semibold text-meridian-text-heading">Journal Entry</h2>
          </div>

          <div>
            <label className="meridian-label">Thesis</label>
            <textarea
              rows={3}
              className="meridian-input"
              placeholder="Why are you taking this trade?"
              value={formData.thesis}
              onChange={(e) => setFormData({ ...formData, thesis: e.target.value })}
            />
          </div>

          <div>
            <label className="meridian-label">Emotional State</label>
            <input
              type="text"
              className="meridian-input"
              placeholder="e.g., Confident, Anxious, FOMO"
              value={formData.emotionalState}
              onChange={(e) => setFormData({ ...formData, emotionalState: e.target.value })}
            />
          </div>

          <div>
            <label className="meridian-label">Notes</label>
            <textarea
              rows={3}
              className="meridian-input"
              placeholder="Additional notes..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={isSubmitting}
            className="meridian-btn-primary px-6 py-2.5"
          >
            {isSubmitting ? 'Creating...' : 'Create Trade'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="meridian-btn-secondary px-6 py-2.5"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
