import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const demoResults: Record<string, { code: string; title: string; domain: string; confidence: number; stage: string }[]> = {
  'rebar': [
    { code: 'IS 1786', title: 'High Strength Deformed Steel Bars & Wires for Concrete Reinforcement', domain: 'Civil', confidence: 98, stage: 'Direct Map' },
    { code: 'IS 432', title: 'Mild Steel and Medium Tensile Steel Bars', domain: 'Civil', confidence: 84, stage: 'BM25' },
    { code: 'IS 2502', title: 'Code of Practice for Bending and Fixing of Bars', domain: 'Civil', confidence: 71, stage: 'BM25' },
  ],
  'electrical wiring': [
    { code: 'IS 732', title: 'Code of Practice for Electrical Wiring Installations', domain: 'Electrical', confidence: 97, stage: 'Direct Map' },
    { code: 'IS 694', title: 'PVC Insulated Cables for Working Voltages up to and including 1100V', domain: 'Electrical', confidence: 88, stage: 'BM25' },
    { code: 'IS 8130', title: 'Conductors for Insulated Electric Cables', domain: 'Electrical', confidence: 72, stage: 'BM25' },
  ],
  'cement concrete': [
    { code: 'IS 456', title: 'Plain and Reinforced Concrete Code of Practice', domain: 'Civil', confidence: 99, stage: 'Direct Map' },
    { code: 'IS 383', title: 'Specification for Coarse and Fine Aggregates', domain: 'Civil', confidence: 85, stage: 'BM25' },
    { code: 'IS 10262', title: 'Concrete Mix Proportioning Guidelines', domain: 'Civil', confidence: 78, stage: 'BM25' },
  ],
  'fire safety': [
    { code: 'IS 2189', title: 'Selection, Installation and Maintenance of Automatic Fire Detection', domain: 'Safety', confidence: 93, stage: 'BM25' },
    { code: 'IS 15105', title: 'Dry Chemical Powder Type Fire Extinguishers', domain: 'Safety', confidence: 81, stage: 'LLM Rewrite' },
    { code: 'IS 16009', title: 'Code of Practice for Fire Detection and Alarm Systems', domain: 'Safety', confidence: 69, stage: 'LLM Rewrite' },
  ],
};

const suggestions = ['rebar', 'electrical wiring', 'cement concrete', 'fire safety'];

export default function SearchDemo() {
  const sectionRef = useRef<HTMLElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[] | null>(null);
  const [rationale, setRationale] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(titleRef.current,
        { opacity: 0, y: 60 },
        { opacity: 1, y: 0, duration: 1, ease: 'power3.out',
          scrollTrigger: { trigger: titleRef.current, start: 'top 85%' } }
      );
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  const handleSearch = async (q: string) => {
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;

    setLoading(true);
    setSearched(true);
    setResults(null);
    setRationale(null);

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, top_k: 5 }),
      });
      
      if (!response.ok) throw new Error('Search failed');
      
      const data = await response.json();
      setResults(data.retrieved_standards);
      setRationale(data.rationale);
      
      setTimeout(() => {
        if (resultsRef.current) {
          gsap.fromTo(
            Array.from(resultsRef.current.children),
            { opacity: 0, x: -20 },
            { opacity: 1, x: 0, stagger: 0.12, duration: 0.6, ease: 'power3.out' }
          );
        }
      }, 50);
    } catch (error) {
      console.error('Error fetching standards:', error);
    } finally {
      setLoading(false);
    }
  };

  const stageColor = (stage: string) => {
    if (stage === 'Direct Map') return '#00d4aa';
    if (stage === 'BM25') return '#1a8cff';
    return '#8b6cff';
  };

  return (
    <section ref={sectionRef} style={{
      padding: 'clamp(80px, 10vw, 140px) clamp(20px, 5vw, 80px)',
      background: '#020b14',
      position: 'relative',
    }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '1px', background: 'linear-gradient(90deg, transparent, #00d4aa44, transparent)' }} />

      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        {/* Header */}
        <div ref={titleRef} style={{ marginBottom: '56px', opacity: 0, textAlign: 'center' }}>
          <div className="overline" style={{ marginBottom: '20px' }}>LIVE DEMO</div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(42px, 6vw, 76px)',
            fontWeight: 300,
            color: '#e8f4ff',
            letterSpacing: '-0.01em',
            lineHeight: 1.1,
            marginBottom: '16px',
          }}>Try the Engine</h2>
          <p style={{
            fontFamily: 'Inter',
            fontWeight: 300,
            fontSize: '16px',
            color: '#8ab4cc',
          }}>Search any engineering term and see BIS standards retrieved in real time.</p>
        </div>

        {/* Search box */}
        <div style={{
          display: 'flex',
          gap: '0',
          marginBottom: '20px',
          border: '1px solid #0d2d44',
          background: '#061828',
          transition: 'border-color 0.3s ease',
        }}
          onFocus={() => { }}
        >
          <div style={{ padding: '18px 20px', display: 'flex', alignItems: 'center' }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="7" cy="7" r="5" stroke="#3d6680" strokeWidth="1.5"/>
              <path d="M11 11 L15 15" stroke="#3d6680" strokeWidth="1.5" strokeLinecap="square"/>
            </svg>
          </div>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch('')}
            placeholder="Search BIS standards — e.g. 'rebar', 'electrical wiring', 'cement'"
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontFamily: 'Inter',
              fontWeight: 300,
              fontSize: '15px',
              color: '#e8f4ff',
              padding: '18px 0',
            }}
          />
          <button
            className="btn-primary"
            onClick={() => handleSearch('')}
            style={{ margin: '8px', padding: '10px 28px', fontSize: '10px' }}
          >
            SEARCH
          </button>
        </div>

        {/* Suggestions */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '40px' }}>
          <span style={{ fontFamily: 'Space Grotesk', fontSize: '10px', color: '#3d6680', letterSpacing: '0.15em', paddingTop: '6px' }}>TRY:</span>
          {suggestions.map(s => (
            <button
              key={s}
              onClick={() => { setQuery(s); handleSearch(s); }}
              style={{
                background: 'transparent',
                border: '1px solid #0d2d44',
                padding: '5px 14px',
                fontFamily: 'Space Grotesk',
                fontSize: '11px',
                color: '#8ab4cc',
                letterSpacing: '0.1em',
                cursor: 'none',
                transition: 'border-color 0.3s, color 0.3s',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#00d4aa'; e.currentTarget.style.color = '#00d4aa'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = '#0d2d44'; e.currentTarget.style.color = '#8ab4cc'; }}
            >{s}</button>
          ))}
        </div>

        {/* Results */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <div style={{
              width: '40px', height: '40px',
              border: '1px solid #0d2d44',
              borderTop: '1px solid #00d4aa',
              borderRadius: '50%',
              margin: '0 auto 16px',
              animation: 'spin 0.8s linear infinite',
            }} />
            <div style={{ fontFamily: 'Space Grotesk', fontSize: '10px', letterSpacing: '0.25em', color: '#3d6680' }}>RETRIEVING STANDARDS...</div>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        )}

        {results && !loading && (
          <div ref={resultsRef} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {rationale && (
              <div style={{
                background: 'rgba(26, 140, 255, 0.05)',
                border: '1px solid rgba(26, 140, 255, 0.2)',
                padding: '24px',
                marginBottom: '20px',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  position: 'absolute',
                  top: 0, left: 0, width: '2px', height: '100%',
                  background: '#1a8cff'
                }} />
                <h5 style={{
                  fontFamily: 'Space Grotesk',
                  fontSize: '10px',
                  fontWeight: 600,
                  color: '#1a8cff',
                  letterSpacing: '0.2em',
                  textTransform: 'uppercase',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                  Expert Rationale
                </h5>
                <p style={{
                  fontFamily: 'Inter',
                  fontSize: '14px',
                  color: '#e8f4ff',
                  lineHeight: 1.6,
                  fontStyle: 'italic'
                }}>{rationale}</p>
              </div>
            )}
            
            <div style={{
              fontFamily: 'Space Grotesk',
              fontSize: '10px',
              letterSpacing: '0.2em',
              color: '#3d6680',
              marginBottom: '16px', 
              textTransform: 'uppercase'
            }}>TOP RETRIEVED STANDARDS</div>

            {results.map((res, i) => (
              <div key={i} style={{
                background: '#061828',
                border: '1px solid #0d2d44',
                padding: '24px',
                marginBottom: '12px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '24px',
                position: 'relative'
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{
                      fontFamily: 'Space Grotesk',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: '#00d4aa',
                      letterSpacing: '0.05em'
                    }}>{res.standardNumber || res.code}</span>
                    <span style={{
                      fontSize: '9px',
                      fontFamily: 'Space Grotesk',
                      padding: '2px 8px',
                      border: '1px solid #1a8cff44',
                      color: '#1a8cff',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>{res.category || res.domain}</span>
                  </div>
                  <h4 style={{
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: '22px',
                    color: '#e8f4ff',
                    marginBottom: '8px',
                    fontWeight: 300
                  }}>{res.title}</h4>
                  <p style={{
                    fontFamily: 'Inter',
                    fontSize: '14px',
                    color: '#8ab4cc',
                    lineHeight: '1.6',
                    fontWeight: 300
                  }}>{res.description || res.title}</p>
                </div>
                
                <div style={{ textAlign: 'right', minWidth: '80px' }}>
                  <div style={{
                    fontFamily: 'Space Grotesk',
                    fontSize: '20px',
                    color: '#00d4aa',
                    fontWeight: 300,
                    marginBottom: '4px'
                  }}>#0{i+1}</div>
                  <div style={{
                    fontFamily: 'Space Grotesk',
                    fontSize: '9px',
                    color: '#3d6680',
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase'
                  }}>Rank</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!searched && !loading && (
          <div style={{
            textAlign: 'center',
            padding: '60px 0',
            border: '1px solid #0d2d44',
            background: '#041120',
          }}>
            <div style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '24px', fontWeight: 300, color: '#3d6680', marginBottom: '8px' }}>
              Ready to retrieve.
            </div>
            <div style={{ fontFamily: 'Space Grotesk', fontSize: '10px', letterSpacing: '0.2em', color: '#1a4a66' }}>
              ENTER A QUERY ABOVE TO BEGIN
            </div>
          </div>
        )}
      </div>
    </section>
  );
}