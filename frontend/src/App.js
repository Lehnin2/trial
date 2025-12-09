import React, { useState, useEffect } from 'react';
import {
    Upload, CheckCircle, AlertCircle, Info, Download,
    Loader, FileText, Clock, XCircle, ChevronDown, ChevronUp
} from 'lucide-react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
    const [view, setView] = useState('upload'); // upload, processing, results
    const [pptxFile, setPptxFile] = useState(null);
    const [metadataFile, setMetadataFile] = useState(null);
    const [prospectusFile, setProspectusFile] = useState(null);
    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState(null);
    const [violations, setViolations] = useState([]);
    const [error, setError] = useState(null);
    const [expandedViolation, setExpandedViolation] = useState(null);
    const [filterSeverity, setFilterSeverity] = useState('all');
    const [filterModule, setFilterModule] = useState('all');

    // Poll job status when processing
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
                        setView('upload');
                    }
                } catch (err) {
                    console.error('Status check error:', err);
                }
            }, 2000); // Poll every 2 seconds

            return () => clearInterval(interval);
        }
    }, [jobId, view]);


    const loadResults = async (jId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/download/${jId}/violations`);
            const data = response.data;

            // Extract violations from the consolidated format
            const allViolations = data.all_violations || [];
            setViolations(allViolations);
            setView('results');
        } catch (err) {
            console.error('Failed to load results:', err);
            setError('Failed to load compliance results');
        }
    };

    const handleUpload = async () => {
        if (!pptxFile || !metadataFile) {
            setError('Please upload both PowerPoint and metadata files');
            return;
        }

        setError(null);
        setView('processing');

        const formData = new FormData();
        formData.append('pptx_file', pptxFile);
        formData.append('metadata_file', metadataFile);
        if (prospectusFile) {
            formData.append('prospectus_file', prospectusFile);
        }

        try {
            const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setJobId(response.data.job_id);
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed');
            setView('upload');
        }
    };

    const handleReset = () => {
        setView('upload');
        setPptxFile(null);
        setMetadataFile(null);
        setProspectusFile(null);
        setJobId(null);
        setJobStatus(null);
        setViolations([]);
        setError(null);
        setExpandedViolation(null);
    };


    const downloadReport = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/download/${jobId}/report`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'compliance_report.txt');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            setError('Failed to download report');
        }
    };

    const downloadJSON = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/download/${jobId}/violations`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'violations.json');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            setError('Failed to download JSON');
        }
    };

    // Filter violations
    const filteredViolations = violations.filter(v => {
        const severityMatch = filterSeverity === 'all' || v.severity === filterSeverity;
        const moduleMatch = filterModule === 'all' || v.module === filterModule;
        return severityMatch && moduleMatch;
    });

    // Calculate stats
    const stats = {
        total: violations.length,
        critical: violations.filter(v => v.severity === 'critical').length,
        major: violations.filter(v => v.severity === 'major').length,
        minor: violations.filter(v => v.severity === 'minor').length,
    };

    const modules = [...new Set(violations.map(v => v.module))];


    // UPLOAD VIEW
    if (view === 'upload') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-white rounded-xl shadow-2xl p-8">
                        <div className="text-center mb-8">
                            <h1 className="text-4xl font-bold text-gray-900 mb-2">
                                📊 PowerPoint Compliance Checker
                            </h1>
                            <p className="text-gray-600 text-lg">
                                Automated regulatory compliance validation for financial presentations
                            </p>
                        </div>

                        {error && (
                            <div className="mb-6 p-4 bg-red-50 border border-red-300 rounded-lg flex items-center gap-3">
                                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                                <span className="text-red-800">{error}</span>
                            </div>
                        )}

                        <div className="space-y-6">
                            {/* PPTX File Upload */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    PowerPoint File <span className="text-red-500">*</span>
                                </label>
                                <div
                                    className="border-2 border-dashed border-indigo-300 rounded-lg p-6 text-center hover:border-indigo-500 transition cursor-pointer bg-indigo-50/50"
                                    onClick={() => document.getElementById('pptx-input').click()}
                                >
                                    <Upload className="w-12 h-12 mx-auto text-indigo-600 mb-2" />
                                    <p className="text-gray-700 font-medium">
                                        {pptxFile ? pptxFile.name : 'Click to upload PowerPoint (.pptx)'}
                                    </p>
                                    <input
                                        id="pptx-input"
                                        type="file"
                                        accept=".pptx"
                                        onChange={(e) => setPptxFile(e.target.files[0])}
                                        className="hidden"
                                    />
                                </div>
                            </div>


                            {/* Metadata File Upload */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Metadata File <span className="text-red-500">*</span>
                                </label>
                                <div
                                    className="border-2 border-dashed border-green-300 rounded-lg p-6 text-center hover:border-green-500 transition cursor-pointer bg-green-50/50"
                                    onClick={() => document.getElementById('metadata-input').click()}
                                >
                                    <FileText className="w-12 h-12 mx-auto text-green-600 mb-2" />
                                    <p className="text-gray-700 font-medium">
                                        {metadataFile ? metadataFile.name : 'Click to upload Metadata (.json)'}
                                    </p>
                                    <input
                                        id="metadata-input"
                                        type="file"
                                        accept=".json"
                                        onChange={(e) => setMetadataFile(e.target.files[0])}
                                        className="hidden"
                                    />
                                </div>
                            </div>

                            {/* Prospectus File Upload (Optional) */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Prospectus File <span className="text-gray-400">(Optional)</span>
                                </label>
                                <div
                                    className="border-2 border-dashed border-purple-300 rounded-lg p-6 text-center hover:border-purple-500 transition cursor-pointer bg-purple-50/50"
                                    onClick={() => document.getElementById('prospectus-input').click()}
                                >
                                    <FileText className="w-12 h-12 mx-auto text-purple-600 mb-2" />
                                    <p className="text-gray-700 font-medium">
                                        {prospectusFile ? prospectusFile.name : 'Click to upload Prospectus (.docx)'}
                                    </p>
                                    <input
                                        id="prospectus-input"
                                        type="file"
                                        accept=".docx"
                                        onChange={(e) => setProspectusFile(e.target.files[0])}
                                        className="hidden"
                                    />
                                </div>
                            </div>

                            <button
                                onClick={handleUpload}
                                disabled={!pptxFile || !metadataFile}
                                className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-bold rounded-lg transition text-lg"
                            >
                                Start Compliance Check
                            </button>
                        </div>


                        <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
                            <h4 className="font-semibold text-gray-900 mb-3">✅ What we validate:</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>Structure & Format Rules</span>
                                </div>
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>Registration Requirements</span>
                                </div>
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>ESG Compliance</span>
                                </div>
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>Disclaimers & Legal Text</span>
                                </div>
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>Performance Disclosures</span>
                                </div>
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>Securities Mentions</span>
                                </div>
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>Prospectus Alignment</span>
                                </div>
                                <div className="flex gap-2">
                                    <span className="text-blue-600">•</span>
                                    <span>General Regulatory Rules</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }


    // PROCESSING VIEW
    if (view === 'processing') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8 flex items-center justify-center">
                <div className="bg-white rounded-xl shadow-2xl p-12 max-w-md w-full text-center">
                    <Loader className="w-16 h-16 mx-auto text-indigo-600 animate-spin mb-6" />
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                        {jobStatus?.status === 'pending' ? 'Initializing...' : 'Processing Compliance Check'}
                    </h2>
                    <p className="text-gray-600 mb-4">{jobStatus?.message || 'Please wait...'}</p>

                    {jobStatus?.progress !== undefined && (
                        <div className="w-full bg-gray-200 rounded-full h-3 mt-6">
                            <div
                                className="bg-indigo-600 h-3 rounded-full transition-all duration-500"
                                style={{ width: `${jobStatus.progress}%` }}
                            ></div>
                        </div>
                    )}

                    <div className="mt-6 space-y-2 text-sm text-gray-500">
                        <div className="flex items-center justify-center gap-2">
                            <Clock className="w-4 h-4" />
                            <span>This may take a few minutes...</span>
                        </div>
                        {jobId && (
                            <p className="text-xs font-mono text-gray-400">Job ID: {jobId.slice(0, 8)}...</p>
                        )}
                    </div>
                </div>
            </div>
        );
    }


    // RESULTS VIEW
    if (view === 'results') {
        const getSeverityColor = (severity) => {
            switch (severity) {
                case 'critical': return 'bg-red-100 text-red-800 border-red-300';
                case 'major': return 'bg-orange-100 text-orange-800 border-orange-300';
                case 'minor': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
                default: return 'bg-gray-100 text-gray-800 border-gray-300';
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
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="mb-8 flex justify-between items-start">
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900 mb-2">
                                Compliance Report
                            </h1>
                            <p className="text-gray-600">
                                Analysis complete - {violations.length} issues found
                            </p>
                        </div>
                        <button
                            onClick={handleReset}
                            className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold rounded-lg transition"
                        >
                            New Check
                        </button>
                    </div>


                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
                            <div className="text-sm text-gray-600 mt-1">Total Issues</div>
                        </div>
                        <div className="bg-red-50 rounded-lg shadow p-6 border-l-4 border-red-500">
                            <div className="text-3xl font-bold text-red-600">{stats.critical}</div>
                            <div className="text-sm text-red-700 mt-1">Critical</div>
                        </div>
                        <div className="bg-orange-50 rounded-lg shadow p-6 border-l-4 border-orange-500">
                            <div className="text-3xl font-bold text-orange-600">{stats.major}</div>
                            <div className="text-sm text-orange-700 mt-1">Major</div>
                        </div>
                        <div className="bg-yellow-50 rounded-lg shadow p-6 border-l-4 border-yellow-500">
                            <div className="text-3xl font-bold text-yellow-600">{stats.minor}</div>
                            <div className="text-sm text-yellow-700 mt-1">Minor</div>
                        </div>
                    </div>

                    {/* Filters */}
                    <div className="bg-white rounded-lg shadow p-6 mb-8">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Filter by Severity
                                </label>
                                <select
                                    value={filterSeverity}
                                    onChange={(e) => setFilterSeverity(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                >
                                    <option value="all">All Severities</option>
                                    <option value="critical">Critical Only</option>
                                    <option value="major">Major Only</option>
                                    <option value="minor">Minor Only</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Filter by Module
                                </label>
                                <select
                                    value={filterModule}
                                    onChange={(e) => setFilterModule(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                >
                                    <option value="all">All Modules</option>
                                    {modules.map(m => (
                                        <option key={m} value={m}>{m}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Results
                                </label>
                                <div className="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 font-medium">
                                    Showing {filteredViolations.length} of {violations.length}
                                </div>
                            </div>
                        </div>
                    </div>


                    {/* Violations List */}
                    <div className="space-y-4 mb-8">
                        <h2 className="text-lg font-semibold text-gray-900">Issues Found</h2>
                        {filteredViolations.length === 0 ? (
                            <div className="bg-green-50 rounded-lg p-8 text-center border border-green-200">
                                <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
                                <p className="text-green-800 font-semibold text-lg">
                                    {violations.length === 0
                                        ? 'No violations found! Document is compliant.'
                                        : 'No violations match your filters.'}
                                </p>
                            </div>
                        ) : (
                            filteredViolations.map((violation, idx) => (
                                <div
                                    key={idx}
                                    className={`border rounded-lg overflow-hidden transition cursor-pointer ${getSeverityColor(violation.severity)}`}
                                    onClick={() => setExpandedViolation(expandedViolation === idx ? null : idx)}
                                >
                                    <div className="p-4 flex items-start gap-4">
                                        <div className="mt-1">
                                            {getSeverityIcon(violation.severity)}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-start gap-4">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xs font-bold px-2 py-1 bg-black/10 rounded">
                                                            {violation.rule_id}
                                                        </span>
                                                        <span className="text-xs font-semibold px-2 py-1 bg-black/10 rounded">
                                                            {violation.module}
                                                        </span>
                                                        <span className="text-xs font-semibold px-2 py-1 bg-black/10 rounded uppercase">
                                                            {violation.severity}
                                                        </span>
                                                    </div>
                                                    <h3 className="font-semibold text-sm mb-2">
                                                        {violation.violation_comment}
                                                    </h3>
                                                    {violation.page_number > 0 && (
                                                        <p className="text-xs opacity-75">
                                                            📄 Slide {violation.page_number} • {violation.location}
                                                        </p>
                                                    )}
                                                </div>
                                                <div>
                                                    {expandedViolation === idx ? (
                                                        <ChevronUp className="w-5 h-5" />
                                                    ) : (
                                                        <ChevronDown className="w-5 h-5" />
                                                    )}
                                                </div>
                                            </div>

                                            {expandedViolation === idx && (
                                                <div className="mt-4 pt-4 border-t border-current/20 space-y-3">
                                                    {violation.exact_phrase && (
                                                        <div>
                                                            <h4 className="font-semibold text-xs mb-1">Found Text:</h4>
                                                            <p className="text-sm italic opacity-90 bg-black/5 p-2 rounded">
                                                                "{violation.exact_phrase}"
                                                            </p>
                                                        </div>
                                                    )}
                                                    {violation.required_action && (
                                                        <div>
                                                            <h4 className="font-semibold text-xs mb-1">Required Action:</h4>
                                                            <p className="text-sm opacity-90">
                                                                {violation.required_action}
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>


                    {/* Download Buttons */}
                    <div className="flex gap-4 justify-center flex-wrap">
                        <button
                            onClick={downloadReport}
                            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg flex items-center gap-2 transition"
                        >
                            <Download className="w-5 h-5" />
                            Download Report (TXT)
                        </button>
                        <button
                            onClick={downloadJSON}
                            className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg flex items-center gap-2 transition"
                        >
                            <Download className="w-5 h-5" />
                            Download JSON
                        </button>
                        <button
                            onClick={handleReset}
                            className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold rounded-lg transition"
                        >
                            Check Another File
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return null;
}

export default App;
