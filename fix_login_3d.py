import os

login_tsx = """import React, { useState } from 'react';
import { Bus, KeyRound, User as UserIcon } from 'lucide-react';
import { User } from '../types';
import { api } from '../services/api';

interface LoginProps {
  onLogin: (user: User) => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

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
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#030712] font-sans text-slate-200 perspective-1000">
      
      {/* Video Background */}
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
      </div>

      <div className="relative z-10 w-full max-w-md px-6">
        
        {/* Floating 3D Card */}
        <div className="glass-panel rounded-3xl p-8 transform transition-transform duration-500 hover:rotate-y-2 hover:rotate-x-2">
          <div className="flex justify-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 p-[2px] shadow-lg shadow-cyan-500/30 animate-pulse-slow">
              <div className="w-full h-full bg-slate-900/80 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <Bus className="w-8 h-8 text-cyan-400 drop-shadow-md" />
              </div>
            </div>
          </div>
          
          <div className="text-center mb-10">
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-2 drop-shadow-sm">
              Partners Bus Prediction
            </h1>
            <p className="text-sm text-cyan-200/70 font-medium tracking-wide uppercase">
              Smart Campus Transportation
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <UserIcon className="h-5 w-5 text-slate-400 group-focus-within:text-cyan-400 transition-colors" />
                </div>
                <input
                  id="identifier"
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className="block w-full pl-12 pr-4 py-3.5 bg-slate-800/50 border border-slate-600/50 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all shadow-inner"
                  placeholder="User ID / Email"
                />
              </div>
            </div>

            <div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <KeyRound className="h-5 w-5 text-slate-400 group-focus-within:text-cyan-400 transition-colors" />
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-12 pr-4 py-3.5 bg-slate-800/50 border border-slate-600/50 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all shadow-inner"
                  placeholder="Password"
                />
              </div>
            </div>

            {errorMsg && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-sm font-medium text-center">
                {errorMsg}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary flex justify-center items-center py-4 text-base tracking-wide mt-4"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'LOGIN'
              )}
            </button>
          </form>
          
        </div>
      </div>
    </div>
  );
};
"""
with open("src/components/Login.tsx", "w") as f:
    f.write(login_tsx)
print("Login.tsx updated")
