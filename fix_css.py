import os

css = """@import "tailwindcss";

@layer base {
  body {
    @apply bg-[#030712] text-slate-200 antialiased;
  }
}

@layer components {
  .glass-panel {
    @apply bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 shadow-2xl;
  }
  .card-3d {
    @apply bg-slate-800/60 backdrop-blur-md border border-slate-700/50 rounded-2xl shadow-lg transition-all duration-300;
  }
  .card-3d:hover {
    @apply transform -translate-y-1 shadow-cyan-500/10 shadow-2xl border-slate-600/60;
  }
  
  .btn-primary {
    @apply bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold py-2.5 px-4 rounded-xl shadow-lg shadow-cyan-500/20 transition-all duration-300 transform active:scale-95;
  }
  .btn-secondary {
    @apply bg-slate-800/80 hover:bg-slate-700 border border-slate-600/50 text-slate-200 font-medium py-2.5 px-4 rounded-xl transition-all duration-300 transform active:scale-95;
  }
}

/* Leaflet Custom Styling Overrides for Dark Mode */
.leaflet-container {
  width: 100%;
  height: 100%;
  background-color: #020617; /* Slate-950 */
  font-family: inherit;
}
.leaflet-popup-content-wrapper {
  background-color: #0f172a;
  color: #e2e8f0;
  border-radius: 12px;
  border: 1px solid rgba(51, 65, 85, 0.5);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  padding: 0;
  overflow: hidden;
}
.leaflet-popup-content {
  margin: 0;
  line-height: 1.4;
}
.leaflet-popup-tip {
  background-color: #0f172a;
}
.leaflet-control-zoom a {
  background-color: #0f172a !important;
  color: #e2e8f0 !important;
  border-color: #334155 !important;
}

/* Custom scrollbars */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: #0f172a;
}
::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
"""

with open("src/index.css", "w") as f:
    f.write(css)

print("CSS updated")
