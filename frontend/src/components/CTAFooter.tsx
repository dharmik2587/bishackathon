import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function CTAFooter() {
  const sectionRef = useRef<HTMLElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const footerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(ctaRef.current?.children ? Array.from(ctaRef.current.children) : [],
        { opacity: 0, y: 60 },
        { opacity: 1, y: 0, stagger: 0.15, duration: 1, ease: 'power3.out',
          scrollTrigger: { trigger: ctaRef.current, start: 'top 85%' } }
      );
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  return (
    <footer ref={sectionRef} style={{ background: '#020b14', position: 'relative' }}>
      {/* Top border */}
      <div style={{ height: '1px', background: 'linear-gradient(90deg, transparent, #00d4aa44, transparent)' }} />

      {/* CTA Block */}
      <div style={{
        padding: 'clamp(80px, 12vw, 160px) clamp(20px, 5vw, 80px)',
        textAlign: 'center',
        position: 'relative',
      }}>
        {/* Background glow */}
        <div style={{
          position: 'absolute',
          top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '600px', height: '300px',
          background: 'radial-gradient(ellipse, rgba(0,212,170,0.07) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div ref={ctaRef}>
          <div className="overline" style={{ marginBottom: '28px', opacity: 0 }}>GET STARTED</div>

          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(52px, 9vw, 120px)',
            fontWeight: 300,
            color: '#e8f4ff',
            letterSpacing: '-0.02em',
            lineHeight: 1.0,
            marginBottom: '12px',
            opacity: 0,
          }}>Ready to Query.</h2>

          <p style={{
            fontFamily: 'Inter',
            fontWeight: 300,
            fontSize: 'clamp(15px, 2vw, 18px)',
            color: '#8ab4cc',
            marginBottom: '48px',
            opacity: 0,
          }}>Search any BIS standard. Get precision results. Sub-second.</p>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap', opacity: 0 }}>
            <button
              className="btn-primary"
              onClick={scrollToTop}
              style={{ padding: '16px 48px', fontSize: '12px' }}
            >
              LAUNCH ENGINE
            </button>
            <a
              href="https://github.com/dharmik2587/bishackathon"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-outline"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '10px',
                padding: '15px 36px',
                textDecoration: 'none',
                fontSize: '12px',
              }}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M7 0.5C3.41 0.5 0.5 3.41 0.5 7c0 2.87 1.86 5.3 4.44 6.16.32.06.44-.14.44-.31v-1.08c-1.8.39-2.18-.87-2.18-.87-.3-.75-.72-.95-.72-.95-.59-.4.04-.39.04-.39.65.05 1 .67 1 .67.58 1 1.52.71 1.9.54.06-.42.23-.71.41-.87-1.44-.16-2.95-.72-2.95-3.2 0-.71.25-1.29.67-1.74-.07-.16-.29-.82.06-1.71 0 0 .55-.17 1.79.67.52-.14 1.08-.21 1.63-.21s1.11.07 1.63.21c1.24-.84 1.79-.67 1.79-.67.35.89.13 1.55.06 1.71.42.45.67 1.03.67 1.74 0 2.49-1.52 3.04-2.96 3.2.23.2.44.6.44 1.2v1.79c0 .17.12.37.44.31C11.64 12.3 13.5 9.87 13.5 7c0-3.59-2.91-6.5-6.5-6.5z" fill="currentColor"/>
              </svg>
              VIEW SOURCE
            </a>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div style={{ height: '1px', background: '#0d2d44', margin: '0 clamp(20px, 5vw, 80px)' }} />

      {/* Footer bar */}
      <div ref={footerRef} style={{
        padding: '32px clamp(20px, 5vw, 80px)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        {/* Left: Wordmark */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
          <span style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '22px',
            fontWeight: 300,
            color: '#e8f4ff',
          }}>BIS</span>
          <span style={{
            fontFamily: 'Space Grotesk',
            fontSize: '8px',
            letterSpacing: '0.3em',
            color: '#00d4aa',
            textTransform: 'uppercase',
          }}>RAG ENGINE</span>
        </div>

        {/* Center: nav */}
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          {['pipeline', 'performance', 'architecture', 'data'].map(id => (
            <button
              key={id}
              className="footer-link"
              onClick={() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })}
              style={{ background: 'none', border: 'none' }}
            >{id}</button>
          ))}
        </div>

        {/* Right: credits */}
        <div style={{
          fontFamily: 'Space Grotesk',
          fontSize: '10px',
          letterSpacing: '0.15em',
          color: '#3d6680',
          textTransform: 'uppercase',
          textAlign: 'right'
        }}>
          Made with ❤️ by Dharmik - Backend Developer & Aayasha Patel - Frontend Developer
        </div>
      </div>

      {/* Copyright */}
      <div style={{
        textAlign: 'center',
        padding: '16px',
        borderTop: '1px solid #061828',
        fontFamily: 'Space Grotesk',
        fontSize: '10px',
        color: '#1a4a66',
        letterSpacing: '0.1em',
      }}>
        © 2025 BIS RAG ENGINE · BUREAU OF INDIAN STANDARDS HACKATHON
      </div>
    </footer>
  );
}
