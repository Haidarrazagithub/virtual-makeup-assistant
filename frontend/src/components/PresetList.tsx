import React from 'react';
import { Check, Trash2 } from 'lucide-react';
import type { SavedLook } from '../services/api';

interface PresetListProps {
  originalImage: string | null;
  activePreset: string;
  selectPreset: (name: string) => void;
  savedLooks: SavedLook[];
  applySavedLook: (look: SavedLook) => void;
  deleteLook: (id: number) => void;
}

export const PresetList: React.FC<PresetListProps> = ({
  originalImage,
  activePreset,
  selectPreset,
  savedLooks,
  applySavedLook,
  deleteLook,
}) => {
  return (
    <div className="flex flex-col gap-6 fade-in">
      {/* curations preset section */}
      <div className="flex flex-col gap-4">
        <div>
          <h4 className="text-white font-semibold font-heading m-0 mb-1 text-sm">Select Look Occasion</h4>
          <p className="text-xs text-gray-400">Presets are custom curated matching your classified skin undertones.</p>
        </div>
        {!originalImage ? (
          <div className="text-center py-6 text-sm text-gray-500">
            Please upload or capture a photo first to view custom presets.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {['office', 'party', 'bridal'].map((name) => {
              const isActive = activePreset === name;
              const title = name === 'office' ? 'Office Look' : name === 'party' ? 'Glam Party Look' : 'Bridal Occasion Look';
              const desc = name === 'office' ? 'Soft, natural tones for everyday professional environment.' : name === 'party' ? 'Bold, glossy lips and darker eyeshadow for evening events.' : 'Deep, warm gold shades with glowing cheeks for ceremony wear.';
              
              const presetColors: Record<string, string[]> = {
                office: ['#DFA8A8', '#DEB887', '#5C4033', '#3D2B1F'],
                party: ['#800020', '#4B0082', '#000000', '#1C1C1C'],
                bridal: ['#B76E79', '#BC8F8F', '#1C110B', '#2C1E1A']
              };
              const colors = presetColors[name] || [];

              return (
                <div 
                  key={name}
                  onClick={() => selectPreset(name)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition flex justify-between items-center ${isActive ? 'bg-purple-600/10 border-purple-500/50 text-white' : 'bg-white/5 border-white/10 hover:border-purple-500/30 text-gray-400'}`}
                >
                  <div>
                    <h5 className="font-heading text-sm font-semibold text-white m-0 mb-1">{title}</h5>
                    <p className="text-xs text-gray-400 max-w-[280px] leading-relaxed mb-2">{desc}</p>
                    <div className="flex gap-1.5 items-center">
                      <span className="text-[10px] text-gray-500 mr-1">Look Palette:</span>
                      {colors.map((c, i) => (
                        <span 
                          key={i} 
                          className="w-3 h-3 rounded-full border border-white/20" 
                          style={{ backgroundColor: c }} 
                        />
                      ))}
                    </div>
                  </div>
                  {isActive && (
                    <span className="w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center text-white">
                      <Check className="w-3 h-3" />
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Saved Looks Section */}
      <div className="flex flex-col gap-4 border-t border-white/10 pt-5">
        <div>
          <h4 className="text-white font-semibold font-heading m-0 mb-1 text-sm">Your Saved Looks</h4>
          <p className="text-xs text-gray-400 font-sans">Custom combinations bookmarked by you.</p>
        </div>
        {savedLooks.length === 0 ? (
          <div className="text-center py-6 text-xs text-gray-500 bg-white/[0.01] rounded-xl border border-dashed border-white/5">
            No custom looks saved yet. Setup your sliders and click "Save Current Look" to bookmark one.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {savedLooks.map((look) => {
              const isActive = activePreset === `saved_${look.id}`;
              return (
                <div 
                  key={look.id}
                  className={`p-3.5 rounded-xl border flex justify-between items-center transition ${isActive ? 'bg-purple-600/10 border-purple-500/50 text-white' : 'bg-white/5 border-white/10 hover:border-purple-500/30 text-gray-400'}`}
                >
                  <div 
                    onClick={() => applySavedLook(look)}
                    className="flex-1 cursor-pointer"
                  >
                    <h5 className="font-heading text-sm font-semibold text-white m-0 mb-2">{look.name}</h5>
                    <div className="flex gap-1.5 items-center">
                      <span className="text-[10px] text-gray-500 mr-1">Shades:</span>
                      {look.lipstick_color && <span className="w-2.5 h-2.5 rounded-full border border-white/20" style={{ backgroundColor: look.lipstick_color }} title="Lips" />}
                      {look.blush_color && <span className="w-2.5 h-2.5 rounded-full border border-white/20" style={{ backgroundColor: look.blush_color }} title="Blush" />}
                      {look.eyeshadow_color && <span className="w-2.5 h-2.5 rounded-full border border-white/20" style={{ backgroundColor: look.eyeshadow_color }} title="Eyeshadow" />}
                      {look.eyeliner_color && <span className="w-2.5 h-2.5 rounded-full border border-white/20" style={{ backgroundColor: look.eyeliner_color }} title="Eyeliner" />}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {isActive && (
                      <span className="w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center text-white">
                        <Check className="w-3 h-3" />
                      </span>
                    )}
                    <button 
                      onClick={() => deleteLook(look.id)}
                      className="text-gray-500 hover:text-red-400 transition bg-transparent border-0 cursor-pointer p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
