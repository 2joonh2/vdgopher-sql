# Pyodide Configuration Guide

## Overview

VDGOPHER for SQL can run entirely in the browser using **Pyodide**, which compiles Python to WebAssembly. This eliminates the need for a backend server and makes the application deployable to static hosting services like GitHub Pages.

## How It Works

1. **Pyodide Web Worker** loads Python runtime (50MB, cached after first load)
2. **SQLGlot** (Python library) runs in the browser via WebAssembly
3. **SQL queries** are analyzed client-side with zero latency
4. **Complete privacy** - queries never leave your machine

## Configuration

### Environment Variables

Create `frontend/.env.local`:

```env
# Use Pyodide (default)
VITE_USE_PYODIDE=true

# Or fall back to backend API
VITE_USE_PYODIDE=false
VITE_API_URL=http://localhost:8000
```

### Build Configuration

`vite.config.ts` automatically includes Web Worker support:
```typescript
worker: {
  format: 'es',
},
```

## Local Development

### Option 1: Pyodide (Recommended - No Backend Needed)
```bash
cd frontend
npm install
npm run dev
```

The app will:
- Load Pyodide from CDN on startup
- Initialize Python runtime in a Web Worker
- Process SQL queries in the browser
- Display results in React Flow graph

⏱️ **First load**: ~5-10 seconds (downloading Pyodide)
⚡ **Subsequent queries**: Instant (no network latency)

### Option 2: Backend API
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd frontend
VITE_USE_PYODIDE=false npm run dev
```

## Production Deployment

### GitHub Pages (Pyodide + Static Files)

This is the **recommended** approach - complete independence:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Enable Pyodide for GitHub Pages"
   git push origin main
   ```

2. **GitHub Actions** runs automatically:
   - Builds with `VITE_USE_PYODIDE=true`
   - Deploys to `gh-pages` branch

3. **Result**: `https://yourusername.github.io/vdgopher_for_sql/`

✨ **Benefits:**
- No backend server needed
- Instant queries (no API latency)
- Works offline after first load
- Unlimited GitHub Pages bandwidth

### Alternative: Deploy with Backend

If you prefer having a backend server:

1. **Deploy FastAPI to Vercel/Railway/Render**
   ```bash
   cd backend
   vercel deploy
   ```

2. **Update frontend config**:
   ```env
   VITE_USE_PYODIDE=false
   VITE_API_URL=https://your-backend-api.com
   ```

3. **Deploy frontend** to Netlify/Vercel/GitHub Pages

## Performance Considerations

### Bundle Size
- **Pyodide**: ~50MB (gzipped: ~15-20MB)
- **First load**: Downloaded from CDN, cached by browser
- **Subsequent loads**: Uses cached version

### Startup Time
| Phase | Time |
|-------|------|
| HTML parse | <1s |
| JS bundle load | <1s |
| React mount | <1s |
| Pyodide download (first time only) | 3-5s |
| SQLGlot package install | 2-3s |
| **Ready for queries** | ~10-12s |

### Query Performance
- **Simple SELECT**: <100ms
- **Complex JOIN/UNION**: <500ms
- **Very large queries**: 1-2s

*All processing happens in the browser - no network latency!*

## Troubleshooting

### "Failed to initialize Pyodide"
- Check browser console for errors
- Ensure CDN is accessible: `https://cdn.jsdelivr.net/pyodide/`
- Try clearing browser cache

### Slow performance
- First load includes downloading Pyodide (~50MB)
- This is normal and cached for subsequent visits
- Check Network tab in DevTools to verify caching

### Worker not loading
- Ensure `frontend/src/workers/pyodide.worker.ts` exists
- Check that Vite worker configuration is correct
- Verify browser supports Web Workers and WebAssembly

### SQLGlot import errors
- Ensure `sqlglot` package is installed in Pyodide
- Check browser console for specific error messages
- Try hard-refreshing the page

## Advanced Configuration

### Custom Pyodide URL
```typescript
// In pyodide.worker.ts
importScripts('https://custom-cdn.com/pyodide-v0.24.0/full/pyodide.js');
```

### Additional Python Packages
```typescript
// In pyodide.worker.ts
await pyodide.loadPackage(['sqlglot', 'custom-package']);
```

### Offline Support
Pyodide can work offline once cached. For guaranteed offline support:
1. Use Workbox/Service Worker for caching
2. Include Pyodide in build artifacts
3. Deploy as Progressive Web App (PWA)

## Switching Between Modes

### Pyodide → Backend
```bash
# Update env
echo "VITE_USE_PYODIDE=false" > frontend/.env.local

# Run with backend
cd backend && python main.py &
cd frontend && npm run dev
```

### Backend → Pyodide
```bash
# Update env
echo "VITE_USE_PYODIDE=true" > frontend/.env.local

# Run with Pyodide only
cd frontend && npm run dev
```

## API Integration

The app automatically detects which mode to use:

```typescript
import api, { initializePyodideWorker } from './config/api';

// Auto-detect based on VITE_USE_PYODIDE
const result = await api.parseSql('SELECT * FROM table', 'tsql');

// Or explicitly choose
if (api.usePyodide) {
  await initializePyodideWorker();
  const result = await api.parseSqlWithPyodide(sql);
} else {
  const result = await api.parseSqlWithBackend(sql);
}
```

## Security Notes

- **SQL queries are NOT sent anywhere** when using Pyodide
- No analytics, no telemetry, no server logs
- All processing happens in your browser
- Source code is visible (frontend is JavaScript)
- Ideal for sensitive/confidential SQL analysis

## References

- [Pyodide Documentation](https://pyodide.org/)
- [SQLGlot Repository](https://github.com/tobymao/sqlglot)
- [GitHub Pages Deployment](https://docs.github.com/en/pages)
- [Vite Worker Configuration](https://vitejs.dev/guide/features.html#web-workers)
