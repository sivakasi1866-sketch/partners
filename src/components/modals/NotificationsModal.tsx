import React from 'react';
import { Bell, Info, AlertTriangle, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { Notification } from '../../types';

interface NotificationsModalProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: Notification[];
  onMarkAllAsRead: () => void;
}

export const NotificationsModal: React.FC<NotificationsModalProps> = ({
  isOpen,
  onClose,
  notifications,
  onMarkAllAsRead
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-50/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-gray-200 rounded-xl max-w-lg w-full p-6 shadow-sm space-y-4 animate-in fade-in zoom-in-95 max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between border-b border-gray-200 pb-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900">Campus Transit Bulletins</h3>
              <p className="text-[11px] text-slate-600">{notifications.length} active announcements</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-600 hover:text-slate-900 p-1 rounded-lg hover:bg-white">✕</button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 text-xs">
          {notifications.map(n => (
            <div
              key={n.id}
              className={`p-3.5 rounded-lg border transition-all ${
                n.type === 'alert'
                  ? 'bg-rose-950/40 border-rose-500/40 text-rose-200'
                  : n.type === 'warning'
                  ? 'bg-amber-950/40 border-amber-500/40 text-amber-200'
                  : 'bg-gray-50 border-gray-200 text-slate-700'
              }`}
            >
              <div className="flex items-start gap-2.5">
                <div className="mt-0.5 shrink-0">
                  {n.type === 'alert' && <AlertCircle className="w-4 h-4 text-rose-400" />}
                  {n.type === 'warning' && <AlertTriangle className="w-4 h-4 text-amber-400" />}
                  {n.type === 'info' && <Info className="w-4 h-4 text-sky-400" />}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 text-xs">{n.title}</h4>
                    <span className="text-[10px] text-slate-600 font-mono">
                      {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-slate-700 text-[11px] leading-relaxed">{n.message}</p>
                </div>
              </div>
            </div>
          ))}
          {notifications.length === 0 && (
            <div className="text-center py-10 text-slate-500 text-xs">
              No bulletins at this moment. Transit network is normal.
            </div>
          )}
        </div>

        <div className="flex justify-between items-center pt-2 border-t border-gray-200">
          <button
            onClick={onMarkAllAsRead}
            className="text-[11px] text-slate-600 hover:text-slate-900 transition-colors"
          >
            Mark all read
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-white hover:bg-gray-50 text-slate-800 rounded-xl text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};
