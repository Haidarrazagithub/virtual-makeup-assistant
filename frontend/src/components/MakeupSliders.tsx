import React from 'react';

interface SliderGroup {
  label: string;
  color: string;
  opacity: number;
  setColor: (c: string) => void;
  setOpacity: (o: number) => void;
  defO: number;
  swatches: string[];
}

interface MakeupSlidersProps {
  originalImage: string | null;
  lipstickColor: string;
  lipstickOpacity: number;
  setLipstickColor: (c: string) => void;
  setLipstickOpacity: (o: number) => void;
  blushColor: string;
  blushOpacity: number;
  setBlushColor: (c: string) => void;
  setBlushOpacity: (o: number) => void;
  foundationColor: string;
  foundationOpacity: number;
  setFoundationColor: (c: string) => void;
  setFoundationOpacity: (o: number) => void;
  eyeshadowColor: string;
  eyeshadowOpacity: number;
  setEyeshadowColor: (c: string) => void;
  setEyeshadowOpacity: (o: number) => void;
  eyelinerColor: string;
  eyelinerOpacity: number;
  setEyelinerColor: (c: string) => void;
  setEyelinerOpacity: (o: number) => void;
  eyebrowColor: string;
  eyebrowOpacity: number;
  setEyebrowColor: (c: string) => void;
  setEyebrowOpacity: (o: number) => void;
}

export const MakeupSliders: React.FC<MakeupSlidersProps> = ({
  originalImage,
  lipstickColor, lipstickOpacity, setLipstickColor, setLipstickOpacity,
  blushColor, blushOpacity, setBlushColor, setBlushOpacity,
  foundationColor, foundationOpacity, setFoundationColor, setFoundationOpacity,
  eyeshadowColor, eyeshadowOpacity, setEyeshadowColor, setEyeshadowOpacity,
  eyelinerColor, eyelinerOpacity, setEyelinerColor, setEyelinerOpacity,
  eyebrowColor, eyebrowOpacity, setEyebrowColor, setEyebrowOpacity,
}) => {
  if (!originalImage) {
    return (
      <div className="text-center py-12 text-sm text-gray-500">
        Upload or capture a photo to customize your sliders.
      </div>
    );
  }

  const groups: SliderGroup[] = [
    { label: 'LIPSTICK', color: lipstickColor, opacity: lipstickOpacity, setColor: setLipstickColor, setOpacity: setLipstickOpacity, defO: 0.6, swatches: ['#DFA8A8', '#E9967A', '#C41E3A', '#D15276', '#4A0E17', '#800020', '#BC8F8F'] },
    { label: 'BLUSH', color: blushColor, opacity: blushOpacity, setColor: setBlushColor, setOpacity: setBlushOpacity, defO: 0.4, swatches: ['#FFC0CB', '#FFB7C5', '#F4A460', '#E9967A', '#DC143C'] },
    { label: 'FOUNDATION', color: foundationColor, opacity: foundationOpacity, setColor: setFoundationColor, setOpacity: setFoundationOpacity, defO: 0.3, swatches: ['#F6D5C3', '#F3D2C1', '#E8C39E', '#DAB088', '#C59A6F'] },
    { label: 'EYESHADOW', color: eyeshadowColor, opacity: eyeshadowOpacity, setColor: setEyeshadowColor, setOpacity: setEyeshadowOpacity, defO: 0.4, swatches: ['#E6E6FA', '#DEB887', '#BC8F8F', '#708090', '#36454F'] },
    { label: 'EYELINER', color: eyelinerColor, opacity: eyelinerOpacity, setColor: setEyelinerColor, setOpacity: setEyelinerOpacity, defO: 0.6, swatches: ['#000000', '#3D2B1F', '#5C4033', '#191970', '#0E3A20'] },
    { label: 'EYEBROWS', color: eyebrowColor, opacity: eyebrowOpacity, setColor: setEyebrowColor, setOpacity: setEyebrowOpacity, defO: 0.4, swatches: ['#1C1C1C', '#2C1E1A', '#3D2B1F', '#5C4033'] }
  ];

  return (
    <div className="flex flex-col gap-5 fade-in">
      {groups.map((grp) => (
        <div key={grp.label} className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="text-white">{grp.label}</span>
            <span className="text-gray-400">{Math.round(grp.opacity * 100)}%</span>
          </div>
          <div className="flex gap-4 items-center">
            <input 
              type="color" 
              value={grp.color}
              onChange={(e) => grp.setColor(e.target.value)}
              className="w-8 h-8 rounded-lg cursor-pointer bg-transparent border border-white/10 outline-none p-0 overflow-hidden"
            />
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.05"
              value={grp.opacity}
              onChange={(e) => grp.setOpacity(parseFloat(e.target.value))}
              className="flex-1 accent-purple-500 bg-white/10 h-1 rounded-lg appearance-none cursor-pointer animate-fade-in"
            />
          </div>
          <div className="flex flex-wrap gap-2 mt-1 items-center">
            <span className="text-[10px] text-gray-500 font-semibold mr-1">Shades:</span>
            {grp.swatches.map((c) => (
              <button 
                key={c}
                onClick={() => {
                  grp.setColor(c);
                  if (grp.opacity === 0) grp.setOpacity(grp.defO);
                }}
                className={`swatch-pill ${grp.color.toLowerCase() === c.toLowerCase() ? 'active' : ''}`}
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
