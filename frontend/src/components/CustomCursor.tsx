import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

export default function CustomCursor() {
  const outerRef = useRef<HTMLDivElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const outer = outerRef.current;
    const inner = innerRef.current;
    if (!outer || !inner) return;

    let mouseX = 0, mouseY = 0;
    let outerX = 0, outerY = 0;

    const onMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      gsap.to(inner, { x: mouseX, y: mouseY, duration: 0.08, ease: 'power2.out' });
    };

    const tick = () => {
      outerX += (mouseX - outerX) * 0.12;
      outerY += (mouseY - outerY) * 0.12;
      gsap.set(outer, { x: outerX, y: outerY });
      requestAnimationFrame(tick);
    };

    const onEnter = () => outer.classList.add('hovered');
    const onLeave = () => outer.classList.remove('hovered');

    document.addEventListener('mousemove', onMove);
    const raf = requestAnimationFrame(tick);

    const interactables = document.querySelectorAll('a, button, .card-hover, .nav-link');
    interactables.forEach(el => {
      el.addEventListener('mouseenter', onEnter);
      el.addEventListener('mouseleave', onLeave);
    });

    return () => {
      document.removeEventListener('mousemove', onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      <div ref={outerRef} className="cursor-outer" />
      <div ref={innerRef} className="cursor-inner" />
    </>
  );
}
