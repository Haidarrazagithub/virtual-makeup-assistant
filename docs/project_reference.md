# Virtual Makeup Assistant - Developer Project Reference

This document serves as a quick reference for developers and agents to understand the project structure, API endpoints, face mesh landmark groupings, and classification heuristics without having to read all backend files.

---

## 📁 Directory Structure

```text
virtual-makeup-assistant/
├── assets/                  # Public assets & static images
├── docs/
│   └── project_reference.md # This document
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   └── face_analysis.py # POST /api/v1/analyze-face
│   │   │       └── router.py            # API Route aggregator
│   │   ├── constants/
│   │   │   └── landmarks.py             # Feature indices mapping list definitions
│   │   ├── main.py                      # FastAPI App initialization & /health
│   │   ├── schemas/
│   │   │   ├── face_analysis.py         # FaceAnalysisResponse schema
│   │   │   └── recommendation.py        # Recommendation engine schemas
│   │   ├── services/
│   │   │   └── vision/
│   │   │       ├── face_analysis_service.py # MediaPipe orchestrator
│   │   │       ├── image_service.py         # Decodes incoming uploaded files
│   │   │       ├── image_validator.py       # Validates file formats/sizes
│   │   │       ├── landmark_service.py      # Face regions extraction helpers
│   │   │       └── skin_tone_service.py     # Cheek ROI classification
│   │   └── utils/
│   └── tests/                           # Project test scripts
```

---

## 🌐 API Endpoints

### 1. Health Probe
- **Path:** `GET /health`
- **Response:**
  ```json
  {
      "status": "healthy",
      "application": "BeautyLens AI"
  }
  ```

### 2. Face Analysis
- **Path:** `POST /api/v1/analyze-face`
- **Request Body (Multipart Form):**
  - `image`: File (image upload, validated for formats: `.jpg`, `.jpeg`, `.png`)
- **Response:**
  ```json
  {
      "face_detected": true,
      "face_count": 1,
      "landmark_count": 468,
      "skin_tone": "Warm",
      "face_shape": "Oval"
  }
  ```

---

## 📍 Landmark Groupings (MediaPipe indices)

Definitions located in [landmarks.py](file:///d:/privet_pr/virtual-makeup-assistant/backend/app/constants/landmarks.py):

| Region | Indices / Description |
| :--- | :--- |
| `LIPS` | Outer and inner lip contour indices. |
| `LEFT_EYE` | Left eye boundary indices. |
| `RIGHT_EYE` | Right eye boundary indices. |
| `LEFT_CHEEK` | Region defining the left cheek (used for skin tone sampling). |
| `RIGHT_CHEEK` | Region defining the right cheek (used for skin tone sampling). |
| `LEFT_EYEBROW` | Left eyebrow contour. |
| `RIGHT_EYEBROW` | Right eyebrow contour. |
| `FACE_OUTLINE` | Full facial silhouette / jawline boundary. |

---

## 🎨 Skin Tone Classification

Implemented in [skin_tone_service.py](file:///d:/privet_pr/virtual-makeup-assistant/backend/app/services/vision/skin_tone_service.py):
1. **Cheek ROI Extraction:** Creates a mask covering the polygons defined by `LEFT_CHEEK` and `RIGHT_CHEEK`.
2. **Mean Color:** Calculates average RGB of the masked cheek pixels.
3. **HSV conversion:** Maps average RGB to HSV.
4. **Undertone Decision Rule:**
   - **Cool:** $Hue < 20^\circ$ (leans red/pink).
   - **Neutral:** $20^\circ \leq Hue \leq 28^\circ$.
   - **Warm:** $Hue > 28^\circ$ (leans yellow/golden).

---

## 📐 Face Shape Classification

Implemented in [face_shape_service.py](file:///d:/privet_pr/virtual-makeup-assistant/backend/app/services/vision/face_shape_service.py):
1. **Key Dimensions:**
   - **Height ($H$):** Distance between top forehead center (10) and chin bottom (152).
   - **Cheek Width ($W_{\text{cheek}}$):** Distance between widest cheekbones (234 to 454).
   - **Forehead Width ($W_{\text{forehead}}$):** Distance between outer temple/forehead points (103 to 332).
   - **Jaw Width ($W_{\text{jaw}}$):** Distance between jaw corners (136 to 365).
2. **Proportion Ratios:**
   - $\text{aspect\_ratio} = H / W_{\text{cheek}}$
   - $\text{forehead\_cheek\_ratio} = W_{\text{forehead}} / W_{\text{cheek}}$
   - $\text{jaw\_cheek\_ratio} = W_{\text{jaw}} / W_{\text{cheek}}$
3. **Decision Rules:**
   - **Long:** $\text{aspect\_ratio} > 1.35$.
   - **Heart:** $\text{forehead\_cheek\_ratio} > 0.95$ and $\text{jaw\_cheek\_ratio} < 0.85$.
   - **Diamond:** $\text{forehead\_cheek\_ratio} < 0.90$ and $\text{jaw\_cheek\_ratio} < 0.80$.
   - **Square:** $\text{aspect\_ratio} \leq 1.35$ and $\text{jaw\_cheek\_ratio} > 0.85$ and $\text{forehead\_cheek\_ratio} > 0.90$.
   - **Round:** $\text{aspect\_ratio} \leq 1.30$ and $0.75 < \text{jaw\_cheek\_ratio} \leq 0.85$.
   - **Oval:** Default category for balanced proportions.

---

## 💄 Makeup Rendering Engine

### 1. Endpoint: Render Makeup
- **Path:** `POST /api/v1/render-makeup`
- **Request (Multipart Form):**
  - `image`: File (upload selfie)
  - `lipstick_color` (hex string, e.g. `"#E0115F"`)
  - `lipstick_opacity` (float `[0.0, 1.0]`)
  - `blush_color` (hex string)
  - `blush_opacity` (float `[0.0, 1.0]`)
  - `foundation_color` (hex string)
  - `foundation_opacity` (float `[0.0, 1.0]`)
  - `eyeshadow_color` (hex string)
  - `eyeshadow_opacity` (float `[0.0, 1.0]`)
- **Response:**
  - `image/jpeg` byte stream of the rendered photo.

### 2. Rendering Implementation Details
Implemented in [makeup_rendering_service.py](file:///d:/privet_pr/virtual-makeup-assistant/backend/app/services/vision/makeup_rendering_service.py):
- **Anti-Aliasing:** All regions employ float alpha-mask multiplication to eliminate harsh pixels.
- **Lipstick:** Draws `UPPER_LIP` and `LOWER_LIP` boundary loops; applies a small $(7,7)$ Gaussian blur.
- **Blush:** Determines center points of `LEFT_CHEEK` and `RIGHT_CHEEK`; draws radial shapes blurred with a $(55,55)$ Gaussian blur.
- **Foundation:** Mask covers the face outline silhouette but excludes eyeballs, eyebrows, and lip zones. Softened with a $(21,21)$ Gaussian blur.
- **Eyeshadow:** Projects the upper eyelid line upwards by $4.5\%$ of the total face height, draws eyeshadow polygon loops above the eyes, and applies a $(21,21)$ Gaussian blur.
- **Eyeliner:** Draws curves along the upper eyelids (Left: `[33, 160, 159, 158, 157, 173, 133]`, Right: `[263, 387, 386, 385, 384, 398, 362]`) with a $2\text{px}$ thickness, smoothed with a small $(3,3)$ Gaussian blur.
- **Eyebrows:** Draws filled eyebrow polygons (Left: `LEFT_EYEBROW`, Right: `RIGHT_EYEBROW`) blurred with a $(9,9)$ Gaussian blur.

---

## 🗄️ Product Catalog & Database

Implemented using a local SQLite database (`beauty_lens.db`) and SQLAlchemy models:

### 1. Database Model (`Product`)
- `id` (Integer, Primary Key)
- `brand` (String) - e.g. "MAC", "NARS", "Fenty Beauty"
- `name` (String) - e.g. "Ruby Red Matte", "Warm Sand Beige"
- `category` (String) - `lipstick`, `blush`, `eyeshadow`, `foundation`, `eyeliner`, `eyebrows`
- `hex_color` (String) - e.g. `"#800020"`
- `finish` (String) - `Matte`, `Satin`, `Glossy`
- `suitability` (String) - `Warm`, `Cool`, `Neutral` skin undertone suitability
- `price` (Float)

### 2. Seeding Data
Seeded with $30+$ cosmetic products categorized by undertone suitability. Seeding can be re-run at any time using:
```powershell
python -m app.utils.seed_products
```

---

## 🤖 AI Recommendations & Prompt Parsing

### 1. Endpoint: Retrieve Products
- **Path:** `GET /api/v1/products`
- **Params:** Optional query filters `category` or `suitability`.
- **Response:** JSON list of matching catalog products.

### 2. Endpoint: Intelligent Look Recommendation
- **Path:** `POST /api/v1/recommend-look`
- **Request (Multipart Form):**
  - `image`: File (upload selfie)
  - `prompt`: String (default: `"Give me natural office makeup"`)
- **Pipeline:**
  1. Detects face landmarks, skin tone (Warm/Cool/Neutral), and face shape (Oval/Round/Square/etc.).
  2. Passes prompt + attributes to `GenAIService`. Uses Google Gemini / OpenAI (or fallback rules parser) to extract presets (`office`/`party`/`bridal`) and custom color overrides from free text.
  3. Merges overrides and applies virtual try-on rendering.
  4. Queries DB for matching products suited to the user's skin tone.
- **Response (JSON):**
  ```json
  {
    "detected_skin_tone": "Cool",
    "detected_face_shape": "Diamond",
    "resolved_preset": "party",
    "applied_options": {
      "lipstick_color": "#E0115F",
      "lipstick_opacity": 0.75,
      ...
    },
    "recommended_products": {
      "lipstick": [...],
      "blush": [...],
      ...
    },
    "rendered_image": "data:image/jpeg;base64,..."
  }
  ```



