"use client";

import { useEffect, useRef, useState, type ElementType, type ReactNode } from "react";

interface ScrollRevealProps {
  children: ReactNode;
  index?: number;
  className?: string;
  as?: ElementType;
}

export function ScrollReveal({ children, index = 0, className, as: Tag = "div" }: ScrollRevealProps) {
  const ref = useRef<HTMLElement | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    if (typeof IntersectionObserver === "undefined") {
      const raf = requestAnimationFrame(() => setVisible(true));
      return () => cancelAnimationFrame(raf);
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -10% 0px" }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <Tag
      ref={ref}
      className={`scroll-reveal${visible ? " show" : ""}${className ? ` ${className}` : ""}`}
      style={{ "--reveal-delay": `${Math.min(index, 8) * 0.08}s` } as React.CSSProperties}
    >
      {children}
    </Tag>
  );
}
