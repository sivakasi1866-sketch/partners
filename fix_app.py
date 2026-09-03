import re

with open("src/App.tsx", "r") as f:
    content = f.read()

# Add import
import_statement = "import { Dither } from './components/ui/DitherBackground';\n"
content = content.replace("import { Login } from './components/Login';", import_statement + "import { Login } from './components/Login';")

# Add Dither in main return
main_return_search = """  return (
    <div className="min-h-screen bg-[#030712] text-slate-200 font-sans flex flex-col selection:bg-cyan-500/30 selection:text-cyan-100">"""

main_return_replace = """  return (
    <div className="min-h-screen bg-transparent text-slate-200 font-sans flex flex-col selection:bg-cyan-500/30 selection:text-cyan-100 relative">
      {/* Global Dither Background */}
      <Dither 
        waveColor={[0.32, 0.15, 1]}
        disableAnimation={false}
        enableMouseInteraction={true}
        mouseRadius={1}
        colorNum={4}
        pixelSize={2}
        waveAmplitude={0.3}
        waveFrequency={3}
        waveSpeed={0.05}
      />
      <div className="fixed inset-0 bg-[#030712]/40 -z-10 pointer-events-none" />
"""

content = content.replace(main_return_search, main_return_replace)

with open("src/App.tsx", "w") as f:
    f.write(content)

