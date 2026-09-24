"use client";

import { useEffect, useRef, useState, type ElementType, type ReactNode } from "react";

interface ScrollRevealProps {
  children: ReactNode;
  /** Stagger index — each step adds ~80ms of delay. Use the item's position in a list. */
  index?: number;
  className?: string;
  as?: ElementType;
}

/**
 * Fades/slides/blurs children into view the first time they cross into the
 * viewport. Always starts hidden (matches SSR, which has no `window`) and
 * flips to visible client-side — never decide the initial state from
 * `window`/`IntersectionObserver` at module scope, or the server-rendered
 * HTML and the client's first render disagree and React throws a hydration
 * mismatch.
 */
export function ScrollReveal({ children, index = 0, className, as: Tag = "div" }: ScrollRevealProps) {
  const ref = useRef<HTMLElement | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    if (typeof IntersectionObserver === "undefined") {
      // Ancient-browser fallback — defer so this isn't a synchronous
      // setState call inside the effect body.
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
