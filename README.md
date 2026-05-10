# VDGOPHER for SQL

Advanced SQL Data Lineage Visualizer with Mathematical Symmetry Engine.

## Structure
- /backend: FastAPI Engine (Optional - for local development only)
- /frontend: React Flow UI with Pyodide

## How to Run Locally

### Option 1: Browser-Based with Pyodide (Recommended)
```bash
cd frontend
npm install
npm run dev
```
The frontend will run on `http://localhost:5173` and use Pyodide for SQL analysis in the browser.
**No backend server needed!**

### Option 2: With Backend Server
```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
python main.py
```

```bash
# Terminal 2: Start frontend
cd frontend
npm install
VITE_USE_PYODIDE=false npm run dev
```

### Quick Start with Batch File
Simply run `run.bat` to start both backend and frontend in separate terminal windows.

---

## GitHub Pages Deployment (Recommended)

### Why Pyodide?
- ✅ **No backend required** - Everything runs in the browser
- ✅ **True static site** - Deployable to GitHub Pages, Netlify, Vercel
- ✅ **Fast** - No network latency for SQL parsing
- ✅ **Private** - SQL queries never leave your computer

### Prerequisites
- GitHub account and repository
- Repository can be public or private

### Step 1: Repository Setup
1. Push your code to GitHub
2. Go to repository **Settings** → **Pages**
3. Select **Deploy from a branch**
4. Choose branch: `gh-pages` and root folder
5. Save

### Step 2: GitHub Actions Deployment
The deployment happens automatically when you push to `main` or `master` branch.
- Frontend builds with Pyodide enabled
- Deploys to `gh-pages` branch
- Site goes live at: `https://yourusername.github.io/vdgopher_for_sql/`

**That's it! No backend configuration needed.**

### Step 3: Alternative Deployment Services
You can also deploy to:
- **Netlify**: Connect your GitHub repo, builds automatically
- **Vercel**: Similar to Netlify
- **GitHub Pages** (recommended, free and easy)

---

## Configuration

### Local Environment Variables
Create `frontend/.env.local`:
```env
# Use Pyodide (browser-based Python)
VITE_USE_PYODIDE=true

# Or use backend API
VITE_USE_PYODIDE=false
VITE_API_URL=http://localhost:8000
```

### Build Commands
```bash
cd frontend

# Development with Pyodide (default)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint
```

---

## Technology Stack

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **React Flow** - Graph visualization
- **Dagre** - Graph layout
- **Axios** - HTTP client

### Backend (Optional)
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **SQLGlot** - SQL parsing and analysis
- **Pydantic** - Data validation

### Browser-Based (Pyodide)
- **Pyodide** - Python in WebAssembly
- **SQLGlot** - Compiled to WebAssembly

---

## How It Works

### SQL Lineage Analysis
1. Parse SQL query using SQLGlot
2. Build scope tree to understand nesting
3. Identify all table and column references
4. Create node/edge graph for visualization
5. Render with React Flow

### Pyodide Workflow
1. Web Worker loads Pyodide (Python runtime)
2. Frontend sends SQL to Worker
3. Worker runs Python code in browser
4. Results sent back to frontend
5. Visualization rendered

---

## Notes

- **Browser Support**: Modern browsers with WebAssembly support (Chrome, Firefox, Safari, Edge)
- **Bundle Size**: ~50MB (Pyodide), but cached after first load
- **Performance**: After Pyodide loads, analysis is instant (no server latency)
- **Offline**: Works completely offline after initial load

---

## Optional: Backend Deployment

If you want to use the FastAPI backend instead of Pyodide:

### Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# From backend directory
vercel
```

### Deploy to Railway
1. Connect GitHub to Railway
2. Add environment variables
3. Deploy

### Update Frontend Config
```env
VITE_USE_PYODIDE=false
VITE_API_URL=https://your-backend-domain.com
```
