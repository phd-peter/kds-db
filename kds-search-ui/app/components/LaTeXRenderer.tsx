"use client";

import { useEffect, useRef } from 'react';
import katex from 'katex';

interface LaTeXRendererProps {
  content: string;
  className?: string;
}

export default function LaTeXRenderer({ content, className = "" }: LaTeXRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    
    // 텍스트에서 LaTeX 방정식을 찾아 변환합니다
    // LaTeX 패턴: $...$ (인라인) 또는 $$...$$ (블록)
    let processedContent = content;
    
    // 블록 방정식 ($$...$$) 처리
    const blockRegex = /\$\$(.*?)\$\$/g;
    processedContent = processedContent.replace(blockRegex, (match, formula) => {
      try {
        const htmlString = katex.renderToString(formula, {
          displayMode: true,
          throwOnError: false
        });
        return `<div class="katex-block my-2">${htmlString}</div>`;
      } catch (e) {
        console.error('LaTeX 렌더링 오류:', e);
        return match;
      }
    });
    
    // 인라인 방정식 ($...$) 처리
    const inlineRegex = /\$(.*?)\$/g;
    processedContent = processedContent.replace(inlineRegex, (match, formula) => {
      try {
        // 이미 블록 처리된 방정식은 제외
        if (match.startsWith('$$')) return match;
        
        const htmlString = katex.renderToString(formula, {
          displayMode: false,
          throwOnError: false
        });
        return `<span class="katex-inline">${htmlString}</span>`;
      } catch (e) {
        console.error('LaTeX 렌더링 오류:', e);
        return match;
      }
    });
    
    // HTML 삽입
    containerRef.current.innerHTML = processedContent;
  }, [content]);

  return (
    <div 
      ref={containerRef} 
      className={`latex-content ${className}`}
    />
  );
} 