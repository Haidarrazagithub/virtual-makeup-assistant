import React from 'react';
import { Sparkles } from 'lucide-react';

interface HeaderProps {
  skinTone: string | null;
  faceShape: string | null;
}

export const Header: React.FC<HeaderProps> = ({ skinTone, faceShape }) => {
  return (
    <header className="border-b border-white/10 py-4 px-6 md:px-12 flex items-center justify-between backdrop-blur-md bg-black/25 sticky top-0 z-50">
      <div className="flex items-center gap-2">
        <Sparkles className="text-purple-500 w-6 h-6 animate-pulse" />
        <h1 className="text-xl md:text-2xl font-bold tracking-tight font-heading m-0 text-white">
          BeautyLens <span className="text-purple-500 font-light">AI</span>
        </h1>
      </div>
      <div className="flex items-center gap-2.5">
        {skinTone && (
          <span className="text-xs font-semibold px-3.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/25 text-purple-300 shadow-sm shadow-purple-500/5">
            Tone: {skinTone}
          </span>
        )}
        {faceShape && (
          <span className="text-xs font-semibold px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/25 text-amber-300 shadow-sm shadow-amber-500/5">
            Shape: {faceShape}
          </span>
        )}
      </div>
    </header>
  );
};
