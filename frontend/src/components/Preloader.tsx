import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

interface PreloaderProps {
  onComplete: () => void;
}

export default function Preloader({ onComplete }: PreloaderProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGPathElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const lineRef = useRef<HTMLDivElement>(null);
  const subtitleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline({
      onComplete: () => {
        gsap.to(containerRef.current, {
          opacity: 0,
          y: -30,
          duration: 0.8,
          ease: 'power3.inOut',
          onComplete,
        });
      },
    });

    // Animate path
    if (svgRef.current) {
      const length = svgRef.current.getTotalLength?.() || 200;
      gsap.set(svgRef.current, { strokeDasharray: length, strokeDashoffset: length });
      tl.to(svgRef.current, { strokeDashoffset: 0, duration: 1.4, ease: 'power2.inOut' });
    }

    // Typewriter effect
    if (textRef.current) {
      const text = 'INITIALIZING RAG ENGINE...';
      textRef.current.textContent = '';
      tl.call(() => {
        let i = 0;
        const interval = setInterval(() => {
          if (textRef.current) {
            textRef.current.textContent = text.slice(0, i + 1);
          }
          i++;
          if (i >= text.length) clearInterval(interval);
        }, 35);
      }, [], '-=0.2');
    }

    tl.fromTo(lineRef.current, { scaleX: 0, transformOrigin: 'left center' }, { scaleX: 1, duration: 0.7, ease: 'power3.out' }, '+=0.2');
    tl.fromTo(subtitleRef.current, { opacity: 0 }, { opacity: 1, duration: 0.4 }, '-=0.2');
    tl.to({}, { duration: 0.6 });
  }, [onComplete]);

  return (
    <div ref={containerRef} id="preloader">
      <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
        <path
          ref={svgRef}
          d="M10 10 L40 10 Q70 10 70 40 Q70 70 40 70 L10 70 Z M10 40 L50 40"
          stroke="#00d4aa"
          strokeWidth="2"
          fill="none"
          strokeLinecap="square"
        />
      </svg>

      <div
        ref={textRef}
        style={{
          fontFamily: 'Space Grotesk, monospace',
          fontSize: '11px',
          letterSpacing: '0.3em',
          color: '#00d4aa',
          textTransform: 'uppercase',
          minHeight: '16px',
        }}
      />

      <div
        ref={lineRef}
        style={{
          width: '200px',
          height: '1px',
          background: 'linear-gradient(90deg, #00d4aa, #1a8cff)',
        }}
      />

      <div
        ref={subtitleRef}
        style={{
          fontFamily: 'Space Grotesk, monospace',
          fontSize: '10px',
          letterSpacing: '0.25em',
          color: '#3d6680',
          textTransform: 'uppercase',
          opacity: 0,
        }}
      >
        BUREAU OF INDIAN STANDARDS · v2.0
      </div>
    </div>
  );
}
