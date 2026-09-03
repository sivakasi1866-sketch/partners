import React from 'react';
import { ShieldCheck, Lock, CheckCircle2, AlertOctagon, Smartphone, Radio } from 'lucide-react';

interface PrivacyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PrivacyModal: React.FC<PrivacyModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-50/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-gray-200 rounded-xl max-w-xl w-full p-6 shadow-sm space-y-6 text-slate-900 animate-in fade-in zoom-in-95 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-gray-200 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900">Institutional GPS Privacy Architecture</h3>
              <p className="text-xs text-emerald-400 font-mono">100% Policy Compliant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-600 hover:text-slate-900 p-1 rounded-lg hover:bg-white text-lg font-bold"
          >
            ✕
          </button>
        </div>

        {/* Core Rules Section */}
        <div className="space-y-4 text-xs">
          {/* Rule 1: Student & Staff Zero-Tracking */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 space-y-2">
            <div className="flex items-center gap-2 font-bold text-emerald-400 text-sm">
              <CheckCircle2 className="w-4 h-4" />
              1. Strict Zero-Location Student & Staff Policy
            </div>
            <p className="text-slate-700 leading-relaxed">
              Students and staff members are <strong>strictly anonymous consumers</strong>. The application never invokes <code className="bg-white px-1 py-0.5 rounded font-mono text-emerald-300">navigator.geolocation</code> on student or staff dashboards. No student or faculty location data is ever generated, collected, or logged.
            </p>
          </div>

          {/* Rule 2: Bus-Only Tracking via Driver Phone */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 space-y-2">
            <div className="flex items-center gap-2 font-bold text-sky-400 text-sm">
              <Smartphone className="w-4 h-4" />
              2. Vehicle-Specific GPS Location (Driver Device)
            </div>
            <p className="text-slate-700 leading-relaxed">
              Only the active institutional shuttle bus is tracked. The assigned commercial driver’s smartphone acts as the telematics beacon for the vehicle.
            </p>
          </div>

          {/* Rule 3: Strict GPS Lifecycle */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 space-y-2">
            <div className="flex items-center gap-2 font-bold text-amber-400 text-sm">
              <Radio className="w-4 h-4" />
              3. Strict GPS Lifecycle Enforcement
            </div>
            <div className="space-y-1.5 text-slate-700 font-sans">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span><strong>START TRIP:</strong> Driver initiates the run ➔ GPS broadcast begins.</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-400"></span>
                <span><strong>IN TRANSIT:</strong> Live bus coordinates are used to estimate arrival times.</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                <span><strong>STOP / END TRIP:</strong> Driver ends run ➔ GPS stream is <strong>instantly terminated</strong>.</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600 text-[11px] pt-1">
                <Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>System rejects any GPS updates once a trip is closed (HTTP 403 Forbidden).</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-sm"
          >
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
};
