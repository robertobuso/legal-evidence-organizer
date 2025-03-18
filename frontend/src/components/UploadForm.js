import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import { FaFileUpload, FaSpinner } from 'react-icons/fa';
import { uploadChatLog, uploadPdf, fetchEmails } from '../utils/api';

const UploadForm = () => {
  const [uploadingChat, setUploadingChat] = useState(false);
  const [uploadingPdf, setUploadingPdf] = useState(false);
  const [fetchingEmails, setFetchingEmails] = useState(false);
  const [emailAddresses, setEmailAddresses] = useState('');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2025-03-18');
  
  // Handler for chat log file upload
  const onDropChat = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    if (!file.name.endsWith('.txt')) {
      toast.error('Please upload a .txt file for chat logs');
      return;
    }
    
    setUploadingChat(true);
    
    try {
      const response = await uploadChatLog(file);
      toast.success(`Chat log "${file.name}" uploaded successfully! Processing...`);
    } catch (error) {
      console.error('Error uploading chat log:', error);
      toast.error(`Error uploading chat log: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploadingChat(false);
    }
  }, []);
  
  // Handler for PDF file upload
  const onDropPdf = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    if (!file.name.endsWith('.pdf')) {
      toast.error('Please upload a .pdf file for invoices');
      return;
    }
    
    setUploadingPdf(true);
    
    try {
      const response = await uploadPdf(file);
      toast.success(`PDF "${file.name}" uploaded successfully! Processing...`);
    } catch (error) {
      console.error('Error uploading PDF:', error);
      toast.error(`Error uploading PDF: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploadingPdf(false);
    }
  }, []);
  
  // Chat dropzone
  const {
    getRootProps: getChatRootProps,
    getInputProps: getChatInputProps,
    isDragActive: isChatDragActive
  } = useDropzone({
    onDrop: onDropChat,
    accept: {
      'text/plain': ['.txt']
    },
    multiple: false
  });
  
  // PDF dropzone
  const {
    getRootProps: getPdfRootProps,
    getInputProps: getPdfInputProps,
    isDragActive: isPdfDragActive
  } = useDropzone({
    onDrop: onDropPdf,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });
  
  // Handler for fetching emails
  const handleEmailFetch = async (e) => {
    e.preventDefault();
    
    // Validate email addresses
    const emailList = emailAddresses.split(',').map(email => email.trim()).filter(email => email);
    if (emailList.length === 0) {
      toast.error('Please enter at least one email address');
      return;
    }
    
    // Validate dates
    if (!startDate || !endDate) {
      toast.error('Please enter both start and end dates');
      return;
    }
    
    setFetchingEmails(true);
    
    try {
      const response = await fetchEmails(emailList, startDate, endDate);
      toast.success('Email fetch initiated. This may take a few minutes.');
    } catch (error) {
      console.error('Error fetching emails:', error);
      toast.error(`Error fetching emails: ${error.response?.data?.detail || error.message}`);
    } finally {
      setFetchingEmails(false);
    }
  };
  
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Upload Evidence Data</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload your evidence data from various sources to analyze for your legal case.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Chat Log Upload */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900">Upload WhatsApp Chat Log</h2>
          <div 
            {...getChatRootProps()} 
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
              isChatDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input {...getChatInputProps()} />
            <div className="space-y-2">
              <FaFileUpload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="text-sm text-gray-600">
                Drag and drop a WhatsApp chat log (.txt), or click to select
              </p>
              <p className="text-xs text-gray-500">
                Only .txt files are accepted
              </p>
            </div>
          </div>
          {uploadingChat && (
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
              <FaSpinner className="animate-spin" />
              <span>Uploading chat log...</span>
            </div>
          )}
        </div>
        
        {/* PDF Upload */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900">Upload PDF Invoice</h2>
          <div 
            {...getPdfRootProps()} 
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
              isPdfDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input {...getPdfInputProps()} />
            <div className="space-y-2">
              <FaFileUpload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="text-sm text-gray-600">
                Drag and drop a PDF invoice (.pdf), or click to select
              </p>
              <p className="text-xs text-gray-500">
                Only .pdf files are accepted
              </p>
            </div>
          </div>
          {uploadingPdf && (
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
              <FaSpinner className="animate-spin" />
              <span>Uploading PDF...</span>
            </div>
          )}
        </div>
      </div>
      
      {/* Gmail Fetch */}
      <div className="pt-8 border-t border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">Fetch Gmail Emails</h2>
        <p className="mt-1 text-sm text-gray-500">
          Fetch emails from Gmail for specified addresses and date range.
        </p>
        
        <form onSubmit={handleEmailFetch} className="mt-4 space-y-4">
          <div>
            <label htmlFor="email-addresses" className="block text-sm font-medium text-gray-700">
              Email Addresses
            </label>
            <div className="mt-1">
              <input
                type="text"
                id="email-addresses"
                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                placeholder="Enter email addresses, separated by commas"
                value={emailAddresses}
                onChange={(e) => setEmailAddresses(e.target.value)}
                required
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Enter email addresses to fetch from and to, separated by commas.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-700">
                Start Date
              </label>
              <div className="mt-1">
                <input
                  type="date"
                  id="start-date"
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="end-date" className="block text-sm font-medium text-gray-700">
                End Date
              </label>
              <div className="mt-1">
                <input
                  type="date"
                  id="end-date"
                  className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </div>
            </div>
          </div>
          
          <div>
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              disabled={fetchingEmails}
            >
              {fetchingEmails ? (
                <>
                  <FaSpinner className="animate-spin mr-2" />
                  Fetching Emails...
                </>
              ) : (
                'Fetch Emails'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadForm;