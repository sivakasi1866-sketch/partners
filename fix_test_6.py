with open('backend/app/tests/test_agent8_regression.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'client.post("/api/trips/update-gps"' in line and 'test_6' in line:
        pass # just context
    new_lines.append(line)
    if 'timestamp": "2023-01-01T00:01:00Z"' in line and 'headers=headers)' in line:
        new_lines.append("        assert r_gps1.status_code == 200\n")
    if 'timestamp": "2023-01-01T00:01:05Z"' in line and 'headers=headers)' in line:
        new_lines.append("        assert r_gps2.status_code == 200\n")

with open('backend/app/tests/test_agent8_regression.py', 'w') as f:
    f.writelines(new_lines)
