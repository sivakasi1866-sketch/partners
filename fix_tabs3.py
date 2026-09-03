with open("src/components/admin/AdminDashboard.tsx", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "{/* TAB 6: PRIVACY & SYSTEM AUDIT LOGS */}" in line:
        start_idx = i
        break

# The line below start_idx is `      {activeTab === 'privacy_logs' && (\n`
# The line below that is the broken button line.
lines.pop(start_idx+2)

with open("src/components/admin/AdminDashboard.tsx", "w") as f:
    f.writelines(lines)
