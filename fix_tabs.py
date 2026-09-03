with open("src/components/admin/AdminDashboard.tsx", "r") as f:
    content = f.read()

content = content.replace("useState<'radar' | 'fleet' | 'drivers' | 'routes' | 'ml_ai' | 'privacy_logs'>('radar')",
    "useState<'radar' | 'fleet' | 'drivers' | 'routes' | 'ml_ai' | 'privacy_logs' | 'import'>('radar')")

old_tabs = """          <button
            id="admin-tab-logs"
            onClick={() => setActiveTab('privacy_logs')}
            className={`px-3.5 py-2 rounded-xl font-bold transition-all ${
              activeTab === 'privacy_logs' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white' }>
            Logs
          </button>
          <button id="admin-tab-import" onClick={() => setActiveTab('import')} className={`px-3.5 py-2 rounded-xl font-bold transition-all ${activeTab === 'import'
                ? 'bg-emerald-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Privacy & Audit Trail
          </button>"""

new_tabs = """          <button
            id="admin-tab-logs"
            onClick={() => setActiveTab('privacy_logs')}
            className={`px-3.5 py-2 rounded-xl font-bold transition-all ${
              activeTab === 'privacy_logs'
                ? 'bg-emerald-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Privacy & Audit Trail
          </button>
          <button
            id="admin-tab-import"
            onClick={() => setActiveTab('import')}
            className={`px-3.5 py-2 rounded-xl font-bold transition-all ${
              activeTab === 'import'
                ? 'bg-emerald-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Bulk Import
          </button>"""
content = content.replace(old_tabs, new_tabs)

with open("src/components/admin/AdminDashboard.tsx", "w") as f:
    f.write(content)
