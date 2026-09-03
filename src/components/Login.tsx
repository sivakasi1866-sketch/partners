import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { Dither } from './ui/DitherBackground';
import { User } from '../types';
import { api } from '../services/api';

interface LoginProps {
  onLogin: (user: User) => void;
}

const ShuttleSVG = ({ className = "" }: { className?: string }) => (
  <svg viewBox="0 0 400 240" xmlns="http://www.w3.org/2000/svg" className={className}>
    <defs>
      <linearGradient id="busBodyGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="#1e293b" />
        <stop offset="50%" stopColor="#0f172a" />
        <stop offset="100%" stopColor="#020617" />
      </linearGradient>
      <linearGradient id="windowGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stopColor="#0284c7" stopOpacity="0.8"/>
        <stop offset="50%" stopColor="#0369a1" stopOpacity="0.9"/>
        <stop offset="100%" stopColor="#0c4a6e" stopOpacity="0.8"/>
      </linearGradient>
      <linearGradient id="accentGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stopColor="#38bdf8" />
        <stop offset="100%" stopColor="#0284c7" />
      </linearGradient>
      <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="4" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
      <filter id="headlightGlow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="6" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    </defs>

    {/* Ground Shadow */}
    <ellipse cx="200" cy="210" rx="150" ry="15" fill="rgba(0,0,0,0.6)" filter="blur(8px)" />
    <ellipse cx="200" cy="210" rx="100" ry="8" fill="rgba(2,132,199,0.2)" filter="blur(12px)" />

    {/* Main Body */}
    <path d="M 50 140 Q 50 60 90 60 L 320 60 Q 360 60 360 120 L 360 180 Q 360 200 340 200 L 70 200 Q 50 200 50 180 Z" 
          fill="url(#busBodyGrad)" stroke="#334155" strokeWidth="1.5" />
    
    {/* Body Contour Line */}
    <path d="M 50 130 Q 50 110 90 110 L 360 110" stroke="#334155" strokeWidth="1" fill="none" opacity="0.5"/>

    {/* Front Windshield / Side Windows Continuous Band */}
    <path d="M 60 120 Q 60 75 90 75 L 310 75 Q 345 75 350 110 L 350 135 L 60 135 Z" 
          fill="url(#windowGrad)" />
    
    {/* Window Reflections */}
    <path d="M 80 85 L 120 125 M 130 85 L 170 125 M 280 85 L 320 125" stroke="rgba(255,255,255,0.1)" strokeWidth="8" strokeLinecap="round" />

    {/* Window Dividers */}
    <line x1="120" y1="75" x2="120" y2="135" stroke="#020617" strokeWidth="4" />
    <line x1="190" y1="75" x2="190" y2="135" stroke="#020617" strokeWidth="4" />
    <line x1="260" y1="75" x2="260" y2="135" stroke="#020617" strokeWidth="4" />
    <line x1="330" y1="75" x2="330" y2="135" stroke="#020617" strokeWidth="4" />

    {/* LED Accent Strip */}
    <path d="M 50 150 L 360 150" stroke="url(#accentGrad)" strokeWidth="2" filter="url(#softGlow)" />
    
    {/* Headlights (Front is right) */}
    <rect x="352" y="158" width="8" height="16" rx="3" fill="#e0f2fe" filter="url(#headlightGlow)" />
    <rect x="350" y="160" width="10" height="12" rx="2" fill="#bae6fd" />
    
    {/* Taillights (Back is left) */}
    <rect x="48" y="158" width="6" height="16" rx="2" fill="#ef4444" filter="url(#headlightGlow)" />

    {/* Wheels (Left to Right) */}
    {/* Back Wheel */}
    <circle cx="110" cy="200" r="22" fill="#020617" stroke="#1e293b" strokeWidth="3" />
    <circle cx="110" cy="200" r="10" fill="#334155" />
    <circle cx="110" cy="200" r="4" fill="#0f172a" />
    
    {/* Front Wheel */}
    <circle cx="300" cy="200" r="22" fill="#020617" stroke="#1e293b" strokeWidth="3" />
    <circle cx="300" cy="200" r="10" fill="#334155" />
    <circle cx="300" cy="200" r="4" fill="#0f172a" />

    {/* Wheel arches */}
    <path d="M 80 200 A 30 30 0 0 1 140 200" fill="none" stroke="#020617" strokeWidth="4" />
    <path d="M 270 200 A 30 30 0 0 1 330 200" fill="none" stroke="#020617" strokeWidth="4" />
  </svg>
);

const TransportNetworkVisual = () => (
  <div className="absolute w-[150%] h-[150%] transform rotate-x-[55deg] rotate-z-[-20deg] translate-y-16 opacity-40 pointer-events-none">
    <svg className="w-full h-full" viewBox="0 0 1000 1000" fill="none">
       {/* Main arterial routes */}
       <path d="M100 500 L400 500 L600 300 L900 300" stroke="#0ea5e9" strokeWidth="2" strokeDasharray="8 8" className="animate-network-flow" />
       <path d="M200 800 L400 500 L700 600 L900 600" stroke="#0284c7" strokeWidth="2" strokeDasharray="6 6" className="animate-network-flow" style={{ animationDuration: '25s' }} />
       <path d="M150 200 L450 200 L600 300 L750 150" stroke="#38bdf8" strokeWidth="1.5" strokeDasharray="4 4" className="animate-network-flow" style={{ animationDuration: '15s', animationDirection: 'reverse' }} />

       {/* Interconnecting grid lines */}
       <path d="M400 200 L400 800 M600 150 L600 600" stroke="#1e293b" strokeWidth="1" />

       {/* Nodes */}
       <circle cx="400" cy="500" r="6" fill="#0ea5e9" className="animate-pulse-node" style={{ animationDelay: '0s' }} />
       <circle cx="600" cy="300" r="6" fill="#0ea5e9" className="animate-pulse-node" style={{ animationDelay: '1s' }} />
       <circle cx="700" cy="600" r="5" fill="#0284c7" className="animate-pulse-node" style={{ animationDelay: '2s' }} />
       <circle cx="450" cy="200" r="4" fill="#38bdf8" className="animate-pulse-node" style={{ animationDelay: '3s' }} />
       
       {/* Small indicator dots */}
       <circle cx="100" cy="500" r="3" fill="#64748b" />
       <circle cx="900" cy="300" r="3" fill="#64748b" />
       <circle cx="200" cy="800" r="3" fill="#64748b" />
       <circle cx="900" cy="600" r="3" fill="#64748b" />
    </svg>
  </div>
);

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    
    if (!identifier.trim() || !password.trim()) {
      setErrorMsg("Please enter both User ID and password.");
      return;
    }
    
    setIsLoading(true);
    try {
      const res = await api.login(identifier.trim(), password);
      if (res.user) {
        onLogin(res.user);
      } else {
        setErrorMsg("Unable to sign in. Please check credentials.");
      }
    } catch (e) {
      console.error(e);
      setErrorMsg("Unable to sign in. Please check credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col md:flex-row bg-[#020617] overflow-hidden text-slate-200">
      
      <style>{`
        @keyframes float-bus {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-4px); }
        }
        @keyframes pulse-node {
          0%, 100% { opacity: 0.4; transform: scale(0.9); }
          50% { opacity: 1; transform: scale(1.1); }
        }
        @keyframes network-flow {
          0% { stroke-dashoffset: 100; }
          100% { stroke-dashoffset: 0; }
        }
        .animate-float-bus {
          animation: float-bus 6s ease-in-out infinite;
        }
        .animate-pulse-node {
          animation: pulse-node 4s ease-in-out infinite;
        }
        .animate-network-flow {
          animation: network-flow 20s linear infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .animate-float-bus, .animate-pulse-node, .animate-network-flow {
            animation: none !important;
            transform: none !important;
          }
        }
      `}</style>

      {/* Very Subtle Dither Background layer */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.07]">
        <Dither 
          waveColor={[0.32, 0.15, 1]}
          disableAnimation={false}
          enableMouseInteraction={false}
          colorNum={4}
          pixelSize={2}
          waveAmplitude={0.2}
          waveFrequency={2}
          waveSpeed={0.03}
        />
      </div>

      {/* MOBILE HEADER (Visible only on small screens) */}
      <div className="md:hidden flex flex-col items-center pt-10 pb-6 px-6 relative z-10">
        <div className="flex flex-col items-center text-center mb-6">
          <h1 className="text-xl font-bold tracking-tight text-slate-100 leading-tight">
            PARTNERS <br/>
            BUS PREDICTION
          </h1>
          <p className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase mt-1">
            Smart Campus Transportation
          </p>
        </div>
        <div className="w-48 h-auto animate-float-bus relative">
           <ShuttleSVG className="w-full h-auto drop-shadow-xl" />
        </div>
      </div>

      {/* LEFT COLUMN: Desktop 3D Visual & Network (Hidden on mobile) */}
      <div className="hidden md:flex md:w-[55%] lg:w-[60%] relative z-10 flex-col items-center justify-center p-12 perspective-1000">
        <div className="absolute top-12 left-12 flex flex-col items-start z-30">
          <h1 className="text-3xl lg:text-4xl font-bold tracking-tight text-slate-100 leading-tight">
            PARTNERS <br/>
            BUS PREDICTION
          </h1>
          <p className="text-xs font-semibold tracking-widest text-slate-400 uppercase mt-2">
            Smart Campus Transportation
          </p>
        </div>

        <TransportNetworkVisual />
        
        {/* 3D Bus Hero Element */}
        <div className="relative z-20 animate-float-bus w-[400px] max-w-full drop-shadow-2xl">
           <ShuttleSVG className="w-full h-auto" />
        </div>
      </div>

      {/* RIGHT COLUMN: Professional Login Panel */}
      <div className="w-full md:w-[45%] lg:w-[40%] flex flex-col justify-center px-6 sm:px-12 md:px-16 py-8 md:py-12 bg-[#050b14] border-t md:border-t-0 md:border-l border-slate-800/80 z-20 min-h-screen md:min-h-0 shadow-2xl relative">
        
        <div className="max-w-[360px] mx-auto w-full">
          
          <div className="mb-10">
            <h2 className="text-2xl font-semibold text-slate-100 mb-2">Welcome back</h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Sign in to continue to your transportation dashboard.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="identifier" className="block text-[13px] font-medium text-slate-300">
                User ID / Email
              </label>
              <div className="relative group">
                <input
                  id="identifier"
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className="block w-full px-4 py-3.5 bg-[#0b1221] border border-slate-700/80 rounded-md text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors text-sm"
                  placeholder="Enter your ID or Email"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="block text-[13px] font-medium text-slate-300">
                Password
              </label>
              <div className="relative group">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-4 pr-10 py-3.5 bg-[#0b1221] border border-slate-700/80 rounded-md text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors text-sm"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {errorMsg && (
              <div className="p-3 bg-red-950/30 border border-red-900/50 rounded-md text-red-400 text-sm font-medium flex items-start gap-2">
                <div className="mt-0.5">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                {errorMsg}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#0284c7] hover:bg-[#0369a1] active:scale-[0.99] text-white border border-transparent flex justify-center items-center py-3.5 rounded-md text-[15px] font-medium transition-all mt-2 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'SIGN IN'
              )}
            </button>
          </form>
          
        </div>
      </div>
    </div>
  );
};
