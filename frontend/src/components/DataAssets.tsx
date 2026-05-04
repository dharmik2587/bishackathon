import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const assets = [
  {
    filename: 'standards.json',
    path: 'public/',
    label: 'RAW STANDARDS',
    desc: 'The complete Bureau of Indian Standards dataset. Contains all standard codes, titles, and domain classifications used by the RAG engine.',
    size: 'Primary Dataset',
    color: '#00d4aa',
    lines: ['{ "code": "IS 456",', '  "title": "Plain and RC",', '  "domain": "Civil" }'],
  },
  {
    filename: 'standards_enriched.json',
    path: 'public/',
    label: 'BM25-READY CORPUS',
    desc: 'Preprocessed and tokenized version of the standards dataset. Cleaned, normalized, and optimized for BM25 term-frequency matching.',
    size: 'Processed Dataset',
    color: '#1a8cff',
    lines: ['{ "tokens": [...],', '  "bm25_score": 0.94,', '  "domain_tags": [...] }'],
  },
  {
    filename: 'public_test_set.json',
    path: 'data/',
    label: 'PUBLIC TEST QUERIES',
    desc: 'Publicly provided evaluation queries for the BIS Hackathon. Used to validate retrieval accuracy and tune the pipeline parameters.',
    size: 'Evaluation Set',
    color: '#00d4aa',
    lines: ['{ "query": "rebar specs",', '  "expected": "IS 1786",', '  "domain": "Civil" }'],
  },
  {
    filename: 'private_data_set.json',
    path: 'data/',
    label: 'PRIVATE EVAL DATASET',
    desc: 'Private evaluation dataset used for final benchmarking. Achieved 66.67% Hit Rate @3 and 0.6467 MRR @5 on this dataset.',
    size: 'Benchmark Dataset',
    color: '#1a8cff',
    lines: ['// Private dataset', '// Hit Rate @3: 66.67%', '// MRR @5: 0.6467'],
  },
];

export default function DataAssets() {
  const sectionRef = useRef<HTMLElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(titleRef.current,
        { opacity: 0, y: 60 },
        { opacity: 1, y: 0, duration: 1, ease: 'power3.out',
          scrollTrigger: { trigger: titleRef.current, start: 'top 85%' } }
      );

      if (gridRef.current) {
        gsap.fromTo(
          Array.from(gridRef.current.children),
          { opacity: 0, y: 40 },
          { opacity: 1, y: 0, stagger: 0.15, duration: 0.9, ease: 'power3.out',
            scrollTrigger: { trigger: gridRef.current, start: 'top 80%' } }
        );
      }
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="data" style={{
      padding: 'clamp(80px, 10vw, 140px) clamp(20px, 5vw, 80px)',
      background: '#020b14',
      position: 'relative',
    }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '1px', background: 'linear-gradient(90deg, transparent, #0d2d44, transparent)' }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div ref={titleRef} style={{ marginBottom: '64px', opacity: 0 }}>
          <div className="overline" style={{ marginBottom: '20px' }}>DATA ASSETS</div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(42px, 6vw, 80px)',
            fontWeight: 300,
            color: '#e8f4ff',
            letterSpacing: '-0.01em',
            lineHeight: 1.1,
            marginBottom: '16px',
          }}>The Corpus</h2>
          <p style={{
            fontFamily: 'Inter',
            fontWeight: 300,
            fontSize: '16px',
            color: '#8ab4cc',
          }}>Four datasets powering the entire retrieval pipeline.</p>
        </div>

        {/* Grid */}
        <div ref={gridRef} style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '2px',
          background: '#0d2d44',
        }}>
          {assets.map((a) => (
            <div
              key={a.filename}
              className="card-hover"
              style={{
                background: '#020b14',
                padding: '32px 28px',
                position: 'relative',
                opacity: 0,
                cursor: 'default',
              }}
            >
              {/* Path */}
              <div style={{
                fontFamily: 'Space Grotesk',
                fontSize: '9px',
                letterSpacing: '0.2em',
                color: '#3d6680',
                textTransform: 'uppercase',
                marginBottom: '6px',
              }}>{a.path}</div>

              {/* Filename */}
              <div style={{
                fontFamily: 'Space Grotesk',
                fontSize: '14px',
                fontWeight: 600,
                color: a.color,
                letterSpacing: '0.05em',
                marginBottom: '8px',
              }}>{a.filename}</div>

              {/* Label */}
              <div style={{
                display: 'inline-block',
                border: `1px solid ${a.color}`,
                padding: '3px 10px',
                fontFamily: 'Space Grotesk',
                fontSize: '9px',
                letterSpacing: '0.2em',
                color: a.color,
                textTransform: 'uppercase',
                marginBottom: '18px',
                opacity: 0.7,
              }}>{a.label}</div>

              {/* Description */}
              <p style={{
                fontFamily: 'Inter',
                fontWeight: 300,
                fontSize: '13px',
                color: '#8ab4cc',
                lineHeight: 1.65,
                marginBottom: '20px',
              }}>{a.desc}</p>

              {/* Code preview */}
              <div style={{
                background: '#041120',
                border: '1px solid #0d2d44',
                padding: '12px 14px',
              }}>
                {a.lines.map((line, i) => (
                  <div key={i} style={{
                    fontFamily: 'Space Grotesk',
                    fontSize: '10px',
                    color: i === 0 ? a.color : '#3d6680',
                    letterSpacing: '0.05em',
                    lineHeight: 1.8,
                  }}>{line}</div>
                ))}
              </div>

              {/* Size badge */}
              <div style={{
                position: 'absolute',
                top: '24px',
                right: '24px',
                fontFamily: 'Space Grotesk',
                fontSize: '9px',
                letterSpacing: '0.15em',
                color: '#3d6680',
                textTransform: 'uppercase',
              }}>{a.size}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}