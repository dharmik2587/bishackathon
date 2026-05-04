import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';

export default function Navbar() {
  const navRef = useRef<HTMLElement>(null);
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    gsap.fromTo(navRef.current,
      { y: -80, opacity: 0 },
      { y: 0, opacity: 1, duration: 1, ease: 'power3.out', delay: 0.8 }
    );

    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMenuOpen(false);
  };

  return (
    <nav
      ref={navRef}
      style={{
        position: 'fixed',
        top: 0, left: 0, right: 0,
        zIndex: 1000,
        padding: '0 40px',
        height: '72px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backdropFilter: 'blur(20px)',
        background: scrolled ? 'rgba(2,11,20,0.95)' : 'rgba(2,11,20,0.6)',
        borderBottom: scrolled ? '1px solid #0d2d44' : '1px solid transparent',
        transition: 'background 0.4s ease, border-color 0.4s ease',
      }}
    >
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
        <span style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontSize: '26px',
          fontWeight: 300,
          color: '#e8f4ff',
          letterSpacing: '0.05em',
        }}>BIS</span>
        <span style={{
          fontFamily: 'Space Grotesk, monospace',
          fontSize: '9px',
          fontWeight: 600,
          letterSpacing: '0.3em',
          color: '#00d4aa',
          textTransform: 'uppercase',
        }}>RAG ENGINE</span>
      </div>

      {/* Desktop Nav */}
      <div className="hidden md:flex" style={{ gap: '40px', alignItems: 'center' }}>
        {['pipeline', 'performance', 'evaluation', 'architecture', 'data'].map(id => (
          <button key={id} className="nav-link" onClick={() => scrollTo(id)}
            style={{ background: 'none', border: 'none', padding: 0 }}>
            {id}
          </button>
        ))}
        <button className="btn-primary" onClick={() => scrollTo('pipeline')} style={{ padding: '10px 24px' }}>
          ACCESS ENGINE
        </button>
      </div>

      {/* Mobile menu button */}
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className="md:hidden"
        style={{ background: 'none', border: '1px solid #0d2d44', padding: '8px 12px', color: '#00d4aa', cursor: 'none', fontFamily: 'Space Grotesk', fontSize: '11px', letterSpacing: '0.1em' }}
      >
        {menuOpen ? 'CLOSE' : 'MENU'}
      </button>

      {/* Mobile menu */}
      {menuOpen && (
        <div style={{
          position: 'absolute',
          top: '72px', left: 0, right: 0,
          background: 'rgba(2,11,20,0.98)',
          borderBottom: '1px solid #0d2d44',
          padding: '20px 40px',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
        }}>
          {['pipeline', 'performance', 'evaluation', 'architecture', 'data'].map(id => (
            <button key={id} className="nav-link" onClick={() => scrollTo(id)}
              style={{ background: 'none', border: 'none', padding: '8px 0', textAlign: 'left' }}>
              {id}
            </button>
          ))}
        </div>
      )}
    </nav>
  );
}
