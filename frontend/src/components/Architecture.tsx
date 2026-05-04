import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const techStack = [
  {
    layer: 'BACKEND',
    title: 'Python 3.11 Inference Engine',
    desc: 'Core RAG pipeline handling multi-stage retrieval. Runs rank-bm25, direct mapping, and DeepSeek LLM fallback in a single optimized call stack.',
    tags: ['Python 3.11', 'rank-bm25', 'openai SDK'],
    color: '#00d4aa',
  },
  {
    layer: 'FRONTEND',
    title: 'React 19 + Vite Dashboard',
    desc: 'Blazing-fast search interface built with TypeScript, Tailwind CSS 4.0, and React 19. Zero-latency UI with live standard results.',
    tags: ['React 19', 'Vite', 'TypeScript', 'Tailwind 4'],
    color: '#1a8cff',
  },
  {
    layer: 'DATA LAYER',
    title: 'Enriched BIS Standards Corpus',
    desc: 'Preprocessed standards_enriched.json corpus with BM25-ready tokenization. Supports direct keyword mappings for 50+ technical domains.',
    tags: ['standards.json', 'BM25 Index', 'TF-IDF'],
    color: '#00d4aa',
  },
  {
    layer: 'AI LAYER',
    title: 'DeepSeek LLM Fallback',
    desc: 'OpenAI-compatible API integration with intelligent query expansion. Handles ambiguous queries that BM25 cannot resolve with confidence.',
    tags: ['DeepSeek', 'Query Rewrite', 'LLM Fallback'],
    color: '#1a8cff',
  },
];

export default function Architecture() {
  const sectionRef = useRef<HTMLElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const leftRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(titleRef.current,
        { opacity: 0, y: 60 },
        { opacity: 1, y: 0, duration: 1, ease: 'power3.out',
          scrollTrigger: { trigger: titleRef.current, start: 'top 85%' } }
      );

      if (leftRef.current) {
        gsap.fromTo(
          Array.from(leftRef.current.children),
          { opacity: 0, x: -40 },
          { opacity: 1, x: 0, stagger: 0.15, duration: 0.9, ease: 'power3.out',
            scrollTrigger: { trigger: leftRef.current, start: 'top 80%' } }
        );
      }

      gsap.fromTo(rightRef.current,
        { opacity: 0, x: 40 },
        { opacity: 1, x: 0, duration: 1, ease: 'power3.out',
          scrollTrigger: { trigger: rightRef.current, start: 'top 80%' } }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="architecture" style={{
      padding: 'clamp(80px, 10vw, 140px) clamp(20px, 5vw, 80px)',
      background: 'linear-gradient(180deg, #041120 0%, #020b14 100%)',
      position: 'relative',
    }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '1px', background: 'linear-gradient(90deg, transparent, #0d2d44, transparent)' }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div ref={titleRef} style={{ marginBottom: '72px', opacity: 0 }}>
          <div className="overline" style={{ marginBottom: '20px' }}>TECH STACK</div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
            fontSize: 'clamp(42px, 6vw, 80px)',
            fontWeight: 300,
            color: '#e8f4ff',
            letterSpacing: '-0.01em',
            lineHeight: 1.1,
          }}>Architecture</h2>
        </div>

        {/* Two column layout */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '64px',
          alignItems: 'start',
        }}
          className="arch-grid"
        >
          {/* Left: Tech stack */}
          <div ref={leftRef} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {techStack.map((t) => (
              <div key={t.layer} style={{
                padding: '28px 28px',
                background: '#061828',
                border: '1px solid #0d2d44',
                position: 'relative',
                transition: 'border-color 0.3s ease',
                opacity: 0,
              }}
                onMouseEnter={e => (e.currentTarget.style.borderColor = t.color)}
                onMouseLeave={e => (e.currentTarget.style.borderColor = '#0d2d44')}
              >
                <div style={{
                  fontFamily: 'Space Grotesk',
                  fontSize: '9px',
                  letterSpacing: '0.3em',
                  color: t.color,
                  textTransform: 'uppercase',
                  marginBottom: '8px',
                }}>{t.layer}</div>
                <div style={{
                  fontFamily: 'Cormorant Garamond, serif',
                  fontSize: '22px',
                  fontWeight: 400,
                  color: '#e8f4ff',
                  marginBottom: '10px',
                }}>{t.title}</div>
                <p style={{
                  fontFamily: 'Inter',
                  fontWeight: 300,
                  fontSize: '13px',
                  color: '#8ab4cc',
                  lineHeight: 1.65,
                  marginBottom: '16px',
                }}>{t.desc}</p>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {t.tags.map(tag => (
                    <span key={tag} style={{
                      fontFamily: 'Space Grotesk',
                      fontSize: '10px',
                      letterSpacing: '0.1em',
                      color: '#3d6680',
                      background: '#041120',
                      border: '1px solid #0d2d44',
                      padding: '3px 10px',
                    }}>{tag}</span>
                  ))}
                </div>
                <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '2px', background: `linear-gradient(to bottom, ${t.color}, transparent)`, opacity: 0.5 }} />
              </div>
            ))}
          </div>

          {/* Right: Node diagram */}
          <div ref={rightRef} style={{ opacity: 0, position: 'sticky', top: '100px' }}>
            <div style={{
              background: '#061828',
              border: '1px solid #0d2d44',
              padding: '40px',
            }}>
              <div style={{
                fontFamily: 'Space Grotesk',
                fontSize: '10px',
                letterSpacing: '0.25em',
                color: '#3d6680',
                textTransform: 'uppercase',
                marginBottom: '32px',
              }}>SYSTEM FLOW DIAGRAM</div>

              <svg width="100%" viewBox="0 0 300 480" fill="none">
                {/* Nodes */}
                {[
                  { x: 150, y: 40, label: 'QUERY INPUT', color: '#00d4aa' },
                  { x: 150, y: 130, label: 'DIRECT MAP', color: '#1a8cff' },
                  { x: 60, y: 240, label: 'BM25', color: '#1a8cff' },
                  { x: 240, y: 240, label: 'MATCH?', color: '#00d4aa' },
                  { x: 150, y: 340, label: 'LLM REWRITE', color: '#00d4aa' },
                  { x: 150, y: 430, label: 'RESULT', color: '#00d4aa' },
                ].map((node, i) => (
                  <g key={i}>
                    <rect
                      x={node.x - 44}
                      y={node.y - 18}
                      width="88"
                      height="36"
                      fill="#020b14"
                      stroke={node.color}
                      strokeWidth="1"
                      opacity="0.9"
                    />
                    <text
                      x={node.x}
                      y={node.y + 5}
                      textAnchor="middle"
                      fill={node.color}
                      fontSize="9"
                      fontFamily="Space Grotesk"
                      letterSpacing="1.5"
                    >{node.label}</text>
                  </g>
                ))}

                {/* Connectors */}
                <line x1="150" y1="58" x2="150" y2="112" stroke="#1a4a66" strokeWidth="1" strokeDasharray="3 3"/>
                <polygon points="146,112 154,112 150,122" fill="#1a4a66"/>
                <line x1="110" y1="148" x2="70" y2="222" stroke="#1a4a66" strokeWidth="1" strokeDasharray="3 3"/>
                <line x1="190" y1="148" x2="230" y2="222" stroke="#1a4a66" strokeWidth="1" strokeDasharray="3 3"/>
                <line x1="110" y1="258" x2="106" y2="322" stroke="#1a4a66" strokeWidth="1" strokeDasharray="3 3"/>
                <line x1="240" y1="258" x2="196" y2="322" stroke="#1a4a66" strokeWidth="1" strokeDasharray="3 3"/>
                <line x1="150" y1="358" x2="150" y2="412" stroke="#00d4aa" strokeWidth="1" strokeDasharray="3 3"/>
                <polygon points="146,412 154,412 150,422" fill="#00d4aa"/>

                {/* Labels */}
                <text x="78" y="196" fill="#3d6680" fontSize="8" fontFamily="Space Grotesk">LOW CONF.</text>
                <text x="218" y="196" fill="#3d6680" fontSize="8" fontFamily="Space Grotesk">HIGH CONF.</text>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .arch-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </section>
  );
}
