import { useState, useEffect } from 'react';
import {
    Upload, CheckCircle, AlertCircle, Info, Download,
    Loader, FileText, Clock, XCircle, Trash2,
    Eye, Play, CheckSquare, Square, Home, Code, RefreshCw,
    Shield, FileSearch, Zap, Users, Sparkles, ArrowRight,
    History, ClipboardCheck, AlertTriangle, Send
} from 'lucide-react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

const MODULES = [
    { id: 'Structure', name: 'Structure', description: 'Document format and layout' },
    { id: 'Registration', name: 'Registration', description: 'Fund registration requirements' },
    { id: 'ESG', name: 'ESG', description: 'ESG compliance' },
    { id: 'Disclaimers', name: 'Disclaimers', description: 'Required disclaimers' },
    { id: 'Performance', name: 'Performance', description: 'Performance rules' },
    { id: 'Values', name: 'Values', description: 'Securities mentions' },
    { id: 'Prospectus', name: 'Prospectus', description: 'Prospectus alignment' },
    { id: 'General', name: 'General', description: 'General rules' }
];

const EXTRACTION_METHODS = [
    { id: 'MO', name: 'Standard (MO)', description: 'Fast extraction using python-pptx' },
    { id: 'FD', name: 'Fida (FD)', description: 'AI-powered with Gemini Multi-Agent' },
    { id: 'SF', name: 'Safa (SF)', description: 'Exhaustive extraction with Groq' },
    { id: 'SL', name: 'Slim (SL)', description: 'Parallel extraction with TokenFactory' }
];

function AppEnhanced() {
    const [view, setView] = useState('landing');
    const [pptxFile, setPptxFile] = useState(null);
    const [metadataFile, setMetadataFile] = useState(null);
    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState(null);
    const [slides, setSlides] = useState([]);
    const [selectedSlide, setSelectedSlide] = useState(0);
    const [selectedModules, setSelectedModules] = useState(MODULES.map(m => m.id));
    const [violations, setViolations] = useState([]);
    const [error, setError] = useState(null);
    const [extractionMethod, setExtractionMethod] = useState('MO');
    const [parallelWorkers, setParallelWorkers] = useState(4);
    const [extractedJson, setExtractedJson] = useState(null);
    const [showModuleSelector, setShowModuleSelector] = useState(false);
    // History state
    const [historyData, setHistoryData] = useState([]);
    const [historyStats, setHistoryStats] = useState(null);
    const [selectedHistoryJob, setSelectedHistoryJob] = useState(null);
    const [reviewNotes, setReviewNotes] = useState('');

    useEffect(() => {
        if (jobId && view === 'processing') {
            const interval = setInterval(async () => {
                try {
                    const response = await axios.get(`${API_BASE_URL}/api/status/${jobId}`);
                    setJobStatus(response.data);
                    if (response.data.status === 'completed') {
                        clearInterval(interval);
                        await loadResults(jobId);
                    } else if (response.data.status === 'failed') {
                        clearInterval(interval);
                        setError(response.data.message || 'Processing failed');
                        setView('preview');
                    }
                } catch (err) {
                    console.error('Status check error:', err);
                }
            }, 2000);
            return () => clearInterval(interval);
        }
    }, [jobId, view]);

    const loadResults = async (jId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/download/${jId}/violations`);
            setViolations(response.data.all_violations || []);
            setView('results');
        } catch (err) {
            setError('Failed to load compliance results');
        }
    };

    const loadExtractedJson = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/download/${jobId}/extracted-json`);
            setExtractedJson(response.data);
            setView('json-viewer');
        } catch (err) {
            setError('Failed to load extracted JSON');
        }
    };

    // History functions
    const loadHistory = async () => {
        try {
            const [historyRes, statsRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/history`),
                axios.get(`${API_BASE_URL}/api/history/stats`)
            ]);
            setHistoryData(historyRes.data.jobs || []);
            setHistoryStats(statsRes.data);
        } catch (err) {
            console.error('Failed to load history:', err);
        }
    };

    const updateReviewStatus = async (jobIdToUpdate, newStatus) => {
        try {
            const formData = new FormData();
            formData.append('review_status', newStatus);
            if (reviewNotes) formData.append('reviewer_notes', reviewNotes);
            await axios.put(`${API_BASE_URL}/api/history/${jobIdToUpdate}/review`, formData);
            setReviewNotes('');
            await loadHistory();
        } catch (err) {
            setError('Failed to update review status');
        }
    };

    const deleteHistoryJob = async (jobIdToDelete) => {
        if (!window.confirm('Are you sure you want to delete this job?')) return;
        try {
            await axios.delete(`${API_BASE_URL}/api/history/${jobIdToDelete}`);
            await loadHistory();
        } catch (err) {
            setError('Failed to delete job');
        }
    };

    const viewHistoryJob = async (historyJob) => {
        setSelectedHistoryJob(historyJob);
        setJobId(historyJob.job_id);
        try {
            // Load slides
            const slidesRes = await axios.get(`${API_BASE_URL}/api/slides/${historyJob.job_id}`);
            setSlides(slidesRes.data.slides || []);
            // Load violations if completed
            if (historyJob.status === 'completed') {
                const violRes = await axios.get(`${API_BASE_URL}/api/download/${historyJob.job_id}/violations`);
                setViolations(violRes.data.all_violations || []);
            }
            setView('history-detail');
        } catch (err) {
            setError('Failed to load job details');
        }
    };

    const handleUploadForPreview = async () => {
        if (!pptxFile || !metadataFile) {
            setError('Please upload both PowerPoint and metadata files');
            return;
        }
        setError(null);
        const formData = new FormData();
        formData.append('pptx_file', pptxFile);
        formData.append('metadata_file', metadataFile);
        formData.append('extraction_method', extractionMethod);
        if (extractionMethod === 'SL') {
            formData.append('parallel_workers', parallelWorkers);
        }
        try {
            const response = await axios.post(`${API_BASE_URL}/api/upload-preview`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setJobId(response.data.job_id);
            setSlides(response.data.slides || []);
            setView('preview');
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed');
        }
    };

    const handleStartCheck = async () => {
        if (!jobId) { setError('No job ID found'); return; }
        setError(null);
        setView('processing');
        const modulesStr = selectedModules.length === MODULES.length ? 'all' : selectedModules.join(',');
        const formData = new FormData();
        formData.append('job_id', jobId);
        formData.append('modules', modulesStr);
        try {
            await axios.post(`${API_BASE_URL}/api/check-modules`, formData);
        } catch (err) {
            setError(err.response?.data?.detail || 'Check failed');
            setView('preview');
        }
    };

    const handleRerunCheck = async () => { setShowModuleSelector(false); await handleStartCheck(); };
    const toggleModule = (moduleId) => { setSelectedModules(prev => prev.includes(moduleId) ? prev.filter(id => id !== moduleId) : [...prev, moduleId]); };
    const toggleAllModules = () => { setSelectedModules(prev => prev.length === MODULES.length ? [] : MODULES.map(m => m.id)); };
    const handleReset = () => { setView('upload'); setPptxFile(null); setMetadataFile(null); setJobId(null); setJobStatus(null); setSlides([]); setViolations([]); setError(null); setSelectedSlide(0); setSelectedModules(MODULES.map(m => m.id)); setExtractedJson(null); setShowModuleSelector(false); };

    const downloadReport = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/download/${jobId}/report`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a'); link.href = url; link.setAttribute('download', 'compliance_report.txt');
            document.body.appendChild(link); link.click(); link.remove();
        } catch (err) { setError('Failed to download report'); }
    };

    const downloadJSON = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/download/${jobId}/violations`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a'); link.href = url; link.setAttribute('download', 'violations.json');
            document.body.appendChild(link); link.click(); link.remove();
        } catch (err) { setError('Failed to download JSON'); }
    };

    const slideViolations = violations.filter(v => v.page_number === selectedSlide + 1);
    const stats = { total: violations.length, critical: violations.filter(v => v.severity === 'critical').length, major: violations.filter(v => v.severity === 'major').length, minor: violations.filter(v => v.severity === 'minor').length };

    // LANDING PAGE - Dark Theme, Humanized
    if (view === 'landing') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900">

                <div className="relative max-w-6xl mx-auto px-8 py-16">
                    {/* Hero */}
                    <div className="text-center mb-20">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-sm mb-6">
                            <Sparkles className="w-4 h-4" /> AI-Powered Compliance
                        </div>
                        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
                            Stop worrying about<br />
                            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">compliance mistakes</span>
                        </h1>
                        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                            We know how stressful it is to manually check every slide for regulatory issues.
                            Let our AI do the heavy lifting while you focus on what matters most.
                        </p>
                        <div className="flex gap-4 justify-center">
                            <button onClick={() => setView('upload')}
                                className="group px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-white font-bold rounded-xl text-lg transition-all transform hover:scale-105 shadow-lg shadow-emerald-500/25 flex items-center gap-3">
                                Check My Presentation <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </button>
                            <button onClick={() => { loadHistory(); setView('history'); }}
                                className="px-8 py-4 bg-gray-800 hover:bg-gray-700 text-white font-bold rounded-xl text-lg transition-all border border-gray-700 flex items-center gap-3">
                                <History className="w-5 h-5" /> View History
                            </button>
                        </div>
                    </div>

                    {/* Trust indicators */}
                    <div className="flex justify-center gap-8 mb-20 text-gray-500 text-sm">
                        <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-500" /> 8 Compliance Modules</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-500" /> Instant Results</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-500" /> Detailed Reports</div>
                    </div>

                    {/* Features */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
                        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-2xl p-6 hover:border-emerald-500/30 transition-all">
                            <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-4">
                                <Shield className="w-6 h-6 text-emerald-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">Complete Coverage</h3>
                            <p className="text-gray-400 text-sm">ESG, disclaimers, performance, structure, and more - all checked automatically.</p>
                        </div>
                        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-2xl p-6 hover:border-cyan-500/30 transition-all">
                            <div className="w-12 h-12 bg-cyan-500/10 rounded-xl flex items-center justify-center mb-4">
                                <FileSearch className="w-6 h-6 text-cyan-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">Smart Analysis</h3>
                            <p className="text-gray-400 text-sm">Our AI understands context, not just keywords. Fewer false positives, more accuracy.</p>
                        </div>
                        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-2xl p-6 hover:border-purple-500/30 transition-all">
                            <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-4">
                                <Zap className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">Save Hours</h3>
                            <p className="text-gray-400 text-sm">What used to take hours of manual review now takes minutes. Time is money.</p>
                        </div>
                        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-2xl p-6 hover:border-orange-500/30 transition-all">
                            <div className="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center mb-4">
                                <Users className="w-6 h-6 text-orange-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">Clear Guidance</h3>
                            <p className="text-gray-400 text-sm">Every issue comes with a clear explanation and how to fix it. No guesswork.</p>
                        </div>
                    </div>

                    {/* How it works */}
                    <div className="bg-gray-800/30 backdrop-blur border border-gray-700/50 rounded-3xl p-10 mb-20">
                        <h2 className="text-2xl font-bold text-white text-center mb-10">How it works</h2>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                            {[
                                { step: '1', title: 'Upload', desc: 'Drop your PowerPoint and metadata file' },
                                { step: '2', title: 'Preview', desc: 'See your slides and pick which checks to run' },
                                { step: '3', title: 'Analyze', desc: 'Our AI scans every slide for issues' },
                                { step: '4', title: 'Fix', desc: 'Get a clear list of what needs attention' }
                            ].map((item, idx) => (
                                <div key={idx} className="text-center">
                                    <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-cyan-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">{item.step}</div>
                                    <h4 className="font-semibold text-white mb-2">{item.title}</h4>
                                    <p className="text-gray-400 text-sm">{item.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* CTA */}
                    <div className="text-center">
                        <p className="text-gray-400 mb-6">Ready to make compliance less painful?</p>
                        <button onClick={() => setView('upload')}
                            className="px-8 py-4 bg-white hover:bg-gray-100 text-gray-900 font-bold rounded-xl text-lg transition-all transform hover:scale-105">
                            Get Started - It's Free
                        </button>
                    </div>
                </div>
            </div >
        );
    }

    // UPLOAD VIEW - Dark Theme
    if (view === 'upload') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-8">
                <div className="max-w-4xl mx-auto">
                    <div className="flex justify-between items-center mb-6">
                        <button onClick={() => setView('landing')} className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-medium">
                            <Home className="w-5 h-5" /> Back to Home
                        </button>
                        <button onClick={() => { loadHistory(); setView('history'); }} className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition">
                            <History className="w-4 h-4" /> View History
                        </button>
                    </div>
                    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-2xl p-8">
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-white mb-2">Upload Your Files</h1>
                            <p className="text-gray-400">Let's get your presentation checked</p>
                        </div>
                        {error && (
                            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
                                <AlertCircle className="w-5 h-5 text-red-400" />
                                <span className="text-red-300">{error}</span>
                            </div>
                        )}
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">PowerPoint File <span className="text-red-400">*</span></label>
                                <div onClick={() => document.getElementById('pptx-input').click()}
                                    className="border-2 border-dashed border-emerald-500/30 rounded-xl p-8 text-center hover:border-emerald-500/60 transition cursor-pointer bg-emerald-500/5">
                                    <Upload className="w-12 h-12 mx-auto text-emerald-400 mb-3" />
                                    <p className="text-gray-300 font-medium">{pptxFile ? pptxFile.name : 'Click to upload PowerPoint (.pptx)'}</p>
                                    <input id="pptx-input" type="file" accept=".pptx" onChange={(e) => setPptxFile(e.target.files[0])} className="hidden" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">Metadata File <span className="text-red-400">*</span></label>
                                <div onClick={() => document.getElementById('metadata-input').click()}
                                    className="border-2 border-dashed border-cyan-500/30 rounded-xl p-8 text-center hover:border-cyan-500/60 transition cursor-pointer bg-cyan-500/5">
                                    <FileText className="w-12 h-12 mx-auto text-cyan-400 mb-3" />
                                    <p className="text-gray-300 font-medium">{metadataFile ? metadataFile.name : 'Click to upload Metadata (.json)'}</p>
                                    <input id="metadata-input" type="file" accept=".json" onChange={(e) => setMetadataFile(e.target.files[0])} className="hidden" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">Extraction Method</label>
                                <div className="grid grid-cols-2 gap-3">
                                    {EXTRACTION_METHODS.map(method => (
                                        <div key={method.id} onClick={() => setExtractionMethod(method.id)}
                                            className={`p-4 border-2 rounded-xl cursor-pointer transition ${extractionMethod === method.id ? 'border-emerald-500 bg-emerald-500/10' : 'border-gray-700 hover:border-gray-600 bg-gray-800/50'}`}>
                                            <p className="font-medium text-white">{method.name}</p>
                                            <p className="text-xs text-gray-400">{method.description}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {extractionMethod === 'SL' && (
                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">
                                        Parallel Workers: <span className="text-emerald-400">{parallelWorkers}</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="1"
                                        max="8"
                                        value={parallelWorkers}
                                        onChange={(e) => setParallelWorkers(parseInt(e.target.value))}
                                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                                    />
                                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                                        <span>1 (slower)</span>
                                        <span>8 (faster)</span>
                                    </div>
                                    <p className="text-xs text-gray-400 mt-2">More workers = faster extraction but more API calls at once</p>
                                </div>
                            )}
                            <button onClick={handleUploadForPreview} disabled={!pptxFile || !metadataFile}
                                className="w-full py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white font-bold rounded-xl transition text-lg flex items-center justify-center gap-2">
                                <Eye className="w-6 h-6" /> Upload & Preview
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // PREVIEW VIEW - Dark Theme - Redesigned for larger slide display
    if (view === 'preview') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-4">
                <div className="max-w-[1600px] mx-auto">
                    <div className="mb-4 flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-white">Preview & Select Modules</h1>
                        <div className="flex gap-2">
                            <button onClick={loadExtractedJson} className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition flex items-center gap-2">
                                <Code className="w-4 h-4" /> View JSON
                            </button>
                            <button onClick={() => { loadHistory(); setView('history'); }} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition flex items-center gap-2">
                                <History className="w-4 h-4" /> History
                            </button>
                            <button onClick={handleReset} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition">New File</button>
                        </div>
                    </div>
                    {error && <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3"><AlertCircle className="w-5 h-5 text-red-400" /><span className="text-red-300">{error}</span></div>}

                    {/* Main layout: Slide thumbnails on left, large preview in center, modules on right */}
                    <div className="flex gap-4">
                        {/* Slide Thumbnails - Narrow column */}
                        <div className="w-48 flex-shrink-0 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-3">
                            <h2 className="font-semibold text-white mb-3 text-sm">Slides ({slides.length})</h2>
                            <div className="space-y-2 max-h-[calc(100vh-200px)] overflow-y-auto">
                                {slides.map((slide, idx) => (
                                    <div key={idx} onClick={() => setSelectedSlide(idx)}
                                        className={`p-2 border-2 rounded-lg cursor-pointer transition ${selectedSlide === idx ? 'border-emerald-500 bg-emerald-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                                        <div className="flex items-center gap-2">
                                            <div className="w-6 h-6 bg-emerald-600 text-white rounded flex items-center justify-center font-bold text-xs">{idx + 1}</div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-xs font-medium text-white truncate">{slide.title || `Slide ${idx + 1}`}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Large Slide Preview - Takes most space */}
                        <div className="flex-1 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
                            <div className="flex justify-between items-center mb-3">
                                <h2 className="font-semibold text-white">Slide {selectedSlide + 1} of {slides.length}</h2>
                                <div className="flex gap-2">
                                    <button onClick={() => setSelectedSlide(Math.max(0, selectedSlide - 1))} disabled={selectedSlide === 0}
                                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white rounded text-sm">← Prev</button>
                                    <button onClick={() => setSelectedSlide(Math.min(slides.length - 1, selectedSlide + 1))} disabled={selectedSlide === slides.length - 1}
                                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white rounded text-sm">Next →</button>
                                </div>
                            </div>
                            {slides[selectedSlide] && (
                                <div className="border-2 border-gray-700 rounded-lg bg-gray-900 overflow-hidden flex items-center justify-center" style={{ aspectRatio: '16/9', maxHeight: 'calc(100vh - 280px)' }}>
                                    {slides[selectedSlide].image ? (
                                        <img src={slides[selectedSlide].image} alt={`Slide ${selectedSlide + 1}`} className="max-w-full max-h-full object-contain" />
                                    ) : (
                                        <div className="p-8 w-full h-full overflow-auto">
                                            {slides[selectedSlide].title && <h3 className="text-2xl font-bold text-white mb-6">{slides[selectedSlide].title}</h3>}
                                            <div className="space-y-3">{slides[selectedSlide].content?.map((item, idx) => (!item.is_title && <p key={idx} className="text-base text-gray-300">{item.text}</p>))}</div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                        {/* Modules - Compact column on right */}
                        <div className="w-64 flex-shrink-0 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-3">
                            <div className="flex justify-between items-center mb-3">
                                <h2 className="font-semibold text-white text-sm">Modules</h2>
                                <button onClick={toggleAllModules} className="text-xs text-emerald-400 hover:text-emerald-300 font-medium">
                                    {selectedModules.length === MODULES.length ? 'None' : 'All'}
                                </button>
                            </div>
                            <div className="space-y-1 mb-3 max-h-[calc(100vh-300px)] overflow-y-auto">
                                {MODULES.map(module => (
                                    <div key={module.id} onClick={() => toggleModule(module.id)}
                                        className={`p-2 border rounded-lg cursor-pointer transition ${selectedModules.includes(module.id) ? 'border-emerald-500 bg-emerald-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                                        <div className="flex items-center gap-2">
                                            {selectedModules.includes(module.id) ? <CheckSquare className="w-4 h-4 text-emerald-400" /> : <Square className="w-4 h-4 text-gray-500" />}
                                            <div>
                                                <p className="text-sm font-medium text-white">{module.name}</p>
                                                <p className="text-xs text-gray-500">{module.description}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <button onClick={handleStartCheck} disabled={selectedModules.length === 0}
                                className="w-full py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 disabled:from-gray-600 disabled:to-gray-600 text-white font-bold rounded-lg transition flex items-center justify-center gap-2 text-sm">
                                <Play className="w-4 h-4" /> Run ({selectedModules.length})
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // PROCESSING VIEW - Dark Theme
    if (view === 'processing') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-8 flex items-center justify-center">
                <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-2xl p-12 max-w-md w-full text-center">
                    <Loader className="w-16 h-16 mx-auto text-emerald-400 animate-spin mb-6" />
                    <h2 className="text-2xl font-bold text-white mb-4">{jobStatus?.status === 'pending' ? 'Starting up...' : 'Analyzing your presentation'}</h2>
                    <p className="text-gray-400 mb-4">{jobStatus?.message || 'This usually takes a minute or two...'}</p>
                    {jobStatus?.progress !== undefined && (
                        <div className="w-full bg-gray-700 rounded-full h-2 mt-6">
                            <div className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-2 rounded-full transition-all duration-500" style={{ width: `${jobStatus.progress}%` }}></div>
                        </div>
                    )}
                    <div className="mt-6 text-sm text-gray-500">
                        <div className="flex items-center justify-center gap-2"><Clock className="w-4 h-4" /><span>Running {selectedModules.length} module(s)</span></div>
                    </div>
                </div>
            </div>
        );
    }

    // JSON VIEWER - Dark Theme
    if (view === 'json-viewer') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-4">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-4 flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-white">Extracted JSON Data</h1>
                        <div className="flex gap-2">
                            <button onClick={() => setView('preview')} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition">Back to Preview</button>
                            <button onClick={handleReset} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition">New File</button>
                        </div>
                    </div>
                    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
                        <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-[700px]">
                            <pre className="text-emerald-400 text-sm font-mono whitespace-pre-wrap">{extractedJson ? JSON.stringify(extractedJson, null, 2) : 'Loading...'}</pre>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // RESULTS VIEW - Dark Theme
    if (view === 'results') {
        const getSeverityColor = (severity) => {
            switch (severity) {
                case 'critical': return 'bg-red-500/10 text-red-300 border-red-500/30';
                case 'major': return 'bg-orange-500/10 text-orange-300 border-orange-500/30';
                case 'minor': return 'bg-yellow-500/10 text-yellow-300 border-yellow-500/30';
                default: return 'bg-gray-500/10 text-gray-300 border-gray-500/30';
            }
        };
        const getSeverityIcon = (severity) => {
            switch (severity) {
                case 'critical': return <XCircle className="w-5 h-5" />;
                case 'major': return <AlertCircle className="w-5 h-5" />;
                case 'minor': return <Info className="w-5 h-5" />;
                default: return <CheckCircle className="w-5 h-5" />;
            }
        };

        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-4">
                <div className="max-w-[1600px] mx-auto">
                    <div className="mb-4 flex justify-between items-start">
                        <div>
                            <h1 className="text-2xl font-bold text-white mb-1">Compliance Report</h1>
                            <p className="text-gray-400">{violations.length} issues found across {slides.length} slides</p>
                        </div>
                        <div className="flex gap-2">
                            <button onClick={loadExtractedJson} className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition flex items-center gap-2"><Code className="w-4 h-4" /> JSON</button>
                            <button onClick={() => setShowModuleSelector(!showModuleSelector)} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition flex items-center gap-2"><RefreshCw className="w-4 h-4" /> Re-run</button>
                            <button onClick={() => { loadHistory(); setView('history'); }} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition flex items-center gap-2"><History className="w-4 h-4" /> History</button>
                            <button onClick={handleReset} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition">New Check</button>
                        </div>
                    </div>

                    {showModuleSelector && (
                        <div className="mb-4 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
                            <div className="flex justify-between items-center mb-3">
                                <h3 className="font-semibold text-white">Select Modules to Re-run</h3>
                                <button onClick={toggleAllModules} className="text-sm text-emerald-400">{selectedModules.length === MODULES.length ? 'Deselect All' : 'Select All'}</button>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
                                {MODULES.map(module => (
                                    <div key={module.id} onClick={() => toggleModule(module.id)}
                                        className={`p-2 border-2 rounded-lg cursor-pointer transition text-center ${selectedModules.includes(module.id) ? 'border-emerald-500 bg-emerald-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                                        <div className="flex items-center justify-center gap-1">
                                            {selectedModules.includes(module.id) ? <CheckSquare className="w-4 h-4 text-emerald-400" /> : <Square className="w-4 h-4 text-gray-500" />}
                                            <span className="text-sm font-medium text-white">{module.name}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <button onClick={handleRerunCheck} disabled={selectedModules.length === 0}
                                className="w-full py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-bold rounded-lg transition flex items-center justify-center gap-2">
                                <Play className="w-4 h-4" /> Run ({selectedModules.length})
                            </button>
                        </div>
                    )}

                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
                            <div className="text-2xl font-bold text-white">{stats.total}</div>
                            <div className="text-sm text-gray-400">Total Issues</div>
                        </div>
                        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                            <div className="text-2xl font-bold text-red-400">{stats.critical}</div>
                            <div className="text-sm text-red-300">Critical</div>
                        </div>
                        <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4">
                            <div className="text-2xl font-bold text-orange-400">{stats.major}</div>
                            <div className="text-sm text-orange-300">Major</div>
                        </div>
                        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                            <div className="text-2xl font-bold text-yellow-400">{stats.minor}</div>
                            <div className="text-sm text-yellow-300">Minor</div>
                        </div>
                    </div>

                    {/* Results layout: Slides list | Large Preview | Violations */}
                    <div className="flex gap-4">
                        {/* Slides - Narrow column */}
                        <div className="w-48 flex-shrink-0 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-3">
                            <h2 className="font-semibold text-white mb-3 text-sm">Slides</h2>
                            <div className="space-y-2 max-h-[calc(100vh-350px)] overflow-y-auto">
                                {slides.map((slide, idx) => {
                                    const slideViols = violations.filter(v => v.page_number === idx + 1);
                                    const hasCritical = slideViols.some(v => v.severity === 'critical');
                                    const hasMajor = slideViols.some(v => v.severity === 'major');
                                    const hasMinor = slideViols.some(v => v.severity === 'minor');
                                    return (
                                        <div key={idx} onClick={() => setSelectedSlide(idx)}
                                            className={`p-2 border-2 rounded-lg cursor-pointer transition ${selectedSlide === idx ? 'border-emerald-500 bg-emerald-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                                            <div className="flex items-center gap-2">
                                                <div className={`w-6 h-6 rounded flex items-center justify-center font-bold text-xs text-white ${hasCritical ? 'bg-red-600' : hasMajor ? 'bg-orange-600' : hasMinor ? 'bg-yellow-600' : 'bg-emerald-600'}`}>{idx + 1}</div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-xs font-medium text-white truncate">{slide.title || `Slide ${idx + 1}`}</p>
                                                    <p className="text-xs text-gray-500">{slideViols.length} issue{slideViols.length !== 1 ? 's' : ''}</p>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                        {/* Large Preview - Takes most space */}
                        <div className="flex-1 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
                            <div className="flex justify-between items-center mb-3">
                                <h2 className="font-semibold text-white">Slide {selectedSlide + 1} of {slides.length}</h2>
                                <div className="flex gap-2">
                                    <button onClick={() => setSelectedSlide(Math.max(0, selectedSlide - 1))} disabled={selectedSlide === 0}
                                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white rounded text-sm">← Prev</button>
                                    <button onClick={() => setSelectedSlide(Math.min(slides.length - 1, selectedSlide + 1))} disabled={selectedSlide === slides.length - 1}
                                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white rounded text-sm">Next →</button>
                                </div>
                            </div>
                            {slides[selectedSlide] && (
                                <div className="border-2 border-gray-700 rounded-lg bg-gray-900 overflow-hidden flex items-center justify-center" style={{ aspectRatio: '16/9', maxHeight: 'calc(100vh - 400px)' }}>
                                    {slides[selectedSlide].image ? (
                                        <img src={slides[selectedSlide].image} alt={`Slide ${selectedSlide + 1}`} className="max-w-full max-h-full object-contain" />
                                    ) : (
                                        <div className="p-8 w-full h-full overflow-auto">
                                            {slides[selectedSlide].title && <h3 className="text-2xl font-bold text-white mb-6">{slides[selectedSlide].title}</h3>}
                                            <div className="space-y-3">{slides[selectedSlide].content?.map((item, idx) => (!item.is_title && <p key={idx} className="text-base text-gray-300">{item.text}</p>))}</div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                        {/* Violations - Right column */}
                        <div className="w-80 flex-shrink-0 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-3">
                            <h2 className="font-semibold text-white mb-3 text-sm">Issues ({slideViolations.length})</h2>
                            <div className="space-y-2 max-h-[calc(100vh-350px)] overflow-y-auto">
                                {slideViolations.length === 0 ? (
                                    <div className="text-center py-8 text-gray-400">
                                        <CheckCircle className="w-10 h-10 mx-auto mb-2 text-emerald-500" />
                                        <p className="text-sm">No issues on this slide</p>
                                    </div>
                                ) : (
                                    slideViolations.map((violation, idx) => (
                                        <div key={idx} className={`border-2 rounded-lg p-3 ${getSeverityColor(violation.severity)}`}>
                                            <div className="flex items-start gap-2">
                                                {getSeverityIcon(violation.severity)}
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                                                        <span className="text-xs font-bold px-2 py-0.5 bg-black/20 rounded">{violation.rule_id}</span>
                                                        <span className="text-xs font-semibold px-2 py-0.5 bg-black/20 rounded">{violation.module}</span>
                                                    </div>
                                                    <p className="text-sm font-medium mb-1">{violation.violation_comment}</p>
                                                    {violation.exact_phrase && <p className="text-xs italic bg-black/10 p-2 rounded mt-2">"{violation.exact_phrase}"</p>}
                                                    {violation.required_action && <p className="text-xs mt-2 opacity-80"><strong>Fix:</strong> {violation.required_action}</p>}
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                    {/* Downloads */}
                    <div className="mt-4 flex gap-4 justify-center">
                        <button onClick={downloadReport} className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg flex items-center gap-2 transition">
                            <Download className="w-5 h-5" /> Download Report
                        </button>
                        <button onClick={downloadJSON} className="px-6 py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-lg flex items-center gap-2 transition">
                            <Download className="w-5 h-5" /> Download JSON
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // HISTORY VIEW - Review workflow
    if (view === 'history') {
        const getStatusBadge = (status) => {
            switch (status) {
                case 'completed': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
                case 'failed': return 'bg-red-500/20 text-red-400 border-red-500/30';
                case 'processing': case 'pending': case 'preview': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
                default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
            }
        };
        const getReviewBadge = (reviewStatus) => {
            switch (reviewStatus) {
                case 'validated': return { bg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: <CheckCircle className="w-4 h-4" />, label: 'Validated' };
                case 'needs_revision': return { bg: 'bg-orange-500/20 text-orange-400 border-orange-500/30', icon: <AlertTriangle className="w-4 h-4" />, label: 'Needs Revision' };
                default: return { bg: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', icon: <Clock className="w-4 h-4" />, label: 'Pending Review' };
            }
        };

        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-4">
                <div className="max-w-[1400px] mx-auto">
                    <div className="mb-6 flex justify-between items-center">
                        <div>
                            <h1 className="text-2xl font-bold text-white mb-1">Compliance History</h1>
                            <p className="text-gray-400">Review and manage all compliance checks</p>
                        </div>
                        <div className="flex gap-2">
                            <button onClick={loadHistory} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition flex items-center gap-2">
                                <RefreshCw className="w-4 h-4" /> Refresh
                            </button>
                            <button onClick={() => setView('landing')} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition flex items-center gap-2">
                                <Home className="w-4 h-4" /> Home
                            </button>
                        </div>
                    </div>

                    {/* Stats Cards */}
                    {historyStats && (
                        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
                            <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
                                <div className="text-2xl font-bold text-white">{historyStats.total_jobs}</div>
                                <div className="text-xs text-gray-400">Total Jobs</div>
                            </div>
                            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4">
                                <div className="text-2xl font-bold text-emerald-400">{historyStats.by_status?.completed || 0}</div>
                                <div className="text-xs text-emerald-300">Completed</div>
                            </div>
                            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                                <div className="text-2xl font-bold text-blue-400">{historyStats.by_status?.processing || 0}</div>
                                <div className="text-xs text-blue-300">Processing</div>
                            </div>
                            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                                <div className="text-2xl font-bold text-yellow-400">{historyStats.by_review?.pending_review || 0}</div>
                                <div className="text-xs text-yellow-300">Pending Review</div>
                            </div>
                            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                                <div className="text-2xl font-bold text-green-400">{historyStats.by_review?.validated || 0}</div>
                                <div className="text-xs text-green-300">Validated</div>
                            </div>
                            <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4">
                                <div className="text-2xl font-bold text-orange-400">{historyStats.by_review?.needs_revision || 0}</div>
                                <div className="text-xs text-orange-300">Needs Revision</div>
                            </div>
                        </div>
                    )}

                    {/* History Table */}
                    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-900/50">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">File</th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Date</th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Status</th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Violations</th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Review Status</th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700/50">
                                {historyData.length === 0 ? (
                                    <tr><td colSpan="6" className="px-4 py-8 text-center text-gray-500">No compliance checks yet</td></tr>
                                ) : (
                                    historyData.map((job) => {
                                        const reviewBadge = getReviewBadge(job.review_status);
                                        return (
                                            <tr key={job.job_id} className="hover:bg-gray-700/30 transition">
                                                <td className="px-4 py-3">
                                                    <div className="flex items-center gap-2">
                                                        <FileText className="w-4 h-4 text-gray-500" />
                                                        <span className="text-sm text-white font-medium truncate max-w-[200px]">{job.filename}</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-400">
                                                    {new Date(job.created_at).toLocaleDateString()} {new Date(job.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusBadge(job.status)}`}>
                                                        {job.status}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-sm text-white">{job.total_violations}</span>
                                                        {job.critical_violations > 0 && (
                                                            <span className="px-1.5 py-0.5 text-xs bg-red-500/20 text-red-400 rounded">{job.critical_violations} critical</span>
                                                        )}
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-1 text-xs font-medium rounded border flex items-center gap-1 w-fit ${reviewBadge.bg}`}>
                                                        {reviewBadge.icon} {reviewBadge.label}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="flex items-center gap-1">
                                                        <button onClick={() => viewHistoryJob(job)} className="p-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded transition" title="View Details">
                                                            <Eye className="w-4 h-4" />
                                                        </button>
                                                        {job.status === 'completed' && job.review_status === 'pending_review' && (
                                                            <>
                                                                <button onClick={() => updateReviewStatus(job.job_id, 'validated')} className="p-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded transition" title="Validate">
                                                                    <ClipboardCheck className="w-4 h-4" />
                                                                </button>
                                                                <button onClick={() => updateReviewStatus(job.job_id, 'needs_revision')} className="p-1.5 bg-orange-600 hover:bg-orange-500 text-white rounded transition" title="Needs Revision">
                                                                    <AlertTriangle className="w-4 h-4" />
                                                                </button>
                                                            </>
                                                        )}
                                                        {job.review_status === 'validated' && (
                                                            <button className="p-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded transition" title="Send to Owner">
                                                                <Send className="w-4 h-4" />
                                                            </button>
                                                        )}
                                                        <button onClick={() => deleteHistoryJob(job.job_id)} className="p-1.5 bg-red-600 hover:bg-red-500 text-white rounded transition" title="Delete">
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    }

    // HISTORY DETAIL VIEW - View a specific job from history
    if (view === 'history-detail' && selectedHistoryJob) {
        const reviewBadge = (() => {
            switch (selectedHistoryJob.review_status) {
                case 'validated': return { bg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', label: 'Validated' };
                case 'needs_revision': return { bg: 'bg-orange-500/20 text-orange-400 border-orange-500/30', label: 'Needs Revision' };
                default: return { bg: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', label: 'Pending Review' };
            }
        })();

        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-4">
                <div className="max-w-[1600px] mx-auto">
                    <div className="mb-4 flex justify-between items-start">
                        <div>
                            <h1 className="text-2xl font-bold text-white mb-1">{selectedHistoryJob.filename}</h1>
                            <div className="flex items-center gap-3">
                                <span className="text-gray-400 text-sm">{new Date(selectedHistoryJob.created_at).toLocaleString()}</span>
                                <span className={`px-2 py-1 text-xs font-medium rounded border ${reviewBadge.bg}`}>{reviewBadge.label}</span>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            {selectedHistoryJob.review_status === 'pending_review' && (
                                <>
                                    <button onClick={() => { updateReviewStatus(selectedHistoryJob.job_id, 'validated'); setSelectedHistoryJob({ ...selectedHistoryJob, review_status: 'validated' }); }}
                                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition flex items-center gap-2">
                                        <ClipboardCheck className="w-4 h-4" /> Validate
                                    </button>
                                    <button onClick={() => { updateReviewStatus(selectedHistoryJob.job_id, 'needs_revision'); setSelectedHistoryJob({ ...selectedHistoryJob, review_status: 'needs_revision' }); }}
                                        className="px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white rounded-lg transition flex items-center gap-2">
                                        <AlertTriangle className="w-4 h-4" /> Needs Revision
                                    </button>
                                </>
                            )}
                            <button onClick={() => { loadHistory(); setView('history'); }} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition flex items-center gap-2">
                                <History className="w-4 h-4" /> Back to History
                            </button>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-4 gap-4 mb-4">
                        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
                            <div className="text-2xl font-bold text-white">{violations.length}</div>
                            <div className="text-sm text-gray-400">Total Issues</div>
                        </div>
                        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                            <div className="text-2xl font-bold text-red-400">{violations.filter(v => v.severity === 'critical').length}</div>
                            <div className="text-sm text-red-300">Critical</div>
                        </div>
                        <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4">
                            <div className="text-2xl font-bold text-orange-400">{violations.filter(v => v.severity === 'major').length}</div>
                            <div className="text-sm text-orange-300">Major</div>
                        </div>
                        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                            <div className="text-2xl font-bold text-yellow-400">{violations.filter(v => v.severity === 'minor').length}</div>
                            <div className="text-sm text-yellow-300">Minor</div>
                        </div>
                    </div>

                    {/* Slide Preview and Violations */}
                    <div className="flex gap-4">
                        <div className="w-48 flex-shrink-0 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-3">
                            <h2 className="font-semibold text-white mb-3 text-sm">Slides</h2>
                            <div className="space-y-2 max-h-[calc(100vh-350px)] overflow-y-auto">
                                {slides.map((slide, idx) => {
                                    const slideViols = violations.filter(v => v.page_number === idx + 1);
                                    const hasCritical = slideViols.some(v => v.severity === 'critical');
                                    const hasMajor = slideViols.some(v => v.severity === 'major');
                                    const hasMinor = slideViols.some(v => v.severity === 'minor');
                                    return (
                                        <div key={idx} onClick={() => setSelectedSlide(idx)}
                                            className={`p-2 border-2 rounded-lg cursor-pointer transition ${selectedSlide === idx ? 'border-emerald-500 bg-emerald-500/10' : 'border-gray-700 hover:border-gray-600'}`}>
                                            <div className="flex items-center gap-2">
                                                <div className={`w-6 h-6 rounded flex items-center justify-center font-bold text-xs text-white ${hasCritical ? 'bg-red-600' : hasMajor ? 'bg-orange-600' : hasMinor ? 'bg-yellow-600' : 'bg-emerald-600'}`}>{idx + 1}</div>
                                                <span className="text-xs text-gray-400">{slideViols.length} issues</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                        <div className="flex-1 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
                            <h2 className="font-semibold text-white mb-3">Slide {selectedSlide + 1}</h2>
                            {slides[selectedSlide] && (
                                <div className="border-2 border-gray-700 rounded-lg bg-gray-900 overflow-hidden">
                                    {slides[selectedSlide].image ? (
                                        <img src={slides[selectedSlide].image} alt={`Slide ${selectedSlide + 1}`} className="w-full h-auto max-h-[calc(100vh-400px)] object-contain mx-auto" />
                                    ) : (
                                        <div className="p-8 min-h-[400px]">
                                            {slides[selectedSlide].title && <h3 className="text-2xl font-bold text-white mb-6">{slides[selectedSlide].title}</h3>}
                                            <div className="space-y-3">{slides[selectedSlide].content?.map((item, idx) => (!item.is_title && <p key={idx} className="text-base text-gray-300">{item.text}</p>))}</div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                        <div className="w-80 flex-shrink-0 bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-3">
                            <h2 className="font-semibold text-white mb-3 text-sm">Issues on Slide {selectedSlide + 1}</h2>
                            <div className="space-y-2 max-h-[calc(100vh-350px)] overflow-y-auto">
                                {violations.filter(v => v.page_number === selectedSlide + 1).length === 0 ? (
                                    <div className="text-center py-8 text-gray-400">
                                        <CheckCircle className="w-10 h-10 mx-auto mb-2 text-emerald-500" />
                                        <p className="text-sm">No issues</p>
                                    </div>
                                ) : (
                                    violations.filter(v => v.page_number === selectedSlide + 1).map((violation, idx) => (
                                        <div key={idx} className={`border rounded-lg p-2 ${violation.severity === 'critical' ? 'bg-red-500/10 border-red-500/30 text-red-300' : violation.severity === 'major' ? 'bg-orange-500/10 border-orange-500/30 text-orange-300' : 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300'}`}>
                                            <div className="flex items-center gap-1 mb-1">
                                                <span className="text-xs font-bold px-1.5 py-0.5 bg-black/20 rounded">{violation.rule_id}</span>
                                                <span className="text-xs px-1.5 py-0.5 bg-black/20 rounded">{violation.severity}</span>
                                            </div>
                                            <p className="text-xs">{violation.violation_comment}</p>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return null;
}

export default AppEnhanced;
