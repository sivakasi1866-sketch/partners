import os

with open("src/components/map/LiveBusMap.tsx", "r") as f:
    content = f.read()

content = content.replace("cartocdn.com/rastertiles/voyager", "cartocdn.com/rastertiles/dark_all")

# Update popup content for better dark mode compatibility
content = content.replace('class="p-2 min-w-[180px] text-slate-900 font-sans"', 'class="p-2 min-w-[180px] text-slate-200 font-sans"')
content = content.replace("text-slate-700", "text-slate-300")
content = content.replace("text-slate-500", "text-slate-400")
content = content.replace("bg-white", "bg-slate-800")
content = content.replace("bg-gray-50", "bg-slate-900")

with open("src/components/map/LiveBusMap.tsx", "w") as f:
    f.write(content)

print("LiveBusMap updated")
