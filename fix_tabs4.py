with open("src/components/admin/AdminDashboard.tsx", "r") as f:
    content = f.read()

import re
if "import { DataImport }" not in content:
    content = content.replace("import { LiveBusMap } from '../map/LiveBusMap';", "import { LiveBusMap } from '../map/LiveBusMap';\nimport { DataImport } from './DataImport';")

tab_content = """      {/* TAB 6: PRIVACY & SYSTEM AUDIT LOGS */}
      {activeTab === 'privacy_logs' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">"""

new_tab_content = """      {/* TAB 7: BULK DATA IMPORT */}
      {activeTab === 'import' && (
        <DataImport />
      )}

      {/* TAB 6: PRIVACY & SYSTEM AUDIT LOGS */}
      {activeTab === 'privacy_logs' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">"""

content = content.replace(tab_content, new_tab_content)

with open("src/components/admin/AdminDashboard.tsx", "w") as f:
    f.write(content)
