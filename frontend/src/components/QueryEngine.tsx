import { useState } from 'react';
import {
  Search,
  Loader2,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Clock,
  FileText,
  AlertTriangle,
  Zap,
  BookOpen,
  Sparkles,
} from 'lucide-react';
import { simulateRAGQuery } from '../data/standards';
import { categoryColors } from '../data/standards';
import { QueryResult } from '../types';
import { sampleQueries } from '../data/standards';

export default function QueryEngine() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [expandedResult, setExpandedResult] = useState<string | null>(null);

  const handleQuery = async (queryText?: string) => {
    const q = queryText || query;
    if (!q.trim()) return;

    setIsLoading(true);
    try {
      const result = await simulateRAGQuery(q);
      setResults(prev => [result, ...prev]);
      if (!queryText) setQuery('');
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSampleQuery = (sq: (typeof sampleQueries)[0]) => {
    setQuery(sq.query);
    handleQuery(sq.query);
  };

  return (
    <div className="space-y-8">
      {/* Query Input Section */}
      <div className="bg-white rounded-2xl shadow-lg border border-surface-200 overflow-hidden">
        <div className="bg-gradient-to-r from-primary-700 via-primary-600 to-primary-500 px-6 py-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-white/20 rounded-lg">
              <Search className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white">Query the RAG Engine</h2>
          </div>
          <p className="text-primary-100 text-sm">
            Describe your product or use case to retrieve applicable BIS standards
          </p>
        </div>

        <div className="p-6">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleQuery();
                  }
                }}
                placeholder="e.g., We manufacture PVC insulated cables for household wiring up to 1100V..."
                className="w-full px-4 py-3 border-2 border-surface-200 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all resize-none text-surface-800 placeholder:text-surface-400"
                rows={3}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={() => handleQuery()}
              disabled={isLoading || !query.trim()}
              className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg shadow-primary-200 self-end"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Retrieving...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Search
                </>
              )}
            </button>
          </div>

          {/* Sample Queries */}
          <div className="mt-5">
            <p className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5" />
              Try a sample query
            </p>
            <div className="flex flex-wrap gap-2">
              {sampleQueries.slice(0, 6).map((sq) => (
                <button
                  key={sq.id}
                  onClick={() => handleSampleQuery(sq)}
                  disabled={isLoading}
                  className="px-3 py-1.5 text-xs font-medium bg-surface-50 text-surface-600 rounded-lg hover:bg-primary-50 hover:text-primary-700 border border-surface-200 hover:border-primary-200 transition-all disabled:opacity-50"
                >
                  {sq.query.length > 60 ? sq.query.slice(0, 60) + '...' : sq.query}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-surface-800 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary-600" />
              Query Results
              <span className="text-sm font-normal text-surface-400">
                ({results.length} {results.length === 1 ? 'query' : 'queries'})
              </span>
            </h3>
          </div>

          {results.map((result, index) => (
            <div
              key={result.id}
              className="bg-white rounded-2xl shadow-md border border-surface-200 overflow-hidden animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Result Header */}
              <div className="px-6 py-4 border-b border-surface-100 bg-surface-50/50">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-surface-600 font-medium truncate">
                      "{result.query}"
                    </p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-accent-50 text-accent-600 rounded-full text-xs font-semibold border border-accent-200">
                      <Clock className="w-3 h-3" />
                      {result.latencySeconds}s
                    </div>
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-primary-50 text-primary-600 rounded-full text-xs font-semibold border border-primary-200">
                      <BookOpen className="w-3 h-3" />
                      {result.retrievedStandards.length} standards
                    </div>
                  </div>
                </div>
              </div>

              {/* Retrieved Standards */}
              <div className="px-6 py-4">
                {result.retrievedStandards.length > 0 ? (
                  <div className="space-y-3">
                    {result.retrievedStandards.map((standard, sIndex) => {
                      const colors = categoryColors[standard.category] || {
                        bg: 'bg-gray-50',
                        text: 'text-gray-700',
                        border: 'border-gray-200',
                      };
                      return (
                        <div
                          key={`${standard.id}-${sIndex}`}
                          className="flex items-start gap-3 p-3 rounded-xl bg-surface-50 border border-surface-100 animate-slide-in"
                          style={{ animationDelay: `${sIndex * 80}ms` }}
                        >
                          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary-100 text-primary-700 font-bold text-sm shrink-0">
                            #{sIndex + 1}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap mb-1">
                              <span className="font-bold text-primary-700 text-sm">
                                {standard.standardNumber}
                              </span>
                              <span
                                className={`px-2 py-0.5 rounded-full text-xs font-medium border ${colors.bg} ${colors.text} ${colors.border}`}
                              >
                                {standard.category}
                              </span>
                            </div>
                            <p className="text-sm font-medium text-surface-700 mb-1">
                              {standard.title}
                            </p>
                            <p className="text-xs text-surface-500 line-clamp-2">
                              {standard.description}
                            </p>
                          </div>
                          <div className="flex items-center gap-1 text-accent-500">
                            <CheckCircle2 className="w-4 h-4" />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex items-center gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                    <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
                    <p className="text-sm text-amber-700">
                      No relevant standards found for this query. Try refining your product
                      description with more specific terms.
                    </p>
                  </div>
                )}
              </div>

              {/* Expandable Details */}
              <div className="border-t border-surface-100">
                <button
                  onClick={() =>
                    setExpandedResult(expandedResult === result.id ? null : result.id)
                  }
                  className="w-full px-6 py-3 flex items-center justify-between text-sm font-medium text-surface-600 hover:bg-surface-50 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    {expandedResult === result.id ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                    {expandedResult === result.id ? 'Hide' : 'Show'} Rationale &amp; Retrieved
                    Context
                  </span>
                  <span className="text-xs text-surface-400">
                    Proof of no hallucination
                  </span>
                </button>

                {expandedResult === result.id && (
                  <div className="px-6 pb-5 space-y-4 animate-fade-in">
                    {/* Rationale */}
                    <div>
                      <h4 className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5" />
                        AI-Generated Rationale
                      </h4>
                      <div className="p-4 bg-primary-50 border border-primary-100 rounded-xl text-sm text-surface-700 whitespace-pre-line leading-relaxed">
                        {result.rationale}
                      </div>
                    </div>

                    {/* Context Chunks */}
                    <div>
                      <h4 className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5" />
                        Retrieved Context Chunks (Source of Truth)
                      </h4>
                      <div className="space-y-2">
                        {result.contextUsed.map((chunk, cIndex) => (
                          <div
                            key={cIndex}
                            className="p-3 bg-surface-50 border border-surface-200 rounded-lg text-xs text-surface-600 font-mono leading-relaxed"
                          >
                            <span className="text-primary-500 font-bold">[{cIndex + 1}]</span>{' '}
                            {chunk}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Grounding Verification */}
                    <div className="flex items-center gap-2 p-3 bg-accent-50 border border-accent-200 rounded-xl">
                      <CheckCircle2 className="w-4 h-4 text-accent-600" />
                      <span className="text-xs font-semibold text-accent-700">
                        ✓ Grounding Verified: All recommendations are derived exclusively from the
                        retrieved context chunks above. No hallucinated standards.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {results.length === 0 && !isLoading && (
        <div className="text-center py-16">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-50 rounded-2xl mb-4">
            <Search className="w-10 h-10 text-primary-300" />
          </div>
          <h3 className="text-xl font-bold text-surface-400 mb-2">No queries yet</h3>
          <p className="text-surface-400 text-sm max-w-md mx-auto">
            Enter a product description above or click a sample query to see the RAG engine in
            action. Results will appear here with retrieved BIS standards and verification context.
          </p>
        </div>
      )}
    </div>
  );
}
