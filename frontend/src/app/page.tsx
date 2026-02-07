import Link from 'next/link';
import Image from 'next/image';
import { ArrowRight, Bot, BookOpen, BarChart3, Compass, TrendingUp, Shield, Anchor, Navigation, Waves } from 'lucide-react';

const features = [
  {
    title: 'AI Agents',
    description:
      'Intelligent trading assistants that analyze your patterns, identify blind spots, and provide personalized coaching to sharpen your edge.',
    icon: Bot,
    decorIcon: Navigation,
    gradient: 'from-meridian-crimson/5 via-white to-white',
    accentBorder: 'border-meridian-crimson/20',
    iconBg: 'bg-gradient-to-br from-meridian-crimson to-meridian-crimson-600',
    iconShadow: 'shadow-meridian-crimson',
    decorColor: 'text-meridian-crimson/[0.07]',
  },
  {
    title: 'Trade Journal',
    description:
      'Log every trade with rich context -- screenshots, notes, emotions, and setup tags. Build the dataset that powers your improvement.',
    icon: BookOpen,
    decorIcon: Anchor,
    gradient: 'from-meridian-steel/5 via-white to-white',
    accentBorder: 'border-meridian-steel/20',
    iconBg: 'bg-gradient-to-br from-meridian-steel to-meridian-steel-600',
    iconShadow: 'shadow-meridian-glow',
    decorColor: 'text-meridian-steel/[0.07]',
  },
  {
    title: 'Analytics',
    description:
      'Deep performance breakdowns by strategy, timeframe, and market conditions. See exactly where your profits and losses come from.',
    icon: BarChart3,
    decorIcon: Waves,
    gradient: 'from-emerald-500/5 via-white to-white',
    accentBorder: 'border-emerald-500/20',
    iconBg: 'bg-gradient-to-br from-emerald-500 to-emerald-600',
    iconShadow: 'shadow-[0_4px_14px_rgba(16,185,129,0.25)]',
    decorColor: 'text-emerald-500/[0.07]',
  },
];

const highlights = [
  {
    title: 'Pattern Recognition',
    description: 'AI identifies recurring setups and behavioral patterns across your trading history.',
    icon: TrendingUp,
    color: 'text-meridian-steel',
    iconBg: 'bg-gradient-to-br from-meridian-steel-50 to-meridian-steel-100',
    accentColor: 'bg-meridian-steel',
  },
  {
    title: 'Risk Awareness',
    description: 'Real-time position sizing guidance and drawdown alerts to protect your capital.',
    icon: Shield,
    color: 'text-emerald-600',
    iconBg: 'bg-gradient-to-br from-emerald-50 to-emerald-100',
    accentColor: 'bg-emerald-500',
  },
  {
    title: 'Find Your Edge',
    description: 'Quantify what works and what doesn\'t. Stop guessing and start trading with conviction.',
    icon: Compass,
    color: 'text-meridian-crimson',
    iconBg: 'bg-gradient-to-br from-meridian-crimson-50 to-meridian-crimson-100',
    accentColor: 'bg-meridian-crimson',
  },
];

function WaveDivider({ flip = false, color = '#F8FAFC' }: { flip?: boolean; color?: string }) {
  return (
    <div className={`w-full overflow-hidden leading-[0] ${flip ? 'rotate-180' : ''}`}>
      <svg
        viewBox="0 0 1440 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-[60px] sm:h-[80px] lg:h-[100px]"
        preserveAspectRatio="none"
      >
        <path
          d="M0,60 C240,120 480,0 720,60 C960,120 1200,0 1440,60 L1440,120 L0,120 Z"
          fill={color}
        />
        <path
          d="M0,80 C360,20 720,100 1080,40 C1260,10 1380,50 1440,80 L1440,120 L0,120 Z"
          fill={color}
          opacity="0.5"
        />
      </svg>
    </div>
  );
}

function WaveDividerNavyToWhite() {
  return (
    <div className="w-full overflow-hidden leading-[0]">
      <svg
        viewBox="0 0 1440 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-[60px] sm:h-[80px] lg:h-[100px]"
        preserveAspectRatio="none"
      >
        <path
          d="M0,40 C360,100 720,0 1080,60 C1260,90 1380,30 1440,50 L1440,120 L0,120 Z"
          fill="#F8FAFC"
        />
        <path
          d="M0,70 C240,30 480,90 720,50 C960,10 1200,80 1440,40 L1440,120 L0,120 Z"
          fill="#F8FAFC"
          opacity="0.6"
        />
      </svg>
    </div>
  );
}

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* ========== HERO SECTION ========== */}
      <div className="relative bg-[#17304e]">
        {/* Navigation */}
        <nav className="relative z-10 flex items-center justify-end px-8 py-5 max-w-7xl mx-auto">
          <div className="flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-sm text-white/80 hover:text-white transition-colors"
            >
              Dashboard
            </Link>
            <Link href="/dashboard" className="inline-flex items-center justify-center px-5 py-2 rounded-lg bg-gradient-to-r from-meridian-crimson to-meridian-crimson-600 font-semibold text-white text-sm shadow-[0_2px_12px_rgba(220,38,38,0.3)] hover:shadow-[0_4px_18px_rgba(220,38,38,0.45)] hover:scale-[1.03] active:scale-[0.98] transition-all duration-200 ease-out">
              Get Started
            </Link>
          </div>
        </nav>

        {/* Hero Content - transparent logo on CSS background */}
        <div className="flex flex-col items-center text-center px-6 pt-4 pb-4">
          <div className="mb-8 animate-fade-in">
            <Image
              src="/logo.png"
              alt="Meridian"
              width={450}
              height={421}
              className="rounded-2xl shadow-2xl"
              style={{ boxShadow: '0 0 100px 60px #17304e' }}
              priority
            />
          </div>
        </div>

        {/* Tagline */}
        <div className="text-center px-6 pb-8">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold tracking-tight leading-tight mb-6 text-white/90 animate-fade-in-up">
            We help you find
            {' '}
            <span className="text-gradient-meridian">your way.</span>
          </h2>

          <p className="text-base sm:text-lg text-white/70 max-w-2xl mx-auto mb-8 leading-relaxed animate-fade-in-up"
             style={{ animationDelay: '0.1s' }}>
            An AI-powered trading journal and research assistant that turns your trade
            data into actionable insights.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up"
               style={{ animationDelay: '0.2s' }}>
            <Link href="/dashboard" className="group inline-flex items-center justify-center px-8 py-3.5 rounded-lg bg-gradient-to-r from-meridian-crimson to-meridian-crimson-600 font-semibold text-white text-base gap-2 shadow-[0_4px_20px_rgba(220,38,38,0.35)] hover:shadow-[0_6px_28px_rgba(220,38,38,0.5)] hover:scale-[1.03] active:scale-[0.98] transition-all duration-200 ease-out">
              Get Started
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>
            <a href="#features" className="group inline-flex items-center justify-center px-8 py-3.5 rounded-lg border border-white/20 font-medium text-white backdrop-blur-sm bg-white/[0.03] hover:bg-white/10 hover:border-white/40 hover:scale-[1.03] active:scale-[0.98] shadow-[0_2px_8px_rgba(0,0,0,0.1)] hover:shadow-[0_4px_16px_rgba(0,0,0,0.15)] transition-all duration-200 ease-out text-base">
              Learn More
            </a>
          </div>
        </div>

        {/* Wave transition to light */}
        <WaveDividerNavyToWhite />
      </div>

      {/* ========== LIGHT FEATURES SECTION ========== */}
      <section id="features" className="relative z-10 px-6 pt-12 pb-20 max-w-6xl mx-auto bg-meridian-surface">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-meridian-crimson/[0.06] border border-meridian-crimson/10 mb-5">
            <Compass className="w-3.5 h-3.5 text-meridian-crimson" />
            <p className="text-xs font-semibold text-meridian-crimson uppercase tracking-wider">Core Features</p>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-meridian-text-heading mb-4">Everything you need to trade better</h2>
          <p className="text-meridian-text-muted text-lg max-w-xl mx-auto">
            Three pillars of improvement, powered by AI and built for serious traders.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature) => {
            const Icon = feature.icon;
            const DecorIcon = feature.decorIcon;
            return (
              <div
                key={feature.title}
                className={`relative overflow-hidden rounded-2xl border ${feature.accentBorder} bg-gradient-to-br ${feature.gradient} p-8 group hover:shadow-meridian-lg hover:border-meridian-border-dark transition-all duration-300 ease-out hover:-translate-y-1`}
              >
                {/* Decorative background icon */}
                <DecorIcon className={`absolute -right-4 -top-4 w-32 h-32 ${feature.decorColor} rotate-12 transition-transform duration-500 group-hover:rotate-[20deg] group-hover:scale-110`} strokeWidth={1.5} />

                {/* Icon */}
                <div className={`relative w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${feature.iconBg} ${feature.iconShadow}`}>
                  <Icon className="w-7 h-7 text-white" strokeWidth={2} />
                </div>

                <h3 className="text-xl font-semibold text-meridian-text-heading mb-3">{feature.title}</h3>
                <p className="text-meridian-text-muted leading-relaxed text-sm">
                  {feature.description}
                </p>

                {/* Bottom accent line */}
                <div className={`absolute bottom-0 left-8 right-8 h-[2px] rounded-full ${feature.iconBg} opacity-0 group-hover:opacity-40 transition-opacity duration-300`} />
              </div>
            );
          })}
        </div>
      </section>

      {/* Decorative wave separator */}
      <div className="bg-meridian-surface">
        <div className="max-w-4xl mx-auto px-6">
          <div className="h-px bg-gradient-to-r from-transparent via-meridian-border-dark to-transparent" />
        </div>
      </div>

      {/* Secondary highlights */}
      <section className="relative z-10 px-6 py-20 max-w-6xl mx-auto bg-meridian-surface">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {highlights.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.title} className="relative bg-white rounded-xl border border-meridian-border p-6 hover:shadow-meridian-card-hover hover:border-meridian-border-dark transition-all duration-200 group">
                {/* Accent bar on left */}
                <div className={`absolute top-4 left-0 w-[3px] h-10 rounded-r-full ${item.accentColor} opacity-80 group-hover:h-14 group-hover:opacity-100 transition-all duration-300`} />

                <div className="flex items-start gap-4 pl-2">
                  <div className={`flex-shrink-0 w-11 h-11 rounded-xl ${item.iconBg} flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${item.color}`} strokeWidth={2} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-meridian-text-heading mb-1.5">{item.title}</h3>
                    <p className="text-meridian-text-muted text-sm leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ========== CTA SECTION (Navy) ========== */}
      <div className="bg-meridian-surface">
        <WaveDivider flip={true} color="#17304e" />
      </div>
      <section className="relative z-10 bg-[#17304e] px-6 py-24 overflow-hidden">
        {/* Decorative compass elements */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full border border-white/[0.06]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full border border-white/[0.08]" />

        <div className="relative max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.06] border border-white/10 mb-6">
            <Compass className="w-3.5 h-3.5 text-meridian-crimson-300" />
            <span className="text-xs font-medium text-white/70 uppercase tracking-wider">Set Your Course</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-5">Ready to navigate your trading?</h2>
          <p className="text-meridian-slate-300 mb-10 max-w-lg mx-auto text-lg leading-relaxed">
            Start journaling your trades today and let Meridian&apos;s AI agents guide you toward
            consistent profitability.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/dashboard" className="group inline-flex items-center justify-center px-8 py-3.5 rounded-lg bg-gradient-to-r from-meridian-crimson to-meridian-crimson-600 font-semibold text-white text-base gap-2 shadow-[0_4px_20px_rgba(220,38,38,0.35)] hover:shadow-[0_6px_28px_rgba(220,38,38,0.5)] hover:scale-[1.03] active:scale-[0.98] transition-all duration-200 ease-out">
              Open Dashboard
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </div>
      </section>
      <WaveDividerNavyToWhite />

      {/* Footer (light) */}
      <footer className="relative z-10 bg-meridian-surface border-t border-meridian-border px-6 py-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-meridian-navy to-meridian-navy-700 flex items-center justify-center">
              <Compass className="w-3.5 h-3.5 text-white/80" strokeWidth={2} />
            </div>
            <span className="text-meridian-text-heading text-sm font-semibold tracking-tight">Meridian</span>
          </div>
          <p className="text-meridian-text-light text-xs">
            Built for traders who want to improve. Not financial advice.
          </p>
        </div>
      </footer>
    </main>
  );
}
