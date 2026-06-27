import axios from 'axios';

export interface Product {
  id: number;
  brand: string;
  name: string;
  category: string;
  hex_color: string;
  finish: string;
  suitability: string;
  price: number;
}

export interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
}

export interface SavedLook {
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

export const api = {
  async analyzeFace(imageBlob: Blob) {
    const formData = new FormData();
    formData.append('image', imageBlob, 'selfie.jpg');
    const res = await axios.post('/api/v1/analyze-face', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async renderMakeup(imageBlob: Blob, params: Record<string, string>) {
    const formData = new FormData();
    formData.append('image', imageBlob, 'selfie.jpg');
    Object.entries(params).forEach(([key, val]) => {
      formData.append(key, val);
    });
    const res = await axios.post('/api/v1/render-makeup', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    });
    return res.data;
  },

  async fetchHistory(sessionId: string): Promise<ChatMessage[]> {
    const res = await axios.get(`/api/v1/sessions/${sessionId}/chat`);
    return res.data;
  },

  async sendPrompt(sessionId: string, prompt: string, imageBlob: Blob) {
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('image', imageBlob, 'selfie.jpg');
    const res = await axios.post(`/api/v1/sessions/${sessionId}/prompt`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async fetchProducts(skinTone: string): Promise<Product[]> {
    const res = await axios.get(`/api/v1/products?suitability=${skinTone}`);
    return res.data;
  },

  async createSession(sessionId: string, skinTone: string, faceShape: string) {
    const res = await axios.post('/api/v1/sessions', {
      id: sessionId,
      skin_tone: skinTone,
      face_shape: faceShape
    });
    return res.data;
  },

  // Saved Looks CRUD
  async fetchSavedLooks(): Promise<SavedLook[]> {
    const res = await axios.get('/api/v1/looks');
    return res.data;
  },

  async createSavedLook(payload: Omit<SavedLook, 'id'>) {
    const res = await axios.post('/api/v1/looks', payload);
    return res.data;
  },

  async deleteSavedLook(id: number) {
    const res = await axios.delete(`/api/v1/looks/${id}`);
    return res.data;
  }
};
