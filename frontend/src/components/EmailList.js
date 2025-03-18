import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { FaSpinner, FaFilter, FaTimes, FaEnvelope } from 'react-icons/fa';
import { format } from 'date-fns';
import { getEmails, getEmailStatus } from '../utils/api';

const EmailList = () => {
  const router = useRouter();
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    sender: '',
    recipient: '',
    subject: '',
    startDate: '',
    endDate: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [totalEmails, setTotalEmails] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  // Fetch emails on component mount and when filters change
  useEffect(() => {
    const fetchEmails = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Get email fetch status
        const statusResponse = await getEmailStatus();
        setTotalEmails(statusResponse.data.total_emails);
        
        // If no emails fetched yet, show message and return
        if (statusResponse.data.total_emails === 0) {
          setLoading(false);
          setHasMore(false);
          return;
        }
        
        // Get emails with filters
        const skip = (page - 1) * limit;
        const response = await getEmails({
          skip,
          limit,
          sender: filters.sender,
          recipient: filters.recipient,
          subject: filters.subject,
          start_date: filters.startDate,
          end_date: filters.endDate,
        });
        
        if (page === 1) {
          setEmails(response.data);
        } else {
          setEmails((prevEmails) => [...prevEmails, ...response.data]);
        }
        
        setHasMore(response.data.length === limit);
      } catch (err) {
        console.error('Error fetching emails:', err);
        setError('Error fetching emails. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchEmails();
  }, [page, filters]);

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
    }));
    setPage(1); // Reset to first page when filters change
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      sender: '',
      recipient: '',
      subject: '',
      startDate: '',
      endDate: '',
    });
    setPage(1);
  };

  // Handle email click
  const handleEmailClick = (emailId) => {
    router.push(`/emails/${emailId}`);
  };

  // Load more emails
  const loadMoreEmails = () => {
    setPage((prevPage) => prevPage + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Email Data</h1>
          <p className="mt-1 text-sm text-gray-500">
            {totalEmails} emails fetched from Gmail
          </p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <FaFilter className="mr-2" />
          {showFilters ? 'Hide Filters' : 'Show Filters'}
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label htmlFor="sender" className="block text-sm font-medium text-gray-700">
                Sender
              </label>
              <input
                type="text"
                id="sender"
                name="sender"
                value={filters.sender}
                onChange={handleFilterChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="Filter by sender"
              />
            </div>
            <div>
              <label htmlFor="recipient" className="block text-sm font-medium text-gray-700">
                Recipient
              </label>
              <input
                type="text"
                id="recipient"
                name="recipient"
                value={filters.recipient}
                onChange={handleFilterChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="Filter by recipient"
              />
            </div>
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
                Subject
              </label>
              <input
                type="text"
                id="subject"
                name="subject"
                value={filters.subject}
                onChange={handleFilterChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="Filter by subject"
              />
            </div>
            <div>
              <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">
                Start Date
              </label>
              <input
                type="date"
                id="startDate"
                name="startDate"
                value={filters.startDate}
                onChange={handleFilterChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">
                End Date
              </label>
              <input
                type="date"
                id="endDate"
                name="endDate"
                value={filters.endDate}
                onChange={handleFilterChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={clearFilters}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <FaTimes className="mr-2" />
              Clear Filters
            </button>
          </div>
        </div>
      )}

      {/* Email List */}
      {loading && page === 1 ? (
        <div className="flex items-center justify-center py-10">
          <FaSpinner className="animate-spin text-primary-500 mr-2" size={20} />
          <span className="text-gray-600">Loading emails...</span>
        </div>
      ) : error ? (
        <div className="bg-red-50 p-4 rounded-md">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      ) : emails.length === 0 ? (
        <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
          <FaEnvelope className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No emails found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {totalEmails === 0
              ? "No emails have been fetched yet. Go to the Upload Data page to fetch emails."
              : "No emails match your current filters."}
          </p>
        </div>
      ) : (
        <div className="overflow-hidden bg-white shadow rounded-md">
          <ul className="divide-y divide-gray-200">
            {emails.map((email) => (
              <li
                key={email.id}
                className="px-6 py-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => handleEmailClick(email.id)}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                      <FaEnvelope className="h-5 w-5 text-primary-600" />
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">{email.subject || "(No Subject)"}</p>
                    <p className="text-sm text-gray-500 truncate">From: {email.sender}</p>
                    <p className="text-sm text-gray-500 truncate">{email.snippet}</p>
                  </div>
                  <div className="flex-shrink-0 whitespace-nowrap text-sm text-gray-500">
                    {email.date ? format(new Date(email.date), 'MMM d, yyyy') : "Unknown date"}
                  </div>
                </div>
              </li>
            ))}
          </ul>
          
          {/* Load More Button */}
          {hasMore && (
            <div className="px-6 py-4 border-t border-gray-200 flex justify-center">
              <button
                onClick={loadMoreEmails}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin mr-2" />
                    Loading...
                  </>
                ) : (
                  'Load More'
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmailList;