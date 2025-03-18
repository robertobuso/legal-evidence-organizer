import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { format } from 'date-fns';
import { FaSpinner, FaGavel, FaTrash, FaSync, FaInfoCircle } from 'react-icons/fa';
import { getEvidence, analyzeEvidence, deleteEvidence, getEvidenceSource } from '../utils/api';
import { toast } from 'react-toastify';

const EvidenceComponent = () => {
  const router = useRouter();
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeEvidence, setActiveEvidence] = useState(null);
  const [sourceData, setSourceData] = useState(null);
  const [loadingSource, setLoadingSource] = useState(false);

  // Fetch evidence on component mount
  useEffect(() => {
    fetchEvidence();
  }, []);

  // Fetch evidence from API
  const fetchEvidence = async () => {
    setLoading(true);
    try {
      const response = await getEvidence();
      setEvidence(response.data);
    } catch (error) {
      console.error('Error fetching evidence:', error);
      toast.error('Failed to fetch evidence');
    } finally {
      setLoading(false);
    }
  };

  // Handle evidence analysis
  const handleAnalyzeEvidence = async () => {
    setAnalyzing(true);

    try {
      const response = await analyzeEvidence();
      toast.success('Evidence analysis started. This may take several minutes.');
      
      // Refresh evidence list after a short delay
      setTimeout(fetchEvidence, 2000);
    } catch (error) {
      console.error('Error analyzing evidence:', error);
      toast.error('Failed to analyze evidence');
    } finally {
      setAnalyzing(false);
    }
  };

  // Handle evidence deletion
  const handleDeleteEvidence = async (id) => {
    if (window.confirm('Are you sure you want to delete this evidence?')) {
      try {
        await deleteEvidence(id);
        toast.success('Evidence deleted successfully');
        // Update evidence list
        setEvidence(evidence.filter(item => item.id !== id));
        // Close detail view if the deleted item was selected
        if (activeEvidence?.id === id) {
          setActiveEvidence(null);
          setSourceData(null);
        }
      } catch (error) {
        console.error('Error deleting evidence:', error);
        toast.error('Failed to delete evidence');
      }
    }
  };

  // Handle evidence click - show detail view
  const handleEvidenceClick = async (item) => {
    setActiveEvidence(item);
    
    // Fetch source data if needed
    if (item.source_type && item.source_id) {
      setLoadingSource(true);
      try {
        const response = await getEvidenceSource(item.source_type, item.source_id);
        setSourceData(response.data);
      } catch (error) {
        console.error('Error fetching evidence source:', error);
        toast.error('Failed to fetch source data');
        setSourceData(null);
      } finally {
        setLoadingSource(false);
      }
    } else {
      setSourceData(null);
    }
  };

  // Close detail view
  const handleCloseDetail = () => {
    setActiveEvidence(null);
    setSourceData(null);
  };

  // Render source content based on type
  const renderSourceContent = () => {
    if (!sourceData) return null;

    switch (sourceData.source_type) {
      case 'email':
        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">From</h3>
              <p className="mt-1">{sourceData.data.sender}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">To</h3>
              <p className="mt-1">{sourceData.data.recipients}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Subject</h3>
              <p className="mt-1">{sourceData.data.subject || "(No Subject)"}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Date</h3>
              <p className="mt-1">
                {sourceData.data.date
                  ? format(new Date(sourceData.data.date), 'MMM d, yyyy h:mm a')
                  : "Unknown date"}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Body</h3>
              <div className="mt-1 p-3 bg-gray-50 rounded border border-gray-200 text-sm whitespace-pre-wrap">
                {sourceData.data.body}
              </div>
            </div>
          </div>
        );
      
      case 'chat':
        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Sender</h3>
              <p className="mt-1">{sourceData.data.sender}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Date/Time</h3>
              <p className="mt-1">
                {sourceData.data.date_time
                  ? format(new Date(sourceData.data.date_time), 'MMM d, yyyy h:mm a')
                  : "Unknown date"}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Message</h3>
              <div className="mt-1 p-3 bg-gray-50 rounded border border-gray-200 text-sm whitespace-pre-wrap">
                {sourceData.data.message}
              </div>
            </div>
          </div>
        );
      
      case 'pdf':
        return (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">File Name</h3>
              <p className="mt-1">{sourceData.data.file_name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Extracted Text</h3>
              <div className="mt-1 p-3 bg-gray-50 rounded border border-gray-200 text-sm whitespace-pre-wrap max-h-96 overflow-y-auto">
                {sourceData.data.extracted_text}
              </div>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="text-gray-500 italic">
            No source data available for this evidence.
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Evidence</h1>
          <p className="mt-1 text-sm text-gray-500">
            Analyze and recommend evidence for your legal case
          </p>
        </div>
        <button
          onClick={handleAnalyzeEvidence}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          disabled={analyzing}
        >
          {analyzing ? (
            <>
              <FaSpinner className="animate-spin mr-2" />
              Analyzing...
            </>
          ) : (
            <>
              <FaSync className="mr-2" />
              Analyze Evidence
            </>
          )}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Evidence List */}
        <div className={`lg:w-${activeEvidence ? '1/2' : 'full'}`}>
          {loading ? (
            <div className="flex items-center justify-center py-10">
              <FaSpinner className="animate-spin text-primary-500 mr-2" size={20} />
              <span className="text-gray-600">Loading evidence...</span>
            </div>
          ) : evidence.length === 0 ? (
            <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
              <FaGavel className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No evidence recommendations</h3>
              <p className="mt-1 text-sm text-gray-500">
                Click "Analyze Evidence" to generate recommendations.
              </p>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {evidence.map((item) => (
                  <li 
                    key={item.id} 
                    className={`block hover:bg-gray-50 cursor-pointer ${
                      activeEvidence?.id === item.id ? 'bg-primary-50' : ''
                    }`}
                    onClick={() => handleEvidenceClick(item)}
                  >
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-primary-600 truncate">
                          {item.title}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${item.source_type === 'email' ? 'bg-blue-100 text-blue-800' : 
                              item.source_type === 'chat' ? 'bg-green-100 text-green-800' : 
                              'bg-purple-100 text-purple-800'}`}
                          >
                            {item.source_type}
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                          <p className="flex items-center text-sm text-gray-500 truncate">
                            {item.description.length > 100 
                              ? `${item.description.substring(0, 100)}...` 
                              : item.description}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <FaInfoCircle className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                          <p>
                            Created {format(new Date(item.created_at), 'MMM d, yyyy')}
                          </p>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Evidence Detail */}
        {activeEvidence && (
          <div className="lg:w-1/2">
            <div className="bg-white shadow sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6 flex justify-between items-start">
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Evidence Details
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    Detailed information about the selected evidence.
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleDeleteEvidence(activeEvidence.id)}
                    className="inline-flex items-center p-2 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    <FaTrash className="h-4 w-4" />
                  </button>
                  <button
                    onClick={handleCloseDetail}
                    className="inline-flex items-center p-2 border border-gray-300 rounded-full shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
                <dl className="grid grid-cols-1 gap-x-4 gap-y-6">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Title</dt>
                    <dd className="mt-1 text-sm text-gray-900">{activeEvidence.title}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Description</dt>
                    <dd className="mt-1 text-sm text-gray-900">{activeEvidence.description}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Relevance</dt>
                    <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{activeEvidence.relevance}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Source Type</dt>
                    <dd className="mt-1 text-sm text-gray-900">{activeEvidence.source_type}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Created</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {format(new Date(activeEvidence.created_at), 'MMM d, yyyy h:mm a')}
                    </dd>
                  </div>
                  
                  {/* Source Content */}
                  <div className="col-span-1">
                    <dt className="text-sm font-medium text-gray-500 mb-2">Source Content</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {loadingSource ? (
                        <div className="flex items-center justify-center py-10">
                          <FaSpinner className="animate-spin text-primary-500 mr-2" size={20} />
                          <span className="text-gray-600">Loading source content...</span>
                        </div>
                      ) : (
                        renderSourceContent()
                      )}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EvidenceComponent;