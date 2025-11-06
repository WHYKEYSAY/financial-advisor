'use client';

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            CreditSphere
          </div>
          <div className="flex items-center gap-4">
            <Link href="/en/login" className="text-gray-600 hover:text-gray-900">
              Login
            </Link>
            <Link href="/en/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              Register
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Your AI Financial Co-Pilot
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Automatically analyze spending, maximize credit card rewards, and optimize your credit health.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/en/register" className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 shadow-lg">
              Start Free Analysis
            </Link>
            <Link href="/en/pricing" className="bg-white text-gray-900 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-50 shadow-lg border">
              View Pricing
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-32 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-2">Smart Categorization</h3>
            <p className="text-gray-600">AI categorization with fuzzy matching</p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">💳</div>
            <h3 className="text-xl font-bold mb-2">Rewards Optimization</h3>
            <p className="text-gray-600">Maximize credit card rewards</p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-2">AI Insights</h3>
            <p className="text-gray-600">Intelligent spending analysis</p>
          </div>
        </div>
      </main>

      <footer className="container mx-auto px-4 py-8 mt-32 border-t">
        <div className="text-center text-gray-600">
          <p>✅ Frontend deployed successfully to Vercel!</p>
          <p className="text-sm mt-2">Note: Temporarily using /home route. Will restore i18n routing after fixing compatibility issues.</p>
        </div>
      </footer>
    </div>
  );
}
