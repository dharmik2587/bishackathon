import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const stages = [
  {
    num: '01',
    title: 'Direct Mapping',
    subtitle: 'Instant precision lookup',
    desc: 'Immediate lookup for high-confidence technical terms. Hardcoded domain expansions for civil, electrical, and mechanical engineering ensure lightning-fast retrieval for known patterns.',
    badge: '~0.001s',
    badgeLabel: 'LATENCY',
    color: '#00d4aa',
    icon: (
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
        <path d="M4 14 L14 4 L24 14" stroke="#00d4aa" strokeWidth="1.5" strokeLinecap="square"/>
        <path d="M14 4 L14 24" stroke="#00d4aa" strokeWidth="1.5" strokeLinecap="square"/>
        <rect x="9" y="18" width="10" height="6" stroke="#00d4aa" strokeWidth="1.5"/>
      </svg>
    ),
  },
  {
    num: '02',
    title: 'BM25 Retrieval',
    subtitle: 'Term-frequency intelligence',
    desc: 'Fast, robust term-frequency matching using rank-bm25. Scans the enriched BIS standards corpus with precision scoring — surfacing the most relevant standards from thousands of entries.',
    badge: 'TF-IDF',
    badgeLabel: 'METHOD',
    color: '#1a8cff',
    icon: (
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
        <circle cx="12" cy="12" r="8" stroke="#1a8cff" strokeWidth="1.5"/>
        <path d="M18 18 L24 24" stroke="#1a8cff" strokeWidth="1.5" strokeLinecap="square"/>
        <path d="M9 12 L15 12 M12 9 L12 15" stroke="#1a8cff" strokeWidth="1.5" strokeLinecap="square"/>
      </svg>
    ),
  },
  {
    num: '03',
    title: 'LLM Query Rewrite',
    subtitle: 'AI-powered fallback',
    desc: 'When retrieval confidence is low, DeepSeek LLM intelligently expands and rewrites the query — bridging semantic gaps to surface the optimal BIS standard through intelligent reasoning.',
    badge: 'DEEPSEEK',
    badgeLabel: 'ENGINE',
    color: '#00d4aa',
    icon: (
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
        <path d="M14 4 C7 4 4 9 4 14 C4 20 9 24 14 24 C19 24 24 20 24 14" stroke="#00d4aa" strokeWidth="1.5" strokeLinecap="square"/>
        <path d="M20 4 L24 4 L24 8" stroke="#00d4aa" strokeWidth="1.5" strokeLinecap="square"/>
        <path d="M14 10 L14 18 M10 14 L18 14" stroke="#00d4aa" strokeWidth="1" strokeLinecap="square" strokeDasharray="2 2"/>
      </svg>
    ),
  },
];

export default function Pipeline() {
  const sectionRef = useRef<HTMLElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(titleRef.current,
        { opacity: 0, y: 60 },
        {
          opacity: 1, y: 0, duration: 1, ease: 'power3.out',
          scrollTrigger: { trigger: titleRef.current, start: 'top 85%' },
        }
      );

      if (cardsRef.current) {
        gsap.fromTo(
          Array.from(cardsRef.current.children),
          { opacity: 0, y: 50 },
          {
            opacity: 1, y: 0, stagger: 0.2, duration: 0.9, ease: 'power3.out',
            scrollTrigger: { trigger: cardsRef.current, start: 'top 80%' },
          }
        );
      }
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="pipeline" style={{
      padding: 'clamp(80px, 10vw, 140px) clamp(20px, 5vw, 80px)',
      background: 'linear-gradient(180deg, #020b14 0%, #041120 100%)',
      position: 'relative',
    }}>
      {/* Background accent */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, transparent, #0d2d44, transparent)',
      }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Section header */}
        <div ref={titleRef} style={{ marginBottom: '72px', opacity: 0 }}>
          <div className="overline" style={{ marginBottom: '20px' }}>HOW IT WORKS</div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(42px, 6vw, 80px)',
            fontWeight: 300,
            color: '#e8f4ff',
            letterSpacing: '-0.01em',
            lineHeight: 1.1,
            marginBottom: '16px',
          }}>The Intelligence Pipeline</h2>
          <p style={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 300,
            fontSize: '16px',
            color: '#8ab4cc',
            maxWidth: '500px',
          }}>Three stages. One result. Zero compromise.</p>
        </div>

        {/* Cards */}
        <div ref={cardsRef} style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
        }}>
          {stages.map((stage) => (
            <div
              key={stage.num}
              className="card-hover"
              style={{
                background: '#061828',
                border: '1px solid #0d2d44',
                padding: '36px 32px',
                position: 'relative',
                opacity: 0,
              }}
            >
              {/* Number */}
              <div style={{
                position: 'absolute',
                top: '24px',
                right: '28px',
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: '72px',
                fontWeight: 300,
                color: stage.color,
                opacity: 0.08,
                lineHeight: 1,
                userSelect: 'none',
              }}>{stage.num}</div>

              {/* Icon */}
              <div style={{ marginBottom: '24px' }}>{stage.icon}</div>

              {/* Title */}
              <div style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: '30px',
                fontWeight: 400,
                color: '#e8f4ff',
                marginBottom: '6px',
                lineHeight: 1.2,
              }}>{stage.title}</div>

              <div style={{
                fontFamily: 'Space Grotesk',
                fontSize: '10px',
                letterSpacing: '0.2em',
                color: stage.color,
                textTransform: 'uppercase',
                marginBottom: '16px',
              }}>{stage.subtitle}</div>

              {/* Description */}
              <p style={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 300,
                fontSize: '14px',
                color: '#8ab4cc',
                lineHeight: 1.7,
                marginBottom: '28px',
              }}>{stage.desc}</p>

              {/* Badge */}
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <div style={{
                  border: `1px solid ${stage.color}`,
                  padding: '5px 14px',
                  fontFamily: 'Space Grotesk',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: stage.color,
                  letterSpacing: '0.15em',
                }}>{stage.badge}</div>
                <div style={{
                  fontFamily: 'Space Grotesk',
                  fontSize: '9px',
                  color: '#3d6680',
                  letterSpacing: '0.2em',
                  textTransform: 'uppercase',
                }}>{stage.badgeLabel}</div>
              </div>

              {/* Bottom accent line */}
              <div style={{
                position: 'absolute',
                bottom: 0, left: 0, right: 0,
                height: '2px',
                background: `linear-gradient(90deg, ${stage.color}, transparent)`,
                opacity: 0.4,
              }} />
            </div>
          ))}
        </div>

        {/* Flow diagram */}
        <div style={{ marginTop: '64px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0', overflowX: 'auto', padding: '20px 0' }}>
          {['QUERY INPUT', 'DIRECT MAP', 'BM25 SCORE', 'LLM REWRITE', 'RESULTS'].map((step, i) => (
            <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                background: '#041120',
                border: '1px solid #0d2d44',
                padding: '10px 18px',
                fontFamily: 'Space Grotesk',
                fontSize: '10px',
                fontWeight: 500,
                letterSpacing: '0.15em',
                color: i === 0 || i === 4 ? '#00d4aa' : '#8ab4cc',
                whiteSpace: 'nowrap',
              }}>{step}</div>
              {i < 4 && (
                <div style={{ padding: '0 2px' }}>
                  <svg width="40" height="12" viewBox="0 0 40 12">
                    <line x1="0" y1="6" x2="32" y2="6" stroke="#1a4a66" strokeWidth="1" strokeDasharray="3 2"/>
                    <polygon points="32,2 40,6 32,10" fill="#1a4a66"/>
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
