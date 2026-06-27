import React, { useState, useRef, useEffect } from 'react';
import { 
  Camera, 
  Upload, 
  RotateCcw, 
  Loader2,
  Bookmark,
  Sparkles
} from 'lucide-react';
import { api } from './services/api';
import type { Product, ChatMessage, SavedLook } from './services/api';
import { Header } from './components/Header';
import { ComparisonSlider } from './components/ComparisonSlider';
import { PresetList } from './components/PresetList';
import { MakeupSliders } from './components/MakeupSliders';
import { ChatAssistant } from './components/ChatAssistant';
import { ProductCatalog } from './components/ProductCatalog';

export default function App() {
  // Session State
  const [sessionId, setSessionId] = useState<string>('');
  
  // Image states
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [renderedImage, setRenderedImage] = useState<string | null>(null);
  const [imageBlob, setImageBlob] = useState<Blob | null>(null);
  
  // Face attributes
  const [skinTone, setSkinTone] = useState<string | null>(null);
  const [faceShape, setFaceShape] = useState<string | null>(null);
  const [activePreset, setActivePreset] = useState<string>('');
  
  // Makeup parameters
  const [lipstickColor, setLipstickColor] = useState('#DFA8A8');
  const [lipstickOpacity, setLipstickOpacity] = useState(0.0);
  const [blushColor, setBlushColor] = useState('#FFC0CB');
  const [blushOpacity, setBlushOpacity] = useState(0.0);
  const [foundationColor, setFoundationColor] = useState('#F3D2C1');
  const [foundationOpacity, setFoundationOpacity] = useState(0.0);
  const [eyeshadowColor, setEyeshadowColor] = useState('#E6E6FA');
  const [eyeshadowOpacity, setEyeshadowOpacity] = useState(0.0);
  const [eyelinerColor, setEyelinerColor] = useState('#000000');
  const [eyelinerOpacity, setEyelinerOpacity] = useState(0.0);
  const [eyebrowColor, setEyebrowColor] = useState('#2C1E1A');
  const [eyebrowOpacity, setEyebrowOpacity] = useState(0.0);

  // Recommendations, Chat & Library
  const [recommendedProducts, setRecommendedProducts] = useState<Record<string, Product[]>>({});
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [savedLooks, setSavedLooks] = useState<SavedLook[]>([]);
  
  // UI states
  const [activeTab, setActiveTab] = useState<'presets' | 'sliders' | 'chat' | 'products'>('presets');
  const [loading, setLoading] = useState(false);
  const [lookNameInput, setLookNameInput] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  
  // Refs
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Split-Screen comparison slider state
  const [sliderPos, setSliderPos] = useState(50);
  const [isDragging, setIsDragging] = useState(false);

  // Initialize Session & Load Saved Looks on Mount
  useEffect(() => {
    let storedSessionId = localStorage.getItem('beautylens_session_id');
    if (!storedSessionId) {
      storedSessionId = 'session_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
      localStorage.setItem('beautylens_session_id', storedSessionId);
    }
    setSessionId(storedSessionId);
    
    fetchSavedLooks();
    fetchChatHistory(storedSessionId);
  }, []);

  const fetchChatHistory = async (sessId: string) => {
    try {
      const history = await api.fetchHistory(sessId);
      if (history && history.length > 0) {
        setChatHistory(history.map((msg: any) => ({
          sender: msg.sender,
          text: msg.text
        })));
      } else {
        setChatHistory([
          { sender: 'bot', text: 'Hi! I am your AI Makeup Expert. Upload a photo or turn on your camera, and type a style request like "Give me a bold party look" or adjust the sliders manually!' }
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch chat logs:", err);
    }
  };

  const fetchSavedLooks = async () => {
    try {
      const looks = await api.fetchSavedLooks();
      setSavedLooks(looks);
    } catch (err) {
      console.error("Failed to load saved looks:", err);
    }
  };

  const handleSaveLookSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lookNameInput.trim()) return;

    try {
      const payload = {
        name: lookNameInput.trim(),
        lipstick_color: lipstickColor,
        lipstick_opacity: lipstickOpacity,
        blush_color: blushColor,
        blush_opacity: blushOpacity,
        foundation_color: foundationColor,
        foundation_opacity: foundationOpacity,
        eyeshadow_color: eyeshadowColor,
        eyeshadow_opacity: eyeshadowOpacity,
        eyeliner_color: eyelinerColor,
        eyeliner_opacity: eyelinerOpacity,
        eyebrow_color: eyebrowColor,
        eyebrow_opacity: eyebrowOpacity
      };

      await api.createSavedLook(payload);
      setLookNameInput('');
      setShowSaveModal(false);
      fetchSavedLooks();
    } catch (err) {
      console.error("Failed to save look configuration:", err);
      alert("Error bookmarking look. Please try again.");
    }
  };

  const deleteLook = async (id: number) => {
    try {
      await api.deleteSavedLook(id);
      fetchSavedLooks();
    } catch (err) {
      console.error("Failed to delete saved look:", err);
    }
  };

  const applySavedLook = (look: SavedLook) => {
    setActivePreset(`saved_${look.id}`);
    if (look.lipstick_color) setLipstickColor(look.lipstick_color);
    setLipstickOpacity(look.lipstick_opacity);
    if (look.blush_color) setBlushColor(look.blush_color);
    setBlushOpacity(look.blush_opacity);
    if (look.foundation_color) setFoundationColor(look.foundation_color);
    setFoundationOpacity(look.foundation_opacity);
    if (look.eyeshadow_color) setEyeshadowColor(look.eyeshadow_color);
    setEyeshadowOpacity(look.eyeshadow_opacity);
    if (look.eyeliner_color) setEyelinerColor(look.eyeliner_color);
    setEyelinerOpacity(look.eyeliner_opacity);
    if (look.eyebrow_color) setEyebrowColor(look.eyebrow_color);
    setEyebrowOpacity(look.eyebrow_opacity);
  };

  // Auto-apply rendering when sliders change
  const isInitialMount = useRef(true);
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    if (imageBlob) {
      const delayDebounceFn = setTimeout(() => {
        applyMakeupRendering();
      }, 400);
      return () => clearTimeout(delayDebounceFn);
    }
  }, [
    lipstickColor, lipstickOpacity,
    blushColor, blushOpacity,
    foundationColor, foundationOpacity,
    eyeshadowColor, eyeshadowOpacity,
    eyelinerColor, eyelinerOpacity,
    eyebrowColor, eyebrowOpacity
  ]);

  // Turn camera stream On
  const startCamera = async () => {
    try {
      setIsCameraActive(true);
      setOriginalImage(null);
      setRenderedImage(null);
      setImageBlob(null);
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Camera access failed:", err);
      alert("Unable to access camera. Please check permissions or upload an image instead.");
      setIsCameraActive(false);
    }
  };

  // Turn camera stream Off
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsCameraActive(false);
  };

  // Capture image frame from stream
  const captureSnapshot = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth || 640;
      canvas.height = videoRef.current.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          if (blob) {
            const dataUrl = canvas.toDataURL('image/jpeg');
            setOriginalImage(dataUrl);
            setRenderedImage(dataUrl);
            setImageBlob(blob);
            stopCamera();
            runInitialFaceAnalysis(blob);
          }
        }, 'image/jpeg', 0.9);
      }
    }
  };

  // Handle uploaded image files
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageBlob(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setOriginalImage(reader.result as string);
        setRenderedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
      runInitialFaceAnalysis(file);
    }
  };

  // Step 1: Initial Face Analysis (skin tone, shape, preset defaults)
  const runInitialFaceAnalysis = async (blob: Blob) => {
    setLoading(true);
    try {
      const data = await api.analyzeFace(blob);
      setSkinTone(data.skin_tone);
      setFaceShape(data.face_shape);
      
      await api.createSession(sessionId, data.skin_tone, data.face_shape);
      fetchRecommendedProducts(data.skin_tone);
      
      if (data.recommended_presets && data.recommended_presets.office) {
        applyPresetValues('office', data.recommended_presets.office);
      }
    } catch (err: any) {
      console.error("Face analysis failed:", err);
      const errMsg = err.response?.data?.detail || err.message || "Unknown error";
      alert(`Error analyzing facial features: ${errMsg}`);
    } finally {
      setLoading(false);
    }
  };

  // Load demo model photo
  const loadDemoPhoto = async () => {
    setLoading(true);
    try {
      const response = await fetch('/src/assets/hero.png');
      const blob = await response.blob();
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setOriginalImage(reader.result as string);
        setRenderedImage(reader.result as string);
      };
      reader.readAsDataURL(blob);
      setImageBlob(blob);
      
      await runInitialFaceAnalysis(blob);
    } catch (err) {
      console.error("Failed to load demo face:", err);
      alert("Error loading demo model. Please upload your own photo instead.");
      setLoading(false);
    }
  };

  // Fetch product catalog items matching skin tone
  const fetchRecommendedProducts = async (tone: string) => {
    try {
      const products = await api.fetchProducts(tone);
      const grouped: Record<string, Product[]> = {};
      products.forEach((p: Product) => {
        if (!grouped[p.category]) grouped[p.category] = [];
        grouped[p.category].push(p);
      });
      setRecommendedProducts(grouped);
    } catch (err) {
      console.error("Failed to load catalog products:", err);
    }
  };

  // Step 2: Apply manual or preset values to render try-on
  const applyMakeupRendering = async () => {
    if (!imageBlob) return;
    
    const params = {
      lipstick_color: lipstickColor,
      lipstick_opacity: String(lipstickOpacity),
      blush_color: blushColor,
      blush_opacity: String(blushOpacity),
      foundation_color: foundationColor,
      foundation_opacity: String(foundationOpacity),
      eyeshadow_color: eyeshadowColor,
      eyeshadow_opacity: String(eyeshadowOpacity),
      eyeliner_color: eyelinerColor,
      eyeliner_opacity: String(eyelinerOpacity),
      eyebrow_color: eyebrowColor,
      eyebrow_opacity: String(eyebrowOpacity)
    };

    try {
      const resBlob = await api.renderMakeup(imageBlob, params);
      const renderedUrl = URL.createObjectURL(resBlob);
      setRenderedImage(renderedUrl);
    } catch (err) {
      console.error("Rendering failed:", err);
    }
  };

  // Load preset parameters into state variables
  const applyPresetValues = (presetName: string, config: any) => {
    setActivePreset(presetName);
    if (config.lipstick_color) setLipstickColor(config.lipstick_color);
    setLipstickOpacity(config.lipstick_opacity ?? 0.0);
    if (config.blush_color) setBlushColor(config.blush_color);
    setBlushOpacity(config.blush_opacity ?? 0.0);
    if (config.foundation_color) setFoundationColor(config.foundation_color);
    setFoundationOpacity(config.foundation_opacity ?? 0.0);
    if (config.eyeshadow_color) setEyeshadowColor(config.eyeshadow_color);
    setEyeshadowOpacity(config.eyeshadow_opacity ?? 0.0);
    if (config.eyeliner_color) setEyelinerColor(config.eyeliner_color);
    setEyelinerOpacity(config.eyeliner_opacity ?? 0.0);
    if (config.eyebrow_color) setEyebrowColor(config.eyebrow_color);
    setEyebrowOpacity(config.eyebrow_opacity ?? 0.0);
  };

  // Click on Preset Card
  const selectPreset = async (name: string) => {
    if (!skinTone || !imageBlob) return;
    setLoading(true);
    try {
      const resBlob = await api.renderMakeup(imageBlob, { look_preset: name });
      const renderedUrl = URL.createObjectURL(resBlob);
      setRenderedImage(renderedUrl);
      
      const defaultPresets: Record<string, any> = {
        office: { Cool: { lips: '#DFA8A8', lipsO: 0.5, blush: '#FFC0CB', blushO: 0.35, shadow: '#E6E6FA', shadowO: 0.3, liner: '#4A3B32', linerO: 0.4, brow: '#2C1E1A', browO: 0.35 }, Warm: { lips: '#E9967A', lipsO: 0.5, blush: '#F4A460', blushO: 0.3, shadow: '#DEB887', shadowO: 0.3, liner: '#5C4033', linerO: 0.45, brow: '#3D2B1F', browO: 0.35 }, Neutral: { lips: '#C8A2C8', lipsO: 0.5, blush: '#E6A8D7', blushO: 0.3, shadow: '#C0C0C0', shadowO: 0.35, liner: '#333333', linerO: 0.4, brow: '#262626', browO: 0.35 } },
        party: { Cool: { lips: '#800020', lipsO: 0.75, blush: '#C71585', blushO: 0.5, shadow: '#4B0082', shadowO: 0.5, liner: '#000000', linerO: 0.8, brow: '#1C1C1C', browO: 0.6 }, Warm: { lips: '#FF4500', lipsO: 0.75, blush: '#CD853F', blushO: 0.45, shadow: '#B8860B', shadowO: 0.5, liner: '#000000', linerO: 0.8, brow: '#1F140E', browO: 0.6 }, Neutral: { lips: '#DC143C', lipsO: 0.75, blush: '#DB7093', blushO: 0.45, shadow: '#708090', shadowO: 0.5, liner: '#000000', linerO: 0.8, brow: '#1A1A1A', browO: 0.6 } },
        bridal: { Cool: { lips: '#B76E79', lipsO: 0.65, blush: '#FFB7C5', blushO: 0.45, shadow: '#D8BFD8', shadowO: 0.45, liner: '#000000', linerO: 0.7, brow: '#2C1E1A', browO: 0.5 }, Warm: { lips: '#D2691E', lipsO: 0.65, blush: '#D2B48C', blushO: 0.4, shadow: '#8B4513', shadowO: 0.45, liner: '#1C110B', linerO: 0.7, brow: '#3D2B1F', browO: 0.5 }, Neutral: { lips: '#C08081', lipsO: 0.65, blush: '#E6C7C2', blushO: 0.4, shadow: '#BC8F8F', shadowO: 0.45, liner: '#1A1A1A', linerO: 0.7, brow: '#262626', browO: 0.5 } }
      };

      const set = defaultPresets[name]?.[skinTone] || {};
      setActivePreset(name);
      setLipstickColor(set.lips || '#FF0000');
      setLipstickOpacity(set.lipsO || 0.0);
      setBlushColor(set.blush || '#FFC0CB');
      setBlushOpacity(set.blushO || 0.0);
      setEyeshadowColor(set.shadow || '#DEB887');
      setEyeshadowOpacity(set.shadowO || 0.0);
      setEyelinerColor(set.liner || '#000000');
      setEyelinerOpacity(set.linerO || 0.0);
      setEyebrowColor(set.brow || '#3D2B1F');
      setEyebrowOpacity(set.browO || 0.0);
    } catch (err) {
      console.error("Failed to apply preset:", err);
    } finally {
      setLoading(false);
    }
  };

  // Stateful AI Recommendation
  const sendChatMessage = async () => {
    if (!chatInput.trim() || !imageBlob) return;
    
    const userPrompt = chatInput;
    setChatInput('');
    setChatHistory(prev => [...prev, { sender: 'user', text: userPrompt }]);
    setLoading(true);

    try {
      const data = await api.sendPrompt(sessionId, userPrompt, imageBlob);
      if (data.rendered_image) {
        setRenderedImage(data.rendered_image);
      }
      
      if (data.applied_options) {
        const opts = data.applied_options;
        if (opts.lipstick_color) setLipstickColor(opts.lipstick_color);
        setLipstickOpacity(opts.lipstick_opacity ?? 0.0);
        if (opts.blush_color) setBlushColor(opts.blush_color);
        setBlushOpacity(opts.blush_opacity ?? 0.0);
        if (opts.foundation_color) setFoundationColor(opts.foundation_color);
        setFoundationOpacity(opts.foundation_opacity ?? 0.0);
        if (opts.eyeshadow_color) setEyeshadowColor(opts.eyeshadow_color);
        setEyeshadowOpacity(opts.eyeshadow_opacity ?? 0.0);
        if (opts.eyeliner_color) setEyelinerColor(opts.eyeliner_color);
        setEyelinerOpacity(opts.eyeliner_opacity ?? 0.0);
        if (opts.eyebrow_color) setEyebrowColor(opts.eyebrow_color);
        setEyebrowOpacity(opts.eyebrow_opacity ?? 0.0);
      }

      if (data.recommended_products) {
        setRecommendedProducts(data.recommended_products);
      }

      setChatHistory(prev => [...prev, { sender: 'bot', text: data.bot_message }]);
    } catch (err) {
      console.error("Chat recommend call failed:", err);
      setChatHistory(prev => [...prev, { sender: 'bot', text: "I ran into a connection issue. Please verify your environment configurations or try again." }]);
    } finally {
      setLoading(false);
    }
  };

  // Reset parameters
  const resetAllMakeup = () => {
    setActivePreset('');
    setLipstickOpacity(0.0);
    setBlushOpacity(0.0);
    setFoundationOpacity(0.0);
    setEyeshadowOpacity(0.0);
    setEyelinerOpacity(0.0);
    setEyebrowOpacity(0.0);
    if (originalImage) setRenderedImage(originalImage);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#08080C] text-gray-100 font-sans">
      <Header skinTone={skinTone} faceShape={faceShape} />

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8 p-6 md:p-8 max-w-[1400px] w-full mx-auto animate-fade-in">
        {/* Left Column - Camera & Preview Panel */}
        <section className="lg:col-span-7 flex flex-col gap-4">
          <div className="glass-panel relative flex-1 min-h-[400px] md:min-h-[500px] overflow-hidden flex items-center justify-center bg-black/40 rounded-2xl shadow-2xl transition duration-300">
            {isCameraActive ? (
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                className="w-full h-full object-cover rounded-2xl animate-fade-in"
              />
            ) : renderedImage && originalImage ? (
              <ComparisonSlider 
                originalImage={originalImage}
                renderedImage={renderedImage}
                sliderPos={sliderPos}
                setSliderPos={setSliderPos}
                isDragging={isDragging}
                setIsDragging={setIsDragging}
              />
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-8">
                {/* Display model preview */}
                <div className="w-24 h-24 rounded-full overflow-hidden border-2 border-purple-500/30 mb-4 shadow-lg animate-pulse">
                  <img 
                    src="/src/assets/hero.png" 
                    alt="Demo Model Face Preview" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2 font-heading">Start Virtual Try-on</h3>
                <p className="text-sm text-gray-400 max-w-[320px] mb-6 leading-relaxed">
                  Turn on your camera, upload a selfie, or try it now with our sample model face!
                </p>
                <div className="flex flex-wrap gap-3 justify-center">
                  <button 
                    onClick={loadDemoPhoto}
                    className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-medium px-5 py-2.5 rounded-xl transition shadow-lg shadow-purple-600/10 cursor-pointer border-0"
                  >
                    <Sparkles className="w-4 h-4" /> Try with Demo Model
                  </button>
                  <button 
                    onClick={startCamera}
                    className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 font-medium px-5 py-2.5 rounded-xl transition cursor-pointer"
                  >
                    <Camera className="w-4 h-4" /> Start Camera
                  </button>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 font-medium px-5 py-2.5 rounded-xl transition cursor-pointer"
                  >
                    <Upload className="w-4 h-4" /> Upload Photo
                  </button>
                </div>
              </div>
            )}

            {isCameraActive && (
              <span className="absolute top-4 left-4 bg-red-600 text-white text-[10px] font-bold px-3 py-1.5 rounded-full animate-pulse flex items-center gap-1.5 z-20">
                <span className="w-1.5 h-1.5 bg-white rounded-full"></span> LIVE STREAM
              </span>
            )}

            {loading && (
              <div className="absolute inset-0 bg-black/85 backdrop-blur-sm flex flex-col items-center justify-center gap-3 z-50">
                <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
                <span className="text-sm font-semibold tracking-wide text-white">Analyzing Features...</span>
              </div>
            )}
          </div>

          {/* Action buttons under Viewport */}
          {(isCameraActive || originalImage) && (
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex gap-3">
                {isCameraActive ? (
                  <>
                    <button 
                      onClick={captureSnapshot}
                      className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition shadow-lg shadow-purple-600/10 cursor-pointer border-0"
                    >
                      Capture Photo
                    </button>
                    <button 
                      onClick={stopCamera}
                      className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 text-sm font-semibold px-5 py-2.5 rounded-xl transition cursor-pointer"
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <button 
                      onClick={startCamera}
                      className="flex items-center gap-1.5 bg-white/5 hover:bg-white/10 text-white text-sm font-semibold px-4 py-2.5 rounded-xl border border-white/10 transition cursor-pointer"
                    >
                      <Camera className="w-4 h-4" /> Reset Camera
                    </button>
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center gap-1.5 bg-white/5 hover:bg-white/10 text-white text-sm font-semibold px-4 py-2.5 rounded-xl border border-white/10 transition cursor-pointer"
                    >
                      <Upload className="w-4 h-4" /> Upload Different
                    </button>
                    <button 
                      onClick={() => setShowSaveModal(true)}
                      className="flex items-center gap-1.5 bg-purple-600/20 hover:bg-purple-600/35 text-purple-300 text-sm font-semibold px-4 py-2.5 rounded-xl border border-purple-500/30 transition cursor-pointer"
                    >
                      <Bookmark className="w-4 h-4" /> Save Look
                    </button>
                  </>
                )}
              </div>
              {originalImage && !isCameraActive && (
                <button 
                  onClick={resetAllMakeup}
                  className="flex items-center gap-1 text-xs text-gray-400 hover:text-white transition font-medium bg-transparent border-0 cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Clear Makeup
                </button>
              )}
            </div>
          )}
        </section>

        {/* Right Column - Workspaces & Controls Dashboard */}
        <section className="lg:col-span-5 flex flex-col glass-panel max-h-[640px] md:max-h-[580px] lg:max-h-[580px] overflow-hidden rounded-2xl bg-card border border-white/10 animate-fade-in">
          <div className="flex border-b border-white/10 bg-black/20">
            {['presets', 'sliders', 'chat', 'products'].map((tab) => (
              <button 
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`flex-grow py-3.5 text-xs font-semibold uppercase tracking-wider transition cursor-pointer border-0 ${activeTab === tab ? 'border-b-2 border-purple-500 text-white bg-white/[0.02]' : 'text-gray-400 hover:text-white bg-transparent'}`}
              >
                {tab === 'chat' ? 'AI Assistant' : tab === 'products' ? 'Shop' : tab}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            {activeTab === 'presets' && (
              <PresetList 
                originalImage={originalImage}
                activePreset={activePreset}
                selectPreset={selectPreset}
                savedLooks={savedLooks}
                applySavedLook={applySavedLook}
                deleteLook={deleteLook}
              />
            )}

            {activeTab === 'sliders' && (
              <MakeupSliders 
                originalImage={originalImage}
                lipstickColor={lipstickColor} lipstickOpacity={lipstickOpacity} setLipstickColor={setLipstickColor} setLipstickOpacity={setLipstickOpacity}
                blushColor={blushColor} blushOpacity={blushOpacity} setBlushColor={setBlushColor} setBlushOpacity={setBlushOpacity}
                foundationColor={foundationColor} foundationOpacity={foundationOpacity} setFoundationColor={setFoundationColor} setFoundationOpacity={setFoundationOpacity}
                eyeshadowColor={eyeshadowColor} eyeshadowOpacity={eyeshadowOpacity} setEyeshadowColor={setEyeshadowColor} setEyeshadowOpacity={setEyeshadowOpacity}
                eyelinerColor={eyelinerColor} eyelinerOpacity={eyelinerOpacity} setEyelinerColor={setEyelinerColor} setEyelinerOpacity={setEyelinerOpacity}
                eyebrowColor={eyebrowColor} eyebrowOpacity={eyebrowOpacity} setEyebrowColor={setEyebrowColor} setEyebrowOpacity={setEyebrowOpacity}
              />
            )}

            {activeTab === 'chat' && (
              <ChatAssistant 
                originalImage={originalImage}
                chatInput={chatInput}
                setChatInput={setChatInput}
                chatHistory={chatHistory}
                sendChatMessage={sendChatMessage}
                loading={loading}
              />
            )}

            {activeTab === 'products' && (
              <ProductCatalog recommendedProducts={recommendedProducts} />
            )}
          </div>
        </section>
      </main>

      {/* Save Look Dialog Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-100 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl bg-card border border-white/10 shadow-2xl">
            <h3 className="font-heading text-lg font-semibold text-white mb-2">Save Makeup Configuration</h3>
            <p className="text-xs text-gray-400 mb-4 leading-relaxed">
              Name your customized look (lipstick, blush, shadows, etc.) to bookmark it in your personal library.
            </p>
            <form onSubmit={handleSaveLookSubmit} className="flex flex-col gap-4">
              <input 
                type="text" 
                placeholder="E.g. Summer Warm Glow, Bold Indigo Night" 
                value={lookNameInput}
                onChange={(e) => setLookNameInput(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-purple-500 transition"
                autoFocus
              />
              <div className="flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => {
                    setLookNameInput('');
                    setShowSaveModal(false);
                  }}
                  className="bg-white/5 hover:bg-white/10 text-white text-xs font-semibold px-4 py-2.5 rounded-xl border border-white/10 transition cursor-pointer"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold px-5 py-2.5 rounded-xl transition cursor-pointer border-0"
                >
                  Save Look
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <footer className="border-t border-white/10 py-6 text-center text-xs text-gray-500 bg-black/10 mt-8 animate-fade-in">
        <p style={{ margin: 0 }}>© {new Date().getFullYear()} BeautyLens AI assistant. Pushing borders in modern AR beauty try-on.</p>
      </footer>

      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileUpload} 
        accept="image/*" 
        style={{ display: 'none' }}
      />
    </div>
  );
}
