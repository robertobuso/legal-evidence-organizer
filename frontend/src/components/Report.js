import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { format } from 'date-fns';
import { FaSpinner, FaFileAlt, FaTrash, FaDownload, FaCalendarAlt } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import { getReports, getTimelines, generateReport, deleteReport, getReportById } from '../utils/api';
import { toast } from 'react-toastify';

const ReportComponent = () => {
  const router = useRouter();
  const [reports, setReports] = useState([]);
  const [timelines, setTimelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingTimelines, setLoadingTimelines] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [activeReport, setActiveReport] = useState(null);
  const [reportContent, setReportContent] = useState('');
  const [loadingReport, setLoadingReport] = useState(false);
  const [selectedTimeline, setSelectedTimeline] = useState('');
  const [reportTitle, setReportTitle] = useState('Legal Report: Contract Dispute Analysis');

  // Fetch reports and timelines on component mount
  useEffect(() => {
    fetchReports();
    fetchTimelines();
  }, []);

  // Fetch reports from API
  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await getReports();
      setReports(response.data);
    } catch (error) {
      console.error('Error fetching reports:', error);
      toast.error('Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  };

  // Fetch timelines from API
  const fetchTimelines = async () => {
    setLoadingTimelines(true);
    try {
      const response = await getTimelines();
      setTimelines(response.data);
      // Set first timeline as selected if available
      if (response.data.length > 0 && !selectedTimeline) {
        setSelectedTimeline(response.data[0].id.toString());
      }
    } catch (error) {
      console.error('Error fetching timelines:', error);
      toast.error('Failed to fetch timelines');
    } finally {
      setLoadingTimelines(false);
    }
  };

  // Handle report generation
  const handleGenerateReport = async (e) => {
    e.preventDefault();
    
    if (!selectedTimeline) {
      toast.error('Please select a timeline');
      return;
    }
    
    setGenerating(true);

    try {
      const response = await generateReport(parseInt(selectedTimeline), reportTitle);
      toast.success('Report generation started. This may take a few minutes.');
      
      // Refresh reports list after a short delay
      setTimeout(fetchReports, 2000);
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  // Handle report click - load content
  const handleReportClick = async (report) => {
    setActiveReport(report);
    setLoadingReport(true);
    
    try {
      const response = await getReportById(report.id);
      setReportContent(response.data.content);
    } catch (error) {
      console.error('Error fetching report content:', error);
      toast.error('Failed to fetch report content');
      setReportContent('Error loading report content.');
    } finally {
      setLoadingReport(false);
    }
  };

  // Handle report deletion
  const handleDeleteReport = async (e, id) => {
    e.stopPropagation(); // Prevent clicking through to report detail
    
    if (window.confirm('Are you sure you want to delete this report?')) {
      try {
        await deleteReport(id);
        toast.success('Report deleted successfully');
        // Update reports list
        setReports(reports.filter(report => report.id !== id));
        // Close detail view if the deleted item was selected
        if (activeReport?.id === id) {
          setActiveReport(null);
          setReportContent('');
        }
      } catch (error) {
        console.error('Error deleting report:', error);
        toast.error('Failed to delete report');
      }
    }
  };

  // Download report as markdown
  const handleDownloadReport = () => {
    if (!reportContent) return;
    
    const element = document.createElement('a');
    const file = new Blob([reportContent], {type: 'text/markdown'});
    element.href = URL.createObjectURL(file);
    element.download = `${activeReport.title.replace(/\s+/g, '_')}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Close report detail view
  const handleCloseReport = () => {
    setActiveReport(null);
    setReportContent('');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Reports</h1>
        <p className="mt-1 text-sm text-gray-500">
          Generate and view comprehensive legal reports based on timelines and evidence.
        </p>
      </div>

      {/* Report Generation Form */}
      <div className="bg-white p-6 shadow rounded-lg">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Report</h2>
        
        <form onSubmit={handleGenerateReport} className="space-y-4">
          <div>
            <label htmlFor="report-title" className="block text-sm font-medium text-gray-700">
              Report Title
            </label>
            <input
              type="text"
              id="report-title"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label htmlFor="timeline" className="block text-sm font-medium text-gray-700">
              Select Timeline
            </label>
            <select
              id="timeline"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
              value={selectedTimeline}
              onChange={(e) => setSelectedTimeline(e.target.value)}
              required
            >
              <option value="">Select a timeline</option>
              {loadingTimelines ? (
                <option value="" disabled>Loading timelines...</option>
              ) : timelines.length === 0 ? (
                <option value="" disabled>No timelines available</option>
              ) : (
                timelines.map((timeline) => (
                  <option key={timeline.id} value={timeline.id}>
                    {timeline.title}
                  </option>
                ))
              )}
            </select>
          </div>
          
          <div>
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              disabled={generating || !selectedTimeline}
            >
              {generating ? (
                <>
                  <FaSpinner className="animate-spin mr-2" />
                  Generating Report...
                </>
              ) : (
                <>
                  <FaFileAlt className="mr-2" />
                  Generate Report
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Reports List */}
        <div className={`lg:w-${activeReport ? '1/3' : 'full'}`}>
          <h2 className="text-lg font-medium text-gray-900 mb-4">Your Reports</h2>
          
          {loading ? (
            <div className="flex items-center justify-center py-10">
              <FaSpinner className="animate-spin text-primary-500 mr-2" size={20} />
              <span className="text-gray-600">Loading reports...</span>
            </div>
          ) : reports.length === 0 ? (
            <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
              <FaFileAlt className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No reports yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Generate a report to see it here.
              </p>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {reports.map((report) => (
                  <li 
                    key={report.id} 
                    className={`block hover:bg-gray-50 cursor-pointer ${
                      activeReport?.id === report.id ? 'bg-primary-50' : ''
                    }`}
                    onClick={() => handleReportClick(report)}
                  >
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-primary-600 truncate">
                          {report.title}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <button
                            onClick={(e) => handleDeleteReport(e, report.id)}
                            className="inline-flex items-center p-1 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          >
                            <FaTrash className="h-3 w-3" />
                          </button>
                        </div>
                      </div>
                      <div className="mt-2 flex justify-between">
                        <div className="flex items-center text-sm text-gray-500">
                          <FaCalendarAlt className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                          <p>
                            Created on{' '}
                            {format(new Date(report.created_at), 'MMM d, yyyy')}
                          </p>
                        </div>
                        {report.timeline_id && (
                          <div className="text-xs text-gray-500">
                            Timeline ID: {report.timeline_id}
                          </div>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Report Content */}
        {activeReport && (
          <div className="lg:w-2/3">
            <div className="bg-white shadow sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6 flex justify-between items-start">
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    {activeReport.title}
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    Generated on {format(new Date(activeReport.created_at), 'MMMM d, yyyy')}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={handleDownloadReport}
                    className="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    disabled={loadingReport}
                  >
                    <FaDownload className="h-4 w-4" />
                  </button>
                  <button
                    onClick={handleCloseReport}
                    className="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="border-t border-gray-200">
                {loadingReport ? (
                  <div className="flex items-center justify-center py-10">
                    <FaSpinner className="animate-spin text-primary-500 mr-2" size={20} />
                    <span className="text-gray-600">Loading report content...</span>
                  </div>
                ) : (
                  <div className="px-4 py-5 sm:px-6 prose prose-sm max-w-none">
                    <ReactMarkdown>{reportContent}</ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportComponent;