import { useState, useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { API_ENDPOINTS } from '../config/api';

gsap.registerPlugin(ScrollTrigger);

interface EvalResult {
  id: string;
  query: string;
  expected_standards: string[];
  retrieved_standards: string[];
  rationale: string;
  latency_seconds: number;
}

interface EvalData {
  total_queries: number;
  hit_rate_3: number;
  mrr_5: number;
  avg_latency: number;
  results: EvalResult[];
}

export default function EvaluationDashboard() {
  const [isRunning, setIsRunning] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [data, setData] = useState<EvalData | null>(null);
  const sectionRef = useRef<HTMLElement>(null);
  const tableRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchExistingResults = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(API_ENDPOINTS.results);
        if (!response.ok) throw new Error('Failed to fetch results');
        const result = await response.json();
        if (result.results && result.results.length > 0) {
          setData(result);
          setProgress(100);
        }
      } catch (err) {
        console.error('Failed to fetch existing results:', err);
        setError('Could not connect to the backend. Please ensure the API is running.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchExistingResults();
  }, []);

  const runEvaluation = async () => {
    setIsRunning(true);
    setProgress(0);
    
    // Simulate progress since real eval might take a few seconds
    const progressInterval = setInterval(() => {
      setProgress(prev => (prev < 90 ? prev + 5 : prev));
    }, 200);

    try {
      const response = await fetch(API_ENDPOINTS.evaluate, { method: 'POST' });
      if (!response.ok) throw new Error('Evaluation failed');
      const result = await response.json();
      
      clearInterval(progressInterval);
      setProgress(100);
      setData(result);
      
      setTimeout(() => {
        if (tableRef.current) {
          gsap.fromTo(tableRef.current, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 });
        }
      }, 100);
    } catch (error) {
      console.error('Eval error:', error);
      clearInterval(progressInterval);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <section ref={sectionRef} id="evaluation" style={{
      padding: '80px clamp(20px, 5vw, 80px)',
      background: '#050f1a',
      minHeight: '100vh'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '40px' }}>
          <div className="overline" style={{ marginBottom: '16px' }}>JUDGES PANEL</div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(40px, 5vw, 64px)',
            fontWeight: 300,
            color: '#e8f4ff',
            marginBottom: '12px'
          }}>Evaluation Criteria</h2>
          <p style={{ fontFamily: 'Inter', color: '#8ab4cc', fontSize: '16px' }}>
            Run the automated benchmarking pipeline against the public test set to verify system accuracy and latency.
          </p>
        </div>

        {/* Control Card */}
        {isLoading ? (
          <div style={{ padding: '60px', textAlign: 'center', background: '#061828', border: '1px solid #0d2d44' }}>
            <div style={{ width: '40px', height: '40px', border: '2px solid #00d4aa', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 20px' }} />
            <div style={{ fontFamily: 'Space Grotesk', fontSize: '12px', color: '#8ab4cc', letterSpacing: '0.1em' }}>LOADING ENGINE DATA...</div>
          </div>
        ) : error ? (
          <div style={{ padding: '60px', textAlign: 'center', background: '#061828', border: '1px solid #ff4d4d33' }}>
            <div style={{ color: '#ff4d4d', fontFamily: 'Space Grotesk', fontSize: '14px', marginBottom: '10px' }}>⚠️ {error}</div>
            <button onClick={() => window.location.reload()} style={{ background: '#ff4d4d', color: '#fff', border: 'none', padding: '10px 20px', fontFamily: 'Space Grotesk', fontSize: '10px', cursor: 'pointer' }}>RETRY CONNECTION</button>
          </div>
        ) : (
          <div style={{
            background: '#061828',
            border: '1px solid #0d2d44',
            padding: '40px',
            marginBottom: '40px',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <div>
                <h3 style={{ fontFamily: 'Space Grotesk', fontSize: '18px', color: '#e8f4ff', marginBottom: '8px' }}>Automated Batch Evaluation</h3>
                <p style={{ fontFamily: 'Inter', fontSize: '14px', color: '#3d6680' }}>
                  Processes all 200+ queries from the public test set.
                </p>
              </div>
              <button 
                onClick={runEvaluation}
                disabled={isRunning}
                style={{
                  background: isRunning ? 'transparent' : '#00d4aa',
                  border: '1px solid #00d4aa',
                  color: isRunning ? '#00d4aa' : '#020b14',
                  padding: '16px 40px',
                  fontFamily: 'Space Grotesk',
                  fontSize: '12px',
                  fontWeight: 600,
                  letterSpacing: '0.1em',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}
              >
                {isRunning ? (
                  <>
                    <div style={{ width: '12px', height: '12px', border: '2px solid #00d4aa', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                    RUNNING...
                  </>
                ) : 'RUN EVALUATION'}
              </button>
            </div>

            <div style={{ height: '4px', background: '#0d2d44', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ 
                height: '100%', 
                width: `${progress}%`, 
                background: '#00d4aa', 
                transition: 'width 0.3s ease' 
              }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px' }}>
              <span style={{ fontFamily: 'Space Grotesk', fontSize: '10px', color: '#3d6680' }}>{progress}% COMPLETE</span>
              <span style={{ fontFamily: 'Space Grotesk', fontSize: '10px', color: '#3d6680' }}>STATUS: {isRunning ? 'PROCESSING QUERIES' : progress === 100 ? 'EVALUATION COMPLETE' : 'IDLE'}</span>
            </div>
          </div>
        )}

        {/* Metrics Row */}
        {data && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', 
            gap: '20px',
            marginBottom: '40px'
          }}>
            {[
              { label: 'Hit Rate @3', value: `${data.hit_rate_3}%`, desc: 'Target: >80%', color: '#00d4aa' },
              { label: 'MRR @5', value: data.mrr_5.toFixed(4), desc: 'Target: >0.70', color: '#1a8cff' },
              { label: 'Avg Latency', value: `${data.avg_latency}s`, desc: 'Target: <5.0s', color: '#00d4aa' },
              { label: 'Total Queries', value: data.total_queries, desc: 'Verified set', color: '#1a8cff' }
            ].map((m, i) => (
              <div key={i} style={{
                background: '#061828',
                border: '1px solid #0d2d44',
                padding: '32px',
                textAlign: 'center'
              }}>
                <div style={{ fontFamily: 'Space Grotesk', fontSize: '10px', color: '#3d6680', letterSpacing: '0.1em', marginBottom: '16px' }}>{m.label.toUpperCase()}</div>
                <div style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '48px', color: m.color, lineHeight: 1, marginBottom: '8px' }}>{m.value}</div>
                <div style={{ fontFamily: 'Inter', fontSize: '12px', color: '#3d6680' }}>{m.desc}</div>
              </div>
            ))}
          </div>
        )}

        {/* Results Table */}
        {data && (
          <div ref={tableRef} style={{ 
            background: '#061828', 
            border: '1px solid #0d2d44',
            overflow: 'hidden'
          }}>
            <div style={{ padding: '24px', borderBottom: '1px solid #0d2d44', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4 style={{ fontFamily: 'Space Grotesk', fontSize: '14px', color: '#e8f4ff' }}>Individual Query Results</h4>
              <span style={{ fontFamily: 'Space Grotesk', fontSize: '10px', color: '#3d6680' }}>SHOWING {data.results.length} ENTRIES</span>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#041120', borderBottom: '1px solid #0d2d44' }}>
                    <th style={{ padding: '16px 24px', fontFamily: 'Space Grotesk', fontSize: '11px', color: '#3d6680', fontWeight: 600 }}>ID</th>
                    <th style={{ padding: '16px 24px', fontFamily: 'Space Grotesk', fontSize: '11px', color: '#3d6680', fontWeight: 600 }}>QUERY</th>
                    <th style={{ padding: '16px 24px', fontFamily: 'Space Grotesk', fontSize: '11px', color: '#3d6680', fontWeight: 600 }}>RETRIEVED</th>
                    <th style={{ padding: '16px 24px', fontFamily: 'Space Grotesk', fontSize: '11px', color: '#3d6680', fontWeight: 600 }}>LATENCY</th>
                  </tr>
                </thead>
                <tbody>
                  {data.results.map((res, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #0d2d44' }}>
                      <td style={{ padding: '16px 24px', fontFamily: 'Space Grotesk', fontSize: '12px', color: '#1a8cff' }}>
                        {res.id ? res.id.toString().slice(-4).toUpperCase() : `Q${i+1}`}
                      </td>
                      <td style={{ padding: '16px 24px', fontFamily: 'Inter', fontSize: '13px', color: '#e8f4ff', maxWidth: '400px' }}>{res.query}</td>
                      <td style={{ padding: '16px 24px' }}>
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          {res.retrieved_standards.slice(0, 3).map((std, si) => (
                            <span key={si} style={{ 
                              padding: '2px 8px', 
                              background: '#041120', 
                              border: '1px solid #0d2d44', 
                              fontFamily: 'Space Grotesk', 
                              fontSize: '10px', 
                              color: '#00d4aa' 
                            }}>{std}</span>
                          ))}
                          {res.retrieved_standards.length > 3 && (
                            <span style={{ fontFamily: 'Space Grotesk', fontSize: '10px', color: '#3d6680' }}>+{res.retrieved_standards.length - 3} more</span>
                          )}
                        </div>
                      </td>
                      <td style={{ padding: '16px 24px', fontFamily: 'Space Grotesk', fontSize: '12px', color: '#8ab4cc' }}>{res.latency_seconds}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </section>
  );
}
