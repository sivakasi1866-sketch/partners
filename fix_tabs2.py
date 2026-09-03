with open("src/components/admin/AdminDashboard.tsx", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "{/* TAB 6: PRIVACY & SYSTEM AUDIT LOGS */}" in line:
        start_idx = i
        break

# We need to replace line 824 with `{activeTab === 'privacy_logs' && (`
lines[start_idx+1] = "      {activeTab === 'privacy_logs' && (\n"

# Then we need to delete lines 825 and 826 which are:
#             Logs          </button>          <button id="admin-tab-import" onClick={() => setActiveTab('import')} className={`px-3.5 py-2 rounded-xl font-bold transition-all ${activeTab === 'import' && (
lines.pop(start_idx+2)
lines.pop(start_idx+2)

with open("src/components/admin/AdminDashboard.tsx", "w") as f:
    f.writelines(lines)
