import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const panels = [
  {
    num: '01',
    title: 'Domain Intelligence',
    subtitle: 'Engineering vocabulary built-in',
    desc: 'Civil, electrical, and mechanical engineering terms are hardcoded with semantic expansions — ensuring BIS standards are retrieved even when queries use informal or abbreviated terminology.',
    tag: 'KNOWLEDGE BASE',
    color: '#00d4aa',
  },
  {
    num: '02',
    title: 'Multi-Stage Fallback',
    subtitle: 'Graceful degradation, always',
    desc: 'The pipeline cascades intelligently: Direct Map → BM25 → LLM Rewrite. Each stage only activates when the previous one lacks confidence — maximizing speed while preserving accuracy.',
    tag: 'PIPELINE DESIGN',
    color: '#1a8cff',
  },
  {
    num: '03',
    title: 'Zero Infrastructure',
    subtitle: 'No GPU, no cloud, no problem',
    desc: 'The entire RAG engine runs client-side and on commodity Python hardware. No vector databases, no GPU clusters — just optimized algorithms delivering sub-second performance.',
    tag: 'DEPLOYMENT',
    color: '#00d4aa',
  },
  {
    num: '04',
    title: 'Production Grade',
    subtitle: 'Hackathon-proven, deploy-ready',
    desc: 'Built to production standards: modular Python backend, TypeScript frontend, JSON-based corpus, full evaluation pipeline with Hit Rate and MRR metrics. Deployable in hours.',
    tag: 'ENGINEERING',
    color: '#1a8cff',
  },
];

export default function FeatureStrip() {
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
          { opacity: 0, y: 50, scale: 0.98 },
          {
            opacity: 1, y: 0, scale: 1,
            stagger: 0.18, duration: 1, ease: 'power3.out',
            scrollTrigger: { trigger: gridRef.current, start: 'top 80%' },
          }
        );
      }
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} style={{
      padding: 'clamp(80px, 10vw, 140px) clamp(20px, 5vw, 80px)',
      background: 'linear-gradient(180deg, #020b14 0%, #041120 50%, #020b14 100%)',
      position: 'relative',
    }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '1px', background: 'linear-gradient(90deg, transparent, #0d2d44, transparent)' }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div ref={titleRef} style={{ marginBottom: '72px', opacity: 0 }}>
          <div className="overline" style={{ marginBottom: '20px' }}>KEY CAPABILITIES</div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(42px, 6vw, 80px)',
            fontWeight: 300,
            color: '#e8f4ff',
            letterSpacing: '-0.01em',
            lineHeight: 1.1,
            marginBottom: '16px',
          }}>Built Different.</h2>
          <p style={{
            fontFamily: 'Inter',
            fontWeight: 300,
            fontSize: '16px',
            color: '#8ab4cc',
          }}>Four core principles that define the engine.</p>
        </div>

        {/* 2x2 Grid */}
        <div ref={gridRef} style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
        }}>
          {panels.map((p) => (
            <div
              key={p.num}
              className="card-hover"
              style={{
                background: '#061828',
                border: '1px solid #0d2d44',
                padding: '40px 36px',
                position: 'relative',
                opacity: 0,
              }}
            >
              {/* Big BG number */}
              <div style={{
                position: 'absolute',
                bottom: '16px',
                right: '24px',
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: '100px',
                fontWeight: 300,
                color: p.color,
                opacity: 0.05,
                lineHeight: 1,
                userSelect: 'none',
                pointerEvents: 'none',
              }}>{p.num}</div>

              {/* Tag */}
              <div style={{
                display: 'inline-block',
                background: 'rgba(0,212,170,0.06)',
                border: `1px solid ${p.color}`,
                padding: '4px 12px',
                fontFamily: 'Space Grotesk',
                fontSize: '9px',
                letterSpacing: '0.25em',
                color: p.color,
                textTransform: 'uppercase',
                marginBottom: '24px',
                opacity: 0.8,
              }}>{p.tag}</div>

              {/* Title */}
              <div style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: 'clamp(26px, 3vw, 36px)',
                fontWeight: 300,
                color: '#e8f4ff',
                lineHeight: 1.15,
                marginBottom: '8px',
              }}>{p.title}</div>

              <div style={{
                fontFamily: 'Space Grotesk',
                fontSize: '11px',
                letterSpacing: '0.15em',
                color: p.color,
                textTransform: 'uppercase',
                marginBottom: '18px',
                opacity: 0.7,
              }}>{p.subtitle}</div>

              <p style={{
                fontFamily: 'Inter',
                fontWeight: 300,
                fontSize: '14px',
                color: '#8ab4cc',
                lineHeight: 1.7,
              }}>{p.desc}</p>

              {/* Bottom border */}
              <div style={{
                position: 'absolute',
                bottom: 0, left: 0, right: 0,
                height: '1px',
                background: `linear-gradient(90deg, ${p.color}, transparent)`,
                opacity: 0.25,
              }} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
