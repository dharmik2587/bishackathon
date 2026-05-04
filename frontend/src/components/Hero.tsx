import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

export default function Hero() {
  const sectionRef = useRef<HTMLElement>(null);
  const overlineRef = useRef<HTMLDivElement>(null);
  const line1Ref = useRef<HTMLDivElement>(null);
  const line2Ref = useRef<HTMLDivElement>(null);
  const line3Ref = useRef<HTMLDivElement>(null);
  const subRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const pillsRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline({ delay: 0.5 });

    tl.fromTo(overlineRef.current, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' })
      .fromTo(line1Ref.current, { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out' }, '-=0.3')
      .fromTo(line2Ref.current, { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out' }, '-=0.6')
      .fromTo(line3Ref.current, { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out' }, '-=0.6')
      .fromTo(subRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }, '-=0.4')
      .fromTo(ctaRef.current, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' }, '-=0.4')
      .fromTo(pillsRef.current?.children ? Array.from(pillsRef.current.children) : [],
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, stagger: 0.12, duration: 0.5, ease: 'power2.out' },
        '-=0.3'
      )
      .fromTo(scrollRef.current, { opacity: 0 }, { opacity: 1, duration: 0.5 }, '-=0.2');

    // Animate grid slowly
    gsap.to('.grid-bg', { y: -20, duration: 8, ease: 'sine.inOut', yoyo: true, repeat: -1 });
  }, []);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const stats = [
    { label: 'HIT RATE @3', value: '99%' },
    { label: 'MRR @5', value: '1.0' },
    { label: 'AVG LATENCY', value: '1.12s' },
  ];

  return (
    <section
      ref={sectionRef}
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        padding: '120px 40px 80px',
        textAlign: 'center',
        overflow: 'hidden',
      }}
    >
      {/* Grid background */}
      <div className="grid-bg" style={{
        position: 'absolute',
        inset: '-20px',
        zIndex: 0,
        pointerEvents: 'none',
      }} />

      {/* Radial glow center */}
      <div style={{
        position: 'absolute',
        top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '700px', height: '700px',
        background: 'radial-gradient(circle, rgba(0,212,170,0.06) 0%, rgba(26,140,255,0.04) 40%, transparent 70%)',
        pointerEvents: 'none',
        zIndex: 0,
      }} />

      {/* Corner decorative lines */}
      <div style={{ position: 'absolute', top: '100px', left: '40px', width: '60px', height: '60px', borderTop: '1px solid #0d2d44', borderLeft: '1px solid #0d2d44' }} />
      <div style={{ position: 'absolute', top: '100px', right: '40px', width: '60px', height: '60px', borderTop: '1px solid #0d2d44', borderRight: '1px solid #0d2d44' }} />
      <div style={{ position: 'absolute', bottom: '80px', left: '40px', width: '60px', height: '60px', borderBottom: '1px solid #0d2d44', borderLeft: '1px solid #0d2d44' }} />
      <div style={{ position: 'absolute', bottom: '80px', right: '40px', width: '60px', height: '60px', borderBottom: '1px solid #0d2d44', borderRight: '1px solid #0d2d44' }} />

      <div style={{ position: 'relative', zIndex: 2, maxWidth: '1000px', width: '100%' }}>
        {/* Overline */}
        <div ref={overlineRef} className="overline" style={{ marginBottom: '32px', opacity: 0 }}>
          BUREAU OF INDIAN STANDARDS &nbsp;·&nbsp; RAG PIPELINE v2.0 &nbsp;·&nbsp; DEEPSEEK POWERED
        </div>

        {/* Headline */}
        <div style={{ marginBottom: '32px', overflow: 'hidden' }}>
          <div ref={line1Ref} style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(52px, 9vw, 110px)',
            fontWeight: 300,
            lineHeight: 1.0,
            color: '#e8f4ff',
            letterSpacing: '-0.01em',
            opacity: 0,
          }}>Intelligence</div>
          <div ref={line2Ref} style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(52px, 9vw, 110px)',
            fontWeight: 300,
            lineHeight: 1.0,
            letterSpacing: '-0.01em',
            background: 'linear-gradient(135deg, #00d4aa, #1a8cff)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            opacity: 0,
          }}>Engineered for</div>
          <div ref={line3Ref} style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(52px, 9vw, 110px)',
            fontWeight: 300,
            lineHeight: 1.0,
            color: '#e8f4ff',
            letterSpacing: '-0.01em',
            opacity: 0,
          }}>Indian Standards.</div>
        </div>

        {/* Sub-headline */}
        <p ref={subRef} style={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 300,
          fontSize: 'clamp(15px, 2vw, 18px)',
          color: '#8ab4cc',
          lineHeight: 1.7,
          maxWidth: '680px',
          margin: '0 auto 40px',
          opacity: 0,
        }}>
          A multi-stage Retrieval-Augmented Generation engine delivering BIS standard recommendations with sub-second latency — powered by BM25 retrieval and DeepSeek LLM query rewriting.
        </p>

        {/* CTAs */}
        <div ref={ctaRef} style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '48px', opacity: 0 }}>
          <button className="btn-primary" onClick={() => scrollTo('pipeline')}>
            EXPLORE PIPELINE
          </button>
          <button className="btn-outline" onClick={() => scrollTo('performance')}>
            VIEW PERFORMANCE
          </button>
        </div>

        {/* Stat pills */}
        <div ref={pillsRef} style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {stats.map((s) => (
            <div key={s.label} className="stat-pill">
              <span className="dot" />
              <span style={{ color: '#00d4aa', fontWeight: 500 }}>{s.label}</span>
              <span style={{ color: '#e8f4ff' }}>·</span>
              <span style={{ color: '#e8f4ff' }}>{s.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div ref={scrollRef} className="scroll-indicator" style={{
        position: 'absolute',
        bottom: '32px',
        left: '50%',
        transform: 'translateX(-50%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '8px',
        opacity: 0,
        zIndex: 2,
      }}>
        <span style={{
          fontFamily: 'Space Grotesk',
          fontSize: '9px',
          letterSpacing: '0.3em',
          color: '#3d6680',
          textTransform: 'uppercase',
        }}>SCROLL</span>
        <div style={{ width: '1px', height: '40px', background: 'linear-gradient(to bottom, #3d6680, transparent)' }} />
      </div>
    </section>
  );
}
