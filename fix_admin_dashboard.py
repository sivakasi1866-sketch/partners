with open("src/components/admin/AdminDashboard.tsx", "r") as f:
    content = f.read()

if "import { RouteManagement }" not in content:
    content = content.replace("import { DataImport } from './DataImport';", "import { DataImport } from './DataImport';\nimport { RouteManagement } from './RouteManagement';")

tab4_old = """      {/* TAB 4: ROUTES & STOPS */}
      {activeTab === 'routes' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-6">"""

import re
# we need to replace the entire Tab 4 block
# Using regex to find from TAB 4 to TAB 5
tab4_pattern = re.compile(r"\{\/\* TAB 4: ROUTES & STOPS \*\/\}.*?\{\/\* TAB 5: AI ROUTE OPTIMIZER", re.DOTALL)
new_tab4 = """{/* TAB 4: ROUTES & STOPS */}
      {activeTab === 'routes' && (
        <RouteManagement routes={routes} fetchRoutes={fetchLogsAndStats} />
      )}

      {/* TAB 5: AI ROUTE OPTIMIZER"""

content = tab4_pattern.sub(new_tab4, content)

with open("src/components/admin/AdminDashboard.tsx", "w") as f:
    f.write(content)
