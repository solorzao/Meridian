import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
        Meridian
      </h1>
      <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
        AI-powered trading journal & research assistant
      </p>
      <div className="flex gap-4">
        <Link
          href="/dashboard"
          className="rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 transition-colors"
        >
          Open Dashboard
        </Link>
      </div>
    </main>
  );
}
