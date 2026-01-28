'use client';

import { useState } from 'react';

interface ScrapingResult {
  response: string;
  trace?: any[];
  sessionId: string;
}

export default function EnhancedScraper() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScrapingResult | null>(null);
  const [error, setError] = useState('');
  const [history, setHistory] = useState<Array<{ url: string; timestamp: Date }>>([]);

  const handleScrape = async () => {
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch('/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Failed to scrape URL');
      }

      setResult(data);
      
      // Add to history
      setHistory(prev => [
        { url, timestamp: new Date() },
        ...prev.slice(0, 9) // Keep last 10
      ]);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const loadFromHistory = (historicalUrl: string) => {
    setUrl(historicalUrl);
  };
  console.log(result?.response);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-full mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI Web Scraper
          </h1>
          <p className="text-xl text-gray-600">
            Intelligent content extraction powered by AWS Bedrock
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Input Card */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    🔗 Website URL
                  </label>
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleScrape()}
                    placeholder="https://example.com/article"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition text-lg"
                    disabled={loading}
                  />
                </div>

                <button
                  onClick={handleScrape}
                  disabled={loading}
                  className="w-full px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:scale-[1.02] active:scale-[0.98]"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-3">
                      <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span className="text-lg">Analyzing and extracting content...</span>
                    </span>
                  ) : (
                    <span className="text-lg">🚀 Start Scraping</span>
                  )}
                </button>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-red-900 mb-1">Scraping Failed</h3>
                    <p className="text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results Display */}
            {result && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    ✨ Extracted Content
                  </h2>
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigator.clipboard.writeText(result.response)}
                      className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition text-sm font-medium"
                      title="Copy to clipboard"
                    >
                      📋 Copy
                    </button>
                    <button
                      onClick={() => {
                        const blob = new Blob([result.response], { type: 'text/plain' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `scraped-${Date.now()}.txt`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                      className="px-4 py-2 bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded-lg transition text-sm font-medium"
                      title="Download as file"
                    >
                      💾 Save
                    </button>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl p-6 border-2 border-gray-200">
                  <div className="max-h-[500px] overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed font-mono">
                      {result.response}
                    </pre>
                  </div>
                </div>

                {result.sessionId && (
                  <div className="mt-4 text-xs text-gray-500 font-mono bg-gray-50 p-3 rounded-lg">
                    Session ID: {result.sessionId}
                  </div>
                )}
              </div>
            )}
          </div>
        
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            {result && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Statistics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Characters</span>
                    <span className="font-bold text-indigo-600">{result.response.length.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Words</span>
                    <span className="font-bold text-indigo-600">{result.response.split(/\s+/).length.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Lines</span>
                    <span className="font-bold text-indigo-600">{result.response.split('\n').length.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}

            {/* History */}
            {history.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">🕒 History</h3>
                  <button
                    onClick={clearHistory}
                    className="text-xs text-red-600 hover:text-red-700 font-medium"
                  >
                    Clear
                  </button>
                </div>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {history.map((item, index) => (
                    <button
                      key={index}
                      onClick={() => loadFromHistory(item.url)}
                      className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition text-sm"
                    >
                      <div className="font-medium text-gray-900 truncate">{item.url}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {item.timestamp.toLocaleTimeString()}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Info Card */}
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
              <h3 className="text-lg font-bold mb-3">💡 How it works</h3>
              <ul className="space-y-2 text-sm opacity-90">
                <li className="flex items-start gap-2">
                  <span>1️⃣</span>
                  <span>Enter any public URL</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>2️⃣</span>
                  <span>AI analyzes the page</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>3️⃣</span>
                  <span>Clean content extracted</span>
                </li>
                <li className="flex items-start gap-2">
                  <span>4️⃣</span>
                  <span>Download or copy results</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
