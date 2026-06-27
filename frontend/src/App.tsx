import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Camera, 
  Upload, 
  Send, 
  Sliders, 
  Sparkles, 
  RotateCcw, 
  ShoppingBag, 
  Loader2,
  Check,
  Bookmark,
  Trash2
} from 'lucide-react';

interface Product {
  id: number;
  brand: string;
  name: string;
  category: string;
  hex_color: string;
  finish: string;
  suitability: string;
  price: number;
}

interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
}

interface SavedLook {
  id: number;
  name: string;
  lipstick_color: string;
  lipstick_opacity: number;
  blush_color: string;
  blush_opacity: number;
  foundation_color: string;
  foundation_opacity: number;
  eyeshadow_color: string;
  eyeshadow_opacity: number;
  eyeliner_color: string;
  eyeliner_opacity: number;
  eyebrow_color: string;
  eyebrow_opacity: number;
}

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
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Split-Screen comparison slider state & handlers
  const [sliderPos, setSliderPos] = useState(50);
  const [isDragging, setIsDragging] = useState(false);

  // Initialize Session & Load Saved Looks on Mount
  useEffect(() => {
    // 1. Get or create Session ID
    let storedSessionId = localStorage.getItem('beautylens_session_id');
    if (!storedSessionId) {
      storedSessionId = 'session_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
      localStorage.setItem('beautylens_session_id', storedSessionId);
    }
    setSessionId(storedSessionId);
    
    // 2. Fetch Saved Looks catalog
    fetchSavedLooks();
    
    // 3. Fetch past chat history logs for session
    fetchChatHistory(storedSessionId);
  }, []);

  const fetchChatHistory = async (sessId: string) => {
    try {
      const res = await axios.get(`/api/v1/sessions/${sessId}/chat`);
      if (res.data && res.data.length > 0) {
        setChatHistory(res.data.map((msg: any) => ({
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
      const res = await axios.get('/api/v1/looks');
      setSavedLooks(res.data);
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

      await axios.post('/api/v1/looks', payload);
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
      await axios.delete(`/api/v1/looks/${id}`);
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

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const pos = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(pos);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    if (e.touches[0]) {
      handleMove(e.touches[0].clientX);
    }
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
    const formData = new FormData();
    formData.append('image', blob, 'selfie.jpg');

    try {
      const res = await axios.post('/api/v1/analyze-face', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = res.data;
      setSkinTone(data.skin_tone);
      setFaceShape(data.face_shape);
      
      // Initialize stateful session on backend
      await axios.post('/api/v1/sessions', {
        id: sessionId,
        skin_tone: data.skin_tone,
        face_shape: data.face_shape
      });
      
      fetchRecommendedProducts(data.skin_tone, data.face_shape);
      
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

  // Fetch product catalog items matching skin tone
  const fetchRecommendedProducts = async (tone: string, shape: string) => {
    try {
      const res = await axios.get(`/api/v1/products?suitability=${tone}`);
      const grouped: Record<string, Product[]> = {};
      res.data.forEach((p: Product) => {
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
    
    const formData = new FormData();
    formData.append('image', imageBlob, 'selfie.jpg');
    formData.append('lipstick_color', lipstickColor);
    formData.append('lipstick_opacity', String(lipstickOpacity));
    formData.append('blush_color', blushColor);
    formData.append('blush_opacity', String(blushOpacity));
    formData.append('foundation_color', foundationColor);
    formData.append('foundation_opacity', String(foundationOpacity));
    formData.append('eyeshadow_color', eyeshadowColor);
    formData.append('eyeshadow_opacity', String(eyeshadowOpacity));
    formData.append('eyeliner_color', eyelinerColor);
    formData.append('eyeliner_opacity', String(eyelinerOpacity));
    formData.append('eyebrow_color', eyebrowColor);
    formData.append('eyebrow_opacity', String(eyebrowOpacity));

    try {
      const res = await axios.post('/api/v1/render-makeup', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });
      
      const renderedUrl = URL.createObjectURL(res.data);
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
    if (!skinTone) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', imageBlob!, 'selfie.jpg');
      formData.append('look_preset', name);

      const res = await axios.post('/api/v1/render-makeup', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });

      const renderedUrl = URL.createObjectURL(res.data);
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

    const formData = new FormData();
    formData.append('prompt', userPrompt);
    formData.append('image', imageBlob, 'selfie.jpg');

    try {
      const res = await axios.post(`/api/v1/sessions/${sessionId}/prompt`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const data = res.data;
      if (data.rendered_image) {
        setRenderedImage(data.rendered_image);
      }
      
      // Update UI controllers to reflect LLM resolved settings
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
      {/* Header Navigation */}
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

      {/* Main Workspace Grid */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8 p-6 md:p-8 max-w-[1400px] w-full mx-auto">
        {/* Left Column - Camera & Preview Panel */}
        <section className="lg:col-span-7 flex flex-col gap-4">
          <div 
            ref={containerRef}
            className="glass-panel relative flex-1 min-h-[400px] md:min-h-[500px] overflow-hidden flex items-center justify-center bg-black/40 rounded-2xl shadow-2xl transition duration-300"
            onMouseMove={handleMouseMove}
            onTouchMove={handleTouchMove}
            onMouseUp={() => setIsDragging(false)}
            onMouseLeave={() => setIsDragging(false)}
            onTouchEnd={() => setIsDragging(false)}
          >
            {isCameraActive ? (
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                className="w-full h-full object-cover rounded-2xl"
              />
            ) : renderedImage ? (
              <div className="comparison-container w-full h-full max-h-[520px]">
                <img 
                  src={renderedImage} 
                  alt="Rendered face" 
                  className="comparison-image"
                />
                
                <img 
                  src={originalImage!} 
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
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-8">
                <div className="w-16 h-16 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4 animate-bounce">
                  <Sparkles className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2 font-heading">Start Virtual Try-on</h3>
                <p className="text-sm text-gray-400 max-w-[320px] mb-6 leading-relaxed">
                  Turn on your camera or upload a selfie to instantly test cosmetics and see recommendations.
                </p>
                <div className="flex gap-4">
                  <button 
                    onClick={startCamera}
                    className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-medium px-5 py-2.5 rounded-xl transition shadow-lg shadow-purple-600/10 cursor-pointer border-0"
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

            {/* Live indicator overlay */}
            {isCameraActive && (
              <span className="absolute top-4 left-4 bg-red-600 text-white text-[10px] font-bold px-3 py-1.5 rounded-full animate-pulse flex items-center gap-1.5 z-20">
                <span className="w-1.5 h-1.5 bg-white rounded-full"></span> LIVE STREAM
              </span>
            )}

            {/* Spinner loader overlay */}
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
                      <Bookmark className="w-4 h-4" /> Save Current Look
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
        <section className="lg:col-span-5 flex flex-col glass-panel max-h-[640px] md:max-h-[580px] lg:max-h-[580px] overflow-hidden rounded-2xl bg-card border border-white/10">
          {/* Navigation Tab Menu */}
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

          {/* Active Tab Workspace Viewports */}
          <div className="flex-1 overflow-y-auto p-6">
            
            {/* Presets Grid Tab */}
            {activeTab === 'presets' && (
              <div className="flex flex-col gap-6 fade-in">
                {/* Visual Occasions Presets List */}
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

                {/* Saved Looks Library Section */}
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
            )}

            {/* Manual Custom Sliders Tab */}
            {activeTab === 'sliders' && (
              <div className="flex flex-col gap-6 fade-in">
                {!originalImage ? (
                  <div className="text-center py-12 text-sm text-gray-500">
                    Upload or capture a photo to customize your sliders.
                  </div>
                ) : (
                  <div className="flex flex-col gap-5">
                    {[
                      { label: 'LIPSTICK', color: lipstickColor, opacity: lipstickOpacity, setColor: setLipstickColor, setOpacity: setLipstickOpacity, defO: 0.6, swatches: ['#DFA8A8', '#E9967A', '#C41E3A', '#D15276', '#4A0E17', '#800020', '#BC8F8F'] },
                      { label: 'BLUSH', color: blushColor, opacity: blushOpacity, setColor: setBlushColor, setOpacity: setBlushOpacity, defO: 0.4, swatches: ['#FFC0CB', '#FFB7C5', '#F4A460', '#E9967A', '#DC143C'] },
                      { label: 'FOUNDATION', color: foundationColor, opacity: foundationOpacity, setColor: setFoundationColor, setOpacity: setFoundationOpacity, defO: 0.3, swatches: ['#F6D5C3', '#F3D2C1', '#E8C39E', '#DAB088', '#C59A6F'] },
                      { label: 'EYESHADOW', color: eyeshadowColor, opacity: eyeshadowOpacity, setColor: setEyeshadowColor, setOpacity: setEyeshadowOpacity, defO: 0.4, swatches: ['#E6E6FA', '#DEB887', '#BC8F8F', '#708090', '#36454F'] },
                      { label: 'EYELINER', color: eyelinerColor, opacity: eyelinerOpacity, setColor: setEyelinerColor, setOpacity: setEyelinerOpacity, defO: 0.6, swatches: ['#000000', '#3D2B1F', '#5C4033', '#191970', '#0E3A20'] },
                      { label: 'EYEBROWS', color: eyebrowColor, opacity: eyebrowOpacity, setColor: setEyebrowColor, setOpacity: setEyebrowOpacity, defO: 0.4, swatches: ['#1C1C1C', '#2C1E1A', '#3D2B1F', '#5C4033'] }
                    ].map((grp) => (
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
                            className="flex-1 accent-purple-500 bg-white/10 h-1 rounded-lg appearance-none cursor-pointer"
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
                )}
              </div>
            )}

            {/* AI Assistant Chat Tab */}
            {activeTab === 'chat' && (
              <div className="chat-container fade-in flex flex-col justify-between h-[450px]">
                <div className="chat-transcript flex-grow overflow-y-auto flex flex-col gap-3 max-h-[350px] pr-2 scroll-smooth">
                  {chatHistory.map((msg, i) => (
                    <div 
                      key={i} 
                      className={`chat-bubble ${msg.sender === 'user' ? 'user bg-purple-600 text-white self-end rounded-tr-none' : 'bot bg-white/5 border border-white/10 text-gray-300 self-start rounded-tl-none'}`}
                    >
                      {msg.text}
                    </div>
                  ))}
                </div>

                {!originalImage ? (
                  <div className="text-center py-6 text-sm text-gray-500">
                    Upload or capture a photo to start chatting with the AI.
                  </div>
                ) : (
                  <div className="chat-input-bar">
                    <input 
                      type="text" 
                      placeholder="Type a look request (e.g. 'purple eyeshadow')..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && sendChatMessage()}
                      className="chat-text-input"
                    />
                    <button 
                      onClick={sendChatMessage}
                      disabled={loading}
                      className="chat-send-btn flex items-center justify-center disabled:opacity-50 border-0"
                    >
                      {loading ? <Loader2 className="w-4.5 h-4.5 animate-spin" /> : <Send className="w-4 h-4" />}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Shopping Catalog Products Tab */}
            {activeTab === 'products' && (
              <div className="shop-categories-list fade-in">
                <div className="shop-header">
                  <h4 className="shop-title">Recommended Shop Catalog</h4>
                  <p className="shop-subtitle">Cosmetics from our catalog matching your skin undertone.</p>
                </div>
                
                {Object.keys(recommendedProducts).length === 0 ? (
                  <div className="text-center py-12 text-sm text-gray-500">
                    No recommendations found. Upload a photo to scan products.
                  </div>
                ) : (
                  <div className="shop-categories-list max-h-[350px] overflow-y-auto pr-1">
                    {Object.entries(recommendedProducts).map(([category, items]) => (
                      <div key={category} className="shop-category-section mb-4">
                        <h5 className="shop-category-title">{category}</h5>
                        <div>
                          {items.map((prod) => (
                            <div 
                              key={prod.id} 
                              className="product-item"
                            >
                              <div className="product-item-details">
                                <span 
                                  className="product-swatch"
                                  style={{ backgroundColor: prod.hex_color }}
                                />
                                <div className="product-meta">
                                  <span className="product-name">{prod.name}</span>
                                  <span className="product-brand-finish">{prod.brand} • {prod.finish}</span>
                                </div>
                              </div>
                              <div className="product-actions">
                                <span className="product-price">${prod.price.toFixed(2)}</span>
                                <button 
                                  onClick={() => alert(`Redirecting to shop item: ${prod.brand} ${prod.name}`)}
                                  className="product-buy-btn flex items-center justify-center border-0 cursor-pointer"
                                >
                                  <ShoppingBag className="w-4 h-4" />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
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

      {/* Footer Branding */}
      <footer className="border-t border-white/10 py-6 text-center text-xs text-gray-500 bg-black/10 mt-8">
        <p style={{ margin: 0 }}>© {new Date().getFullYear()} BeautyLens AI assistant. Pushing borders in modern AR beauty try-on.</p>
      </footer>

      {/* Hidden file input */}
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
