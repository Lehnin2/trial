import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle, AlertCircle, Info, Download, Filter, Loader } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000'; // Change this for production

export default function ComplianceFrontend() {
  const [stage, setStage] = useState('upload'); // upload, extracting, checking, results
  const [file, setFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [violations, setViolations] = useState([]);
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedViolation, setExpandedViolation] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState('');
  const [extractedFilePath, setExtractedFilePath] = useState(null);

  // Check if backend is available on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        console.warn('Backend not responding');
      }
    } catch (err) {
      console.error('Backend connection error:', err);
    }
  };

  // ===== API CALLS =====

  const extractPPTX = async (file) => {
    try {
      setProgress('Uploading and extracting PPTX...');
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Extraction failed');
      }

      const data = await response.json();
      setProgress('Extraction complete!');
      setExtractedFilePath(data.extracted_file);
      
      return data;
    } catch (err) {
      throw new Error(`Extraction error: ${err.message}`);
    }
  };

  const checkCompliance = async (extractedFilePath) => {
    try {
      setProgress('Running compliance checks against 140+ rules...');

      const response = await fetch(`${API_BASE_URL}/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          json_file_path: extractedFilePath
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Compliance check failed');
      }

      const data = await response.json();
      setProgress('Compliance check complete!');
      
      return data;
    } catch (err) {
      throw new Error(`Compliance check error: ${err.message}`);
    }
  };

  // ===== EVENT HANDLERS =====

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    if (!uploadedFile.name.endsWith('.pptx')) {
      setError('Please upload a .pptx file');
      return;
    }

    setFile(uploadedFile);
    setError(null);
    setStage('extracting');
    
    try {
      // Step 1: Extract PPTX
      const extractionResult = await extractPPTX(uploadedFile);
      setExtractedData(extractionResult);
      
      // Step 2: Check Compliance
      setStage('checking');
      const complianceResult = await checkCompliance(extractionResult.extracted_file);
      
      setViolations(complianceResult.violations || []);
      setProgress('');
      setStage('results');
    } catch (err) {
      setError(err.message);
      setStage('upload');
      setProgress('');
    }
  };

  const filteredViolations = violations.filter(v => {
    const severityMatch = selectedSeverity === 'all' || v.severity === selectedSeverity;
    const categoryMatch = selectedCategory === 'all' || v.section === selectedCategory;
    return severityMatch && categoryMatch;
  });

  const violationStats = {
    critical: violations.filter(v => v.severity === 'critical').length,
    warning: violations.filter(v => v.severity === 'warning').length,
    info: violations.filter(v => v.severity === 'info').length,
    total: violations.length
  };

  const categoryStats = {};
  violations.forEach(v => {
    categoryStats[v.section] = (categoryStats[v.section] || 0) + 1;
  });

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'info': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'critical': return <AlertCircle className="w-5 h-5" />;
      case 'warning': return <AlertCircle className="w-5 h-5" />;
      case 'info': return <Info className="w-5 h-5" />;
      default: return <CheckCircle className="w-5 h-5" />;
    }
  };

  const handleExportJSON = async () => {
    try {
      const reportData = {
        document_name: extractedData?.document_metadata?.document_name,
        total_violations: violationStats.total,
        critical_count: violationStats.critical,
        warning_count: violationStats.warning,
        info_count: violationStats.info,
        violations: violations,
        metadata: extractedData?.document_metadata
      };

      const element = document.createElement('a');
      const file = new Blob([JSON.stringify(reportData, null, 2)], {type: 'application/json'});
      element.href = URL.createObjectURL(file);
      element.download = `compliance_report_${Date.now()}.json`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } catch (err) {
      setError('Failed to export report');
    }
  };

  // ===== UPLOAD STAGE =====
  if (stage === 'upload') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-12">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Compliance Checker
              </h1>
              <p className="text-gray-600 text-lg">
                Upload your PPTX presentation to check for regulatory compliance
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-300 rounded-lg flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span className="text-red-800">{error}</span>
              </div>
            )}

            <div className="border-2 border-dashed border-indigo-300 rounded-lg p-12 text-center hover:border-indigo-500 transition cursor-pointer bg-indigo-50/50"
                 onClick={() => document.getElementById('file-input').click()}>
              <Upload className="w-16 h-16 mx-auto text-indigo-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Drop your file here
              </h3>
              <p className="text-gray-600 mb-4">
                or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Only .pptx files are supported
              </p>
              <input
                id="file-input"
                type="file"
                accept=".pptx"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>

            {file && (
              <div className="mt-4 p-4 bg-green-50 border border-green-300 rounded-lg">
                <p className="text-green-800">
                  ✓ File selected: <span className="font-semibold">{file.name}</span>
                </p>
              </div>
            )}

            <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-gray-900 mb-3">What we check:</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex gap-2">
                  <span className="text-blue-600">✓</span>
                  <span>General rules (disclaimers, structure, glossary)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600">✓</span>
                  <span>ESG compliance and classification</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600">✓</span>
                  <span>Performance disclosures</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600">✓</span>
                  <span>Registration and authorization</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600">✓</span>
                  <span>140+ regulatory compliance rules</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ===== EXTRACTING/CHECKING STAGE =====
  if (stage === 'extracting' || stage === 'checking') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-12 max-w-md w-full text-center">
          <Loader className="w-16 h-16 mx-auto text-indigo-600 animate-spin mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {stage === 'extracting' ? 'Extracting Content' : 'Checking Compliance'}
          </h2>
          <p className="text-gray-600 mb-2">{progress}</p>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-6">
            <div className="bg-indigo-600 h-2 rounded-full animate-pulse" style={{width: '70%'}}></div>
          </div>
          <p className="text-sm text-gray-500 mt-4">
            {stage === 'extracting' 
              ? 'This may take 5-10 minutes depending on file size...' 
              : 'Analyzing against 140+ compliance rules...'}
          </p>
        </div>
      </div>
    );
  }

  // ===== RESULTS STAGE =====
  if (stage === 'results') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Compliance Report
              </h1>
              <p className="text-gray-600">
                {extractedData?.document_metadata?.document_name || 'Presentation'} 
                {extractedData?.document_metadata?.fund_isin && 
                  ` (${extractedData.document_metadata.fund_isin})`}
              </p>
            </div>
            <button
              onClick={() => {
                setStage('upload');
                setFile(null);
                setViolations([]);
                setExtractedData(null);
                setError(null);
              }}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg transition"
            >
              Upload New File
            </button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-gray-900">{violationStats.total}</div>
              <div className="text-sm text-gray-600 mt-1">Total Issues</div>
            </div>
            <div className="bg-red-50 rounded-lg shadow p-6 border-l-4 border-red-500">
              <div className="text-3xl font-bold text-red-600">{violationStats.critical}</div>
              <div className="text-sm text-red-700 mt-1">Critical</div>
            </div>
            <div className="bg-yellow-50 rounded-lg shadow p-6 border-l-4 border-yellow-500">
              <div className="text-3xl font-bold text-yellow-600">{violationStats.warning}</div>
              <div className="text-sm text-yellow-700 mt-1">Warnings</div>
            </div>
            <div className="bg-blue-50 rounded-lg shadow p-6 border-l-4 border-blue-500">
              <div className="text-3xl font-bold text-blue-600">{violationStats.info}</div>
              <div className="text-sm text-blue-700 mt-1">Info</div>
            </div>
          </div>

          {/* Document Info */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Information</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Fund ISIN:</span>
                <p className="font-semibold text-gray-900">
                  {extractedData?.document_metadata?.fund_isin || 'N/A'}
                </p>
              </div>
              <div>
                <span className="text-gray-600">Client Type:</span>
                <p className="font-semibold text-gray-900 capitalize">
                  {extractedData?.document_metadata?.client_type || 'N/A'}
                </p>
              </div>
              <div>
                <span className="text-gray-600">Language:</span>
                <p className="font-semibold text-gray-900">
                  {extractedData?.document_metadata?.language || 'N/A'}
                </p>
              </div>
              <div>
                <span className="text-gray-600">Pages:</span>
                <p className="font-semibold text-gray-900">
                  {extractedData?.document_metadata?.total_slides || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Severity
                </label>
                <select
                  value={selectedSeverity}
                  onChange={(e) => setSelectedSeverity(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="all">All Severities</option>
                  <option value="critical">Critical Only</option>
                  <option value="warning">Warnings Only</option>
                  <option value="info">Info Only</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="all">All Categories</option>
                  <option value="general">General</option>
                  <option value="esg">ESG</option>
                  <option value="performance">Performance</option>
                  <option value="structure">Structure</option>
                  <option value="prospectus">Prospectus</option>
                  <option value="values">Securities</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Results
                </label>
                <div className="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 font-medium">
                  Showing {filteredViolations.length} of {violations.length}
                </div>
              </div>
            </div>
          </div>

          {/* Category Stats */}
          {Object.keys(categoryStats).length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Violations by Category</h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                {Object.entries(categoryStats).map(([cat, count]) => (
                  <div key={cat} className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-600">{count}</div>
                    <div className="text-xs text-gray-600 capitalize mt-1">{cat}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Violations List */}
          <div className="space-y-4">
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
                        <div>
                          <h3 className="font-semibold text-sm">
                            [{violation.rule_id}] {violation.rule_text}
                          </h3>
                          <p className="text-sm mt-1">
                            {violation.message}
                          </p>
                          {violation.slide && (
                            <p className="text-xs mt-2 opacity-75">
                              Slide {violation.slide}
                            </p>
                          )}
                        </div>
                        <span className="text-xs font-semibold px-2 py-1 bg-black/10 rounded">
                          {violation.severity}
                        </span>
                      </div>

                      {expandedViolation === idx && (
                        <div className="mt-4 pt-4 border-t border-current/20 space-y-3">
                          {violation.suggested_fix && (
                            <div>
                              <h4 className="font-semibold text-xs mb-1">Suggested Fix:</h4>
                              <p className="text-sm italic opacity-90">
                                {violation.suggested_fix}
                              </p>
                            </div>
                          )}
                          <div className="flex gap-2 text-xs flex-wrap">
                            <span className="px-2 py-1 bg-black/10 rounded capitalize">
                              {violation.section}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer Actions */}
          <div className="mt-8 flex gap-4 justify-center flex-wrap">
            <button 
              onClick={handleExportJSON}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg flex items-center gap-2 transition"
            >
              <Download className="w-5 h-5" />
              Export as JSON
            </button>
            <button
              onClick={() => {
                setStage('upload');
                setFile(null);
                setViolations([]);
                setExtractedData(null);
                setError(null);
              }}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold rounded-lg transition"
            >
              Check Another File
            </button>
          </div>
        </div>
      </div>
    );
  }
}