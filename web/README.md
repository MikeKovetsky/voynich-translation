# Voynich Manuscript Viewer

A React-based web viewer for the Voynich Manuscript.

## Setup

1. Install dependencies:
   ```bash
   cd web
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

## Data Structure

- **Images**: The manuscript images are served from `public/manuscript/` (symlinked to the project root `images/` folder).
- **Pages**: The list of page filenames is in `src/data/pages.json`.
- **Translations**: Translation overlays are defined in `src/data/translations.json`.

### Translation Format
The translation file maps image filenames to an array of text overlays:

```json
{
  "f1r.jpg": [
    { 
      "top": "10%", 
      "left": "10%", 
      "text": "Translated text here..." 
    }
  ]
}
```
