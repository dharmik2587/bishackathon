import { useState } from 'react';
import {
  Target,
  TrendingUp,
  Clock,
  Shield,
  Play,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  BarChart3,
  Zap,
  FileCheck,
} from 'lucide-react';
import { simulateRAGQuery, calculateMetrics, sampleQueries } from '../data/standards';
import { QueryResult, EvaluationMetrics } from '../types';

function MetricCard({
  icon: Icon,
  label,
  value,
  target,
  unit,
  color,
  delay,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  target: string;
  unit: string;
  color: 'blue' | 'green' | 'amber' | 'purple';
  delay: number;
}) {
  const colorMap = {
    blue: {
      iconBg: 'bg-primary-100',
      iconText: 'text-primary-600',
      valueText: 'text-primary-700',
      border: 'border-primary-100',
      glow: 'shadow-primary-100',
    },
    green: {
      iconBg: 'bg-accent-100',
      iconText: 'text-accent-600',
      valueText: 'text-accent-600',
      border: 'border-accent-100',
      glow: 'shadow-accent-100',
    },
    amber: {
      iconBg: 'bg-amber-100',
      iconText: 'text-amber-600',
      valueText: 'text-amber-700',
      border: 'border-amber-100',
      glow: 'shadow-amber-100',
    },
    purple: {
      iconBg: 'bg-purple-100',
      iconText: 'text-purple-600',
      valueText: 'text-purple-700',
      border: 'border-purple-100',
      glow: 'shadow-purple-100',
    },
  };
  const c = colorMap[color];

  return (
    <div
      className={`bg-white rounded-2xl shadow-md border ${c.border} p-5 animate-fade-in relative overflow-hidden`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-5 -mr-6 -mt-6 bg-gradient-to-br from-current to-transparent" />
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2.5 rounded-xl ${c.iconBg}`}>
          <Icon className={`w-5 h-5 ${c.iconText}`} />
        </div>
        <span className="text-xs font-medium text-surface-400 bg-surface-50 px-2 py-1 rounded-full">
          Target: {target}
        </span>
      </div>
      <div className={`text-3xl font-black ${c.valueText} mb-1 animate-count-up`}>{value}</div>
      <div className="text-sm font-medium text-surface-500">{label}</div>
      <div className="text-xs text-surface-400 mt-1">{unit}</div>
    </div>
  );
}

export default function Dashboard() {
  const [isRunning, setIsRunning] = useState(false);
  const [batchResults, setBatchResults] = useState<QueryResult[]>([]);
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [progress, setProgress] = useState(0);

  const runBatchEvaluation = async () => {
    setIsRunning(true);
    setBatchResults([]);
    setMetrics(null);
    setProgress(0);

    const results: QueryResult[] = [];

    for (let i = 0; i < sampleQueries.length; i++) {
      const sq = sampleQueries[i];
      try {
        const result = await simulateRAGQuery(sq.query, sq.id);
        results.push(result);
      } catch {
        // Fallback: never crash
        results.push({
          id: sq.id,
          query: sq.query,
          retrievedStandards: [],
          rationale: 'Query processing failed. Returning empty fallback.',
          contextUsed: [],
          latencySeconds: 0,
          timestamp: Date.now(),
        });
      }
      setBatchResults([...results]);
      setProgress(((i + 1) / sampleQueries.length) * 100);
    }

    const calculatedMetrics = calculateMetrics(results);
    setMetrics(calculatedMetrics);
    setIsRunning(false);
  };

  return (
    <div className="space-y-8">
      {/* Batch Evaluation Control */}
      <div className="bg-white rounded-2xl shadow-lg border border-surface-200 overflow-hidden">
        <div className="bg-gradient-to-r from-surface-800 via-surface-700 to-surface-600 px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-white/10 rounded-lg">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-xl font-bold text-white">Automated Batch Evaluation</h2>
              </div>
              <p className="text-surface-300 text-sm">
                Run all sample queries to simulate the automated evaluation pipeline
              </p>
            </div>
            <button
              onClick={runBatchEvaluation}
              disabled={isRunning}
              className="px-6 py-3 bg-accent-500 text-white rounded-xl font-semibold hover:bg-accent-600 disabled:opacity-70 transition-all flex items-center gap-2 shadow-lg"
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Running ({Math.round(progress)}%)
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Run Evaluation
                </>
              )}
            </button>
          </div>

          {/* Progress Bar */}
          {(isRunning || batchResults.length > 0) && (
            <div className="mt-4">
              <div className="h-2 bg-surface-600 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-accent-400 to-accent-500 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-surface-400">
                  {batchResults.length}/{sampleQueries.length} queries completed
                </span>
                <span className="text-xs text-surface-400">
                  {isRunning ? 'Processing...' : 'Complete'}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Metrics Dashboard */}
      {metrics && (
        <div>
          <h3 className="text-lg font-bold text-surface-800 mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-primary-600" />
            Evaluation Metrics
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              icon={Target}
              label="Hit Rate @3"
              value={`${metrics.hitRateAt3}%`}
              target=">80%"
              unit="Percentage of queries with correct standard in top 3"
              color="blue"
              delay={0}
            />
            <MetricCard
              icon={TrendingUp}
              label="MRR @5"
              value={metrics.mrrAt5.toFixed(3)}
              target=">0.700"
              unit="Mean Reciprocal Rank across top 5 results"
              color="green"
              delay={100}
            />
            <MetricCard
              icon={Clock}
              label="Average Latency"
              value={`${metrics.avgLatency}s`}
              target="<5.0s"
              unit="End-to-end processing time per query"
              color="amber"
              delay={200}
            />
            <MetricCard
              icon={Shield}
              label="No Hallucination"
              value={`${metrics.noHallucinationRate}%`}
              target="100%"
              unit="Strict grounding in retrieved context"
              color="purple"
              delay={300}
            />
          </div>
        </div>
      )}

      {/* Individual Query Results from Batch */}
      {batchResults.length > 0 && (
        <div>
          <h3 className="text-lg font-bold text-surface-800 mb-4 flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-primary-600" />
            Individual Query Results
          </h3>
          <div className="bg-white rounded-2xl shadow-md border border-surface-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-surface-50 border-b border-surface-200">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-surface-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-surface-500 uppercase tracking-wider">
                      Query
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-surface-500 uppercase tracking-wider">
                      Retrieved Standards
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-surface-500 uppercase tracking-wider">
                      Latency
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-surface-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {batchResults.map((result, index) => (
                    <tr
                      key={result.id}
                      className="border-b border-surface-100 hover:bg-surface-50 transition-colors animate-fade-in"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <td className="px-4 py-3">
                        <span className="text-xs font-mono font-bold text-primary-600 bg-primary-50 px-2 py-1 rounded">
                          {result.id}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-sm text-surface-700 max-w-xs truncate">
                          {result.query}
                        </p>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {result.retrievedStandards.length > 0 ? (
                            result.retrievedStandards.slice(0, 3).map((s) => (
                              <span
                                key={s.id}
                                className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-50 text-primary-700 text-xs font-medium rounded-full border border-primary-100"
                              >
                                {s.standardNumber}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-amber-500 flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3" /> None found
                            </span>
                          )}
                          {result.retrievedStandards.length > 3 && (
                            <span className="text-xs text-surface-400">
                              +{result.retrievedStandards.length - 3} more
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="flex items-center gap-1.5 text-xs font-mono">
                          <Zap className="w-3 h-3 text-amber-500" />
                          <span
                            className={
                              result.latencySeconds < 3
                                ? 'text-accent-600 font-semibold'
                                : result.latencySeconds < 5
                                  ? 'text-amber-600'
                                  : 'text-red-600'
                            }
                          >
                            {result.latencySeconds}s
                          </span>
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {result.retrievedStandards.length > 0 ? (
                          <span className="inline-flex items-center gap-1 text-xs font-medium text-accent-600 bg-accent-50 px-2 py-1 rounded-full">
                            <CheckCircle2 className="w-3 h-3" /> Success
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
                            <AlertTriangle className="w-3 h-3" /> No results
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {batchResults.length === 0 && !isRunning && (
        <div className="text-center py-16">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-surface-100 rounded-2xl mb-4">
            <BarChart3 className="w-10 h-10 text-surface-300" />
          </div>
          <h3 className="text-xl font-bold text-surface-400 mb-2">No evaluation data yet</h3>
          <p className="text-surface-400 text-sm max-w-md mx-auto">
            Click "Run Evaluation" above to process all {sampleQueries.length} sample queries
            through the RAG pipeline and see comprehensive metrics.
          </p>
        </div>
      )}
    </div>
  );
}
