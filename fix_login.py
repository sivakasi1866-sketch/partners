import re

with open("src/components/Login.tsx", "r") as f:
    content = f.read()

# Replace video block with Dither component
video_block = """      {/* Video Background */}
      <div className="absolute inset-0 z-0">
        <video 
          autoPlay 
          loop 
          muted 
          playsInline 
          className="w-full h-full object-cover opacity-60"
        >
          <source src="/galaxy-bg.webm" type="video/webm" />
          {/* Fallback gradient if video fails */}
          <div className="w-full h-full bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900"></div>
        </video>
        <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-transparent to-transparent opacity-80" />
      </div>"""

dither_block = """      {/* Dither Background */}
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
      <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-transparent to-transparent opacity-80 -z-10" />"""

content = content.replace(video_block, dither_block)

# Add import
import_statement = "import { Dither } from './ui/DitherBackground';\n"
content = content.replace("import { User } from '../types';", import_statement + "import { User } from '../types';")

# Make Login bg transparent
content = content.replace('bg-[#030712]', 'bg-transparent')

with open("src/components/Login.tsx", "w") as f:
    f.write(content)

