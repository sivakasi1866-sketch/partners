with open("src/App.tsx", "r") as f:
    content = f.read()

import re

# 1. Add import for ImageGeneratorModal
content = re.sub(
    r"import \{ AIAssistantModal \} from '\./components/modals/AIAssistantModal';",
    "import { AIAssistantModal } from './components/modals/AIAssistantModal';\nimport { ImageGeneratorModal } from './components/modals/ImageGeneratorModal';\nimport { Image as ImageIcon } from 'lucide-react';",
    content
)

# 2. Add state for isImageGeneratorOpen
content = re.sub(
    r"const \[isAIAssistantOpen, setIsAIAssistantOpen\] = useState\(false\);",
    "const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);\n  const [isImageGeneratorOpen, setIsImageGeneratorOpen] = useState(false);",
    content
)

# 3. Add the button
button_code = """            <button
              onClick={() => setIsImageGeneratorOpen(true)}
              className="hidden sm:flex px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-md text-xs font-semibold items-center gap-1.5 border border-purple-200 transition-colors"
            >
              <ImageIcon className="w-4 h-4" />
              <span>Image Studio</span>
            </button>
            <button
              onClick={() => setIsAIAssistantOpen(true)}"""
              
content = content.replace(
    """            <button
              onClick={() => setIsAIAssistantOpen(true)}""",
    button_code
)

# 4. Add the Modal component
modal_code = """      <AIAssistantModal isOpen={isAIAssistantOpen} onClose={() => setIsAIAssistantOpen(false)} currentUser={currentUser} />
      <ImageGeneratorModal isOpen={isImageGeneratorOpen} onClose={() => setIsImageGeneratorOpen(false)} />"""

content = content.replace(
    "<AIAssistantModal isOpen={isAIAssistantOpen} onClose={() => setIsAIAssistantOpen(false)} currentUser={currentUser} />",
    modal_code
)

with open("src/App.tsx", "w") as f:
    f.write(content)
