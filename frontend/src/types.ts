export interface BISStandard {
  id: string;
  standardNumber: string;
  title: string;
  category: string;
  section?: string;
  description: string;
  keywords: string[];
  contextChunks: string[];
}

export interface QueryResult {
  id: string;
  query: string;
  retrievedStandards: BISStandard[];
  rationale: string;
  contextUsed: string[];
  latencySeconds: number;
  timestamp: number;
}

export interface EvaluationMetrics {
  hitRateAt3: number;
  mrrAt5: number;
  avgLatency: number;
  noHallucinationRate: number;
  totalQueries: number;
  successfulQueries: number;
}

export interface BatchEvaluation {
  results: QueryResult[];
  metrics: EvaluationMetrics;
  timestamp: number;
}

export type TabId = 'query' | 'dashboard' | 'architecture' | 'batch';
