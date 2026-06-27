import React, { useRef } from 'react';
import { Sliders } from 'lucide-react';

interface ComparisonSliderProps {
  originalImage: string;
  renderedImage: string;
  sliderPos: number;
  setSliderPos: (pos: number) => void;
  isDragging: boolean;
  setIsDragging: (isDrag: boolean) => void;
}

export const ComparisonSlider: React.FC<ComparisonSliderProps> = ({
  originalImage,
  renderedImage,
  sliderPos,
  setSliderPos,
  isDragging,
  setIsDragging,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(percentage);
  };

  const onMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    handleMove(e.touches[0].clientX);
  };

  return (
    <div 
      ref={containerRef}
      className="comparison-container w-full h-full max-h-[520px]"
      onMouseMove={onMouseMove}
      onTouchMove={onTouchMove}
      onMouseUp={() => setIsDragging(false)}
      onMouseLeave={() => setIsDragging(false)}
      onTouchEnd={() => setIsDragging(false)}
    >
      <img 
        src={renderedImage} 
        alt="Rendered face" 
        className="comparison-image animate-fade-in"
      />
      
      <img 
        src={originalImage} 
        alt="Original face" 
        className="comparison-image"
        style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
      />

      <div 
        className="comparison-handle"
        style={{ left: `${sliderPos}%` }}
        onMouseDown={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onTouchStart={() => setIsDragging(true)}
      >
        <div className="comparison-handle-button select-none cursor-ew-resize">
          <Sliders className="w-3.5 h-3.5 rotate-90 text-purple-400" />
        </div>
      </div>

      <span className="comparison-label left left-4">BEFORE</span>
      <span className="comparison-label right right-4">AFTER</span>
    </div>
  );
};
