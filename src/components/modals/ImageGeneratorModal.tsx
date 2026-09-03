import React, { useState } from 'react';
import { Image as ImageIcon, Send, Loader2, Download } from 'lucide-react';
import { api } from '../../services/api';

interface ImageGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ImageGeneratorModal: React.FC<ImageGeneratorModalProps> = ({ isOpen, onClose }) => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;

    setIsLoading(true);
    setErrorMsg('');
    try {
      const res = await api.generateImage(prompt);
      if (res.success && res.image) {
        setGeneratedImage(res.image);
      } else {
        setErrorMsg(res.error || 'Failed to generate image.');
      }
    } catch (err: any) {
      setErrorMsg('An error occurred during image generation.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-50/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-gray-200 rounded-xl max-w-lg w-full shadow-sm flex flex-col overflow-hidden animate-in fade-in zoom-in-95">
        {/* Header */}
        <div className="p-4 bg-gray-50/80 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-600">
              <ImageIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                AI Image Studio
                <span className="text-[10px] bg-purple-500/20 text-purple-700 px-1.5 py-0.5 rounded font-mono">
                  Gemini 3.1 Flash
                </span>
              </h3>
              <p className="text-[11px] text-slate-600">Create visuals from text prompts</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-600 hover:text-slate-900 p-1 rounded-lg hover:bg-white">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-4 flex flex-col gap-4">
          <form onSubmit={handleGenerate} className="flex gap-2">
            <input
              type="text"
              placeholder="Describe the image you want to generate..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isLoading}
              className="flex-1 bg-gray-50 border border-gray-200 text-slate-900 rounded-xl px-3.5 py-2 text-sm focus:outline-none focus:border-purple-500"
            />
            <button
              type="submit"
              disabled={isLoading || !prompt.trim()}
              className="p-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center min-w-[44px]"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>

          {errorMsg && (
            <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm border border-red-200">
              {errorMsg}
            </div>
          )}

          <div className="bg-gray-50 border border-gray-200 rounded-xl aspect-square flex items-center justify-center overflow-hidden relative">
            {generatedImage ? (
              <>
                <img src={generatedImage} alt="Generated" className="w-full h-full object-cover" />
                <a
                  href={generatedImage}
                  download="generated-image.jpg"
                  className="absolute bottom-4 right-4 p-2 bg-white/90 backdrop-blur shadow-sm rounded-lg hover:bg-white text-slate-700 transition-colors"
                >
                  <Download className="w-4 h-4" />
                </a>
              </>
            ) : (
              <div className="text-slate-400 flex flex-col items-center gap-2">
                <ImageIcon className="w-8 h-8 opacity-50" />
                <span className="text-sm font-medium">Your image will appear here</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
