import { useEffect, useRef } from 'react';

export function FloatingParticles() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Create particles
    for (let i = 0; i < 50; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.width = Math.random() * 10 + 5 + 'px';
      particle.style.height = particle.style.width;
      particle.style.animationDuration = Math.random() * 3 + 2 + 's';
      particle.style.animationDelay = Math.random() * 2 + 's';
      container.appendChild(particle);
    }

    // Cleanup
    return () => {
      if (container) {
        container.innerHTML = '';
      }
    };
  }, []);

  return <div ref={containerRef} className="floating-particles" />;
}
