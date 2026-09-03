import os
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Layout colors
    content = content.replace("bg-slate-950", "bg-gray-50")
    content = content.replace("bg-slate-900", "bg-white")
    content = content.replace("bg-slate-800", "bg-white")
    content = content.replace("bg-slate-700", "bg-gray-50")
    content = content.replace("bg-slate-950/40", "bg-gray-50")
    content = content.replace("bg-slate-950/80", "bg-gray-50")
    content = content.replace("bg-slate-800/80", "bg-white")
    content = content.replace("bg-slate-800/60", "bg-white")
    content = content.replace("bg-slate-900/60", "bg-white")
    content = content.replace("bg-slate-900/80", "bg-white")
    
    # Borders
    content = content.replace("border-slate-800", "border-gray-200")
    content = content.replace("border-slate-800/60", "border-gray-200")
    content = content.replace("border-slate-700", "border-gray-200")
    content = content.replace("border-slate-700/80", "border-gray-200")
    content = content.replace("border-slate-600", "border-gray-300")
    content = content.replace("border-emerald-500/30", "border-emerald-200")
    content = content.replace("border-rose-600/50", "border-rose-200")
    
    # Shadows
    content = re.sub(r'shadow-indigo-600/\d+', 'shadow-sm', content)
    content = re.sub(r'shadow-emerald-600/\d+', 'shadow-sm', content)
    content = re.sub(r'shadow-rose-600/\d+', 'shadow-sm', content)
    content = re.sub(r'shadow-amber-600/\d+', 'shadow-sm', content)
    content = re.sub(r'shadow-emerald-500/\d+', 'shadow-sm', content)
    content = re.sub(r'shadow-emerald-900/\d+', 'shadow-sm', content)
    content = content.replace("shadow-2xl", "shadow-sm")
    content = content.replace("shadow-xl", "shadow-sm")
    content = content.replace("shadow-lg", "shadow-sm")
    
    # Radii
    content = content.replace("rounded-3xl", "rounded-xl")
    content = content.replace("rounded-2xl", "rounded-lg")
    
    # Text colors
    content = content.replace("text-white", "text-slate-900")
    content = content.replace("text-slate-100", "text-slate-900")
    content = content.replace("text-slate-200", "text-slate-800")
    content = content.replace("text-slate-300", "text-slate-700")
    content = content.replace("text-slate-400", "text-slate-600")
    content = content.replace("text-slate-500", "text-slate-500")
    
    # Text inside colored buttons needs to be white
    # e.g., bg-emerald-600 hover:bg-emerald-500 text-slate-900 -> text-white
    content = re.sub(r'(bg-[a-z]+-[567]00[^"\'}]*)text-slate-900', r'\1text-white', content)
    content = re.sub(r'(bg-[a-z]+-[567]00[^"\'}]*)text-slate-800', r'\1text-white', content)
    
    # Gradients
    content = re.sub(r'bg-gradient-to-[a-z]+\s+from-[a-z0-9/]+\s+to-[a-z0-9/]+', 'bg-white', content)
    content = re.sub(r'bg-gradient-to-[a-z]+\s+from-[a-z0-9/]+\s+via-[a-z0-9/]+\s+to-[a-z0-9/]+', 'bg-white', content)
    
    # Specific UI text replaces
    content = content.replace("Elite Bus Prediction System", "Partners Bus Prediction")
    content = content.replace("Elite Bus Prediction", "Partners Bus Prediction")
    content = content.replace("AI Transit Bot", "Help & Support")
    content = content.replace("Institutional Smart Bus Telemetry & ML ETA Forecasting", "Campus Transportation System")
    
    # Remove animate-pulse
    content = content.replace("animate-pulse", "")
    
    # Fix specific ring styles
    content = content.replace("ring-slate-900", "ring-white")
    content = content.replace("ring-slate-950", "ring-white")

    with open(filepath, 'w') as f:
        f.write(content)

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            process_file(os.path.join(root, file))

print("Refactoring complete.")
