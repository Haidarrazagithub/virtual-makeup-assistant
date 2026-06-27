import httpx
import json
import logging
from typing import Dict, Any, Optional
from app.core.settings import settings

logger = logging.getLogger(__name__)


class GenAIService:
    """
    Translates user chat prompts into structured makeup parameters.
    """

    @classmethod
    async def translate_prompt(
        cls,
        prompt: str,
        skin_tone: str,
        face_shape: str
    ) -> Dict[str, Any]:
        """
        Translates raw text instructions into rendering configurations.
        Uses OpenAI or Gemini if configured, else falls back to a rules-based parser.
        """
        prompt_lower = prompt.lower()
        
        # 1. Attempt using Gemini API if configured
        if settings.GEMINI_API_KEY:
            try:
                result = await cls._call_gemini_api(prompt, skin_tone, face_shape)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Gemini API call failed, falling back: {e}")

        # 2. Attempt using OpenAI API if configured
        if settings.OPENAI_API_KEY:
            try:
                result = await cls._call_openai_api(prompt, skin_tone, face_shape)
                if result:
                    return result
            except Exception as e:
                logger.error(f"OpenAI API call failed, falling back: {e}")

        # 3. Fallback: Rules-based local parsing
        return cls._local_rule_parser(prompt_lower)

    @classmethod
    async def _call_gemini_api(cls, prompt: str, skin_tone: str, face_shape: str) -> Optional[Dict[str, Any]]:
        # Stable Gemini 2.0 API endpoint
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
        
        headers = {
            "x-goog-api-key": settings.GEMINI_API_KEY,
            "Content-Type": "application/json"
        }
        
        system_instruction = (
            "You are a makeup assistant. Analyze the user request, skin tone, and face shape, "
            "and output a JSON object containing keys: "
            "look_preset (office, party, bridal, or null), lipstick_color (hex or null), "
            "lipstick_opacity (float 0.0-1.0 or null), blush_color (hex or null), "
            "blush_opacity (float 0.0-1.0 or null), foundation_color (hex or null), "
            "foundation_opacity (float 0.0-1.0 or null), eyeshadow_color (hex or null), "
            "eyeshadow_opacity (float 0.0-1.0 or null), eyeliner_color (hex or null), "
            "eyeliner_opacity (float 0.0-1.0 or null), eyebrow_color (hex or null), "
            "eyebrow_opacity (float 0.0-1.0 or null). "
            "Output ONLY the JSON object. Do not include markdown tags."
        )
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"User Prompt: {prompt}\nUser Skin Tone: {skin_tone}\nUser Face Shape: {face_shape}"
                }]
            }],
            "systemInstruction": {
                "parts": [{
                    "text": system_instruction
                }]
            },
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        return None

    @classmethod
    async def _call_openai_api(cls, prompt: str, skin_tone: str, face_shape: str) -> Optional[Dict[str, Any]]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a makeup assistant. Parse requests and return a JSON object with keys: "
                        "look_preset, lipstick_color, lipstick_opacity, blush_color, blush_opacity, "
                        "foundation_color, foundation_opacity, eyeshadow_color, eyeshadow_opacity, "
                        "eyeliner_color, eyeliner_opacity, eyebrow_color, eyebrow_opacity."
                    )
                },
                {
                    "role": "user",
                    "content": f"Prompt: {prompt}\nSkin: {skin_tone}\nShape: {face_shape}"
                }
            ]
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=headers, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return json.loads(text)
        return None

    @classmethod
    def _local_rule_parser(cls, prompt_lower: str) -> Dict[str, Any]:
        """
        Regex/keyword matching fallback to construct look profiles locally.
        """
        opts: Dict[str, Any] = {
            "look_preset": None,
            "lipstick_color": None,
            "lipstick_opacity": 0.0,
            "blush_color": None,
            "blush_opacity": 0.0,
            "foundation_color": None,
            "foundation_opacity": 0.0,
            "eyeshadow_color": None,
            "eyeshadow_opacity": 0.0,
            "eyeliner_color": None,
            "eyeliner_opacity": 0.0,
            "eyebrow_color": None,
            "eyebrow_opacity": 0.0
        }

        # 1. Preset Matching
        if "office" in prompt_lower or "natural" in prompt_lower:
            opts["look_preset"] = "office"
        elif "party" in prompt_lower or "glam" in prompt_lower or "festival" in prompt_lower:
            opts["look_preset"] = "party"
        elif "bridal" in prompt_lower or "wedding" in prompt_lower:
            opts["look_preset"] = "bridal"

        # 2. Lipstick Customization
        if "red" in prompt_lower and ("lipstick" in prompt_lower or "lip" in prompt_lower):
            opts["lipstick_color"] = "#E0115F"  # Ruby Red
            opts["lipstick_opacity"] = 0.75
        elif "pink" in prompt_lower and ("lipstick" in prompt_lower or "lip" in prompt_lower):
            opts["lipstick_color"] = "#FFC0CB"  # Pink
            opts["lipstick_opacity"] = 0.6
        elif "coral" in prompt_lower and ("lipstick" in prompt_lower or "lip" in prompt_lower):
            opts["lipstick_color"] = "#E9967A"  # Coral
            opts["lipstick_opacity"] = 0.6

        # 3. Eyeshadow Customization
        if "purple" in prompt_lower or "lavender" in prompt_lower:
            opts["eyeshadow_color"] = "#E6E6FA"
            opts["eyeshadow_opacity"] = 0.5
        elif "gold" in prompt_lower or "brown" in prompt_lower:
            opts["eyeshadow_color"] = "#DEB887"
            opts["eyeshadow_opacity"] = 0.5

        # 4. Eyeliner Customization
        if "eyeliner" in prompt_lower:
            if "brown" in prompt_lower:
                opts["eyeliner_color"] = "#5C4033"
            else:
                opts["eyeliner_color"] = "#000000"  # Default black
            opts["eyeliner_opacity"] = 0.75

        # 5. Eyebrows Customization
        if "eyebrow" in prompt_lower or "brow" in prompt_lower:
            if "black" in prompt_lower:
                opts["eyebrow_color"] = "#1C1C1C"
            else:
                opts["eyebrow_color"] = "#3D2B1F"  # Default brown
            opts["eyebrow_opacity"] = 0.5

        return opts
