import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import { Upload, FileText, CheckCircle, AlertTriangle, Play, RefreshCw, XCircle } from 'lucide-react';

export const DataImport: React.FC = () => {
  const [templates, setTemplates] = useState<Record<string, any>>({});
  const [selectedEntity, setSelectedEntity] = useState<string>('students');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const res = await api.authFetch('/api/import/templates');
      const data = await res.json();
      setTemplates(data.templates);
    } catch (e) {
      setError('Failed to fetch templates');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setPreview(null);
      setError('');
      setSuccess('');
    }
  };

  const handleValidate = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('entity_type', selectedEntity);
      formData.append('file', file);
      
      const res = await api.authFetch('/api/import/validate', {
        method: 'POST',
        body: formData
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Validation failed');
      }
      
      setPreview(data);
    } catch (e: any) {
      setError(e.message || 'Validation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCommit = async () => {
    if (!preview || !preview.preview_valid.length) {
      setError('No valid rows to import');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const res = await api.authFetch('/api/import/commit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          entity_type: selectedEntity,
          rows: preview.preview_valid
        })
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Import failed');
      }
      
      setSuccess(`Successfully imported ${data.imported_rows} rows`);
      setFile(null);
      setPreview(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (e: any) {
      setError(e.message || 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm text-slate-900">
      <div className="mb-6">
        <h3 className="font-bold text-xl flex items-center gap-2">
          <Upload className="text-emerald-400" /> Bulk Data Import
        </h3>
        <p className="text-slate-600 text-sm mt-1">Upload institutional data from Excel files (.xlsx). Only administrators can perform bulk imports.</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-xl mb-6 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}
      
      {success && (
        <div className="bg-emerald-500/10 border border-emerald-200 text-emerald-400 p-4 rounded-xl mb-6 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p>{success}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="space-y-4">
          <h4 className="font-semibold text-lg border-b border-gray-200 pb-2">1. Select Entity Type</h4>
          <div className="flex flex-wrap gap-2">
            {Object.keys(templates).map(entity => (
              <button
                key={entity}
                onClick={() => { setSelectedEntity(entity); setPreview(null); setFile(null); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedEntity === entity ? 'bg-emerald-500 text-slate-950' : 'bg-white text-slate-700 hover:bg-gray-50'
                }`}
              >
                {entity.charAt(0).toUpperCase() + entity.slice(1)}
              </button>
            ))}
          </div>
          
          {selectedEntity && templates[selectedEntity] && (
            <div className="mt-4 bg-white/50 p-4 rounded-xl border border-gray-200/50">
              <h5 className="font-medium text-sm text-slate-700 mb-2">Required Template Columns:</h5>
              <div className="flex flex-wrap gap-2">
                {templates[selectedEntity].map((col: any) => (
                  <span key={col} className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-mono text-emerald-300">
                    {col}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <h4 className="font-semibold text-lg border-b border-gray-200 pb-2">2. Upload Excel File</h4>
          <div className="mt-2">
            <input 
              type="file" 
              accept=".xlsx" 
              onChange={handleFileChange}
              ref={fileInputRef}
              className="block w-full text-sm text-slate-600
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-emerald-500/20 file:text-emerald-400
                hover:file:bg-emerald-500/30 cursor-pointer border border-gray-200 rounded-lg p-2"
            />
          </div>
          
          <button
            onClick={handleValidate}
            disabled={!file || loading}
            className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 mt-4 ${
              !file || loading ? 'bg-white text-slate-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white'
            }`}
          >
            {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
            Validate Data
          </button>
        </div>
      </div>

      {preview && (
        <div className="border-t border-gray-200 pt-6">
          <h4 className="font-semibold text-lg mb-4 flex items-center justify-between">
            <span>3. Validation Preview</span>
            <span className="text-sm font-normal text-slate-600">Total Rows: {preview.total_rows}</span>
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-emerald-500/10 border border-emerald-200 rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle className="w-5 h-5" />
                <span className="font-semibold">Valid Rows Ready to Import</span>
              </div>
              <span className="text-2xl font-bold text-emerald-300">{preview.valid_rows}</span>
            </div>
            
            <div className={`border rounded-xl p-4 flex items-center justify-between ${
              preview.invalid_rows > 0 ? 'bg-red-500/10 border-red-500/30' : 'bg-white border-gray-200'
            }`}>
              <div className={`flex items-center gap-2 ${preview.invalid_rows > 0 ? 'text-red-400' : 'text-slate-600'}`}>
                {preview.invalid_rows > 0 ? <XCircle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
                <span className="font-semibold">Invalid/Rejected Rows</span>
              </div>
              <span className={`text-2xl font-bold ${preview.invalid_rows > 0 ? 'text-red-300' : 'text-slate-500'}`}>
                {preview.invalid_rows}
              </span>
            </div>
          </div>
          
          {preview.errors && preview.errors.length > 0 && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-6">
              <h5 className="font-medium text-red-400 mb-2">Validation Errors:</h5>
              <ul className="list-disc pl-5 space-y-1 text-sm text-red-300">
                {preview.errors.slice(0, 10).map((err: string, i: number) => (
                  <li key={i}>{err}</li>
                ))}
                {preview.errors.length > 10 && (
                  <li>...and {preview.errors.length - 10} more errors</li>
                )}
              </ul>
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={handleCommit}
              disabled={loading || preview.valid_rows === 0}
              className={`py-3 px-8 rounded-xl font-bold flex items-center gap-2 ${
                loading || preview.valid_rows === 0 ? 'bg-white text-slate-500 cursor-not-allowed' : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950'
              }`}
            >
              {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
              Confirm & Import {preview.valid_rows} Rows
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
