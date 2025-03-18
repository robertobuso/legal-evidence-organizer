import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { ToastContainer } from 'react-toastify';
import { format } from 'date-fns';
import { FaSpinner, FaSearch, FaEnvelope, FaComment, FaFilePdf } from 'react-icons/fa';
import 'react-toastify/dist/ReactToastify.css';

import Layout from '../components/Layout';
import { searchData } from '../utils/api';

export default function SearchPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [sourceType, setSourceType] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [person, setPerson] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [totalResults, setTotalResults] = useState(0);
  const limit = 20;

  // Handle search form submission
  const handleSearch = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setSearched(true);
    setPage(0);
    
    try {
      const response = await searchData({
        query: searchTerm,
        source_type: sourceType || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        person: person || undefined,
        skip: 0,
        limit,
      });
      
      setResults(response.data);
      setTotalResults(response.data.length);
      setHasMore(response.data.length === limit);
    } catch (error) {
      console.error('Error searching data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load more results
  const loadMore = async () => {
    const nextPage = page + 1;
    setLoading(true);
    
    try {
      const response = await searchData({
        query: searchTerm,
        source_type: sourceType || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        person: person || undefined,
        skip: nextPage * limit,
        limit,
      });
      
      if (response.data.length > 0) {
        setResults([...results, ...response.data]);
        setTotalResults(prevTotal => prevTotal + response.data.length);
        setPage(nextPage);
        setHasMore(response.data.length === limit);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error loading more results:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle result item click
  const handleResultClick = (result) => {
    const { type, id } = result;
    
    if (type === 'email') {
      router.push(`/emails/${id}`);
    } else if (type === 'chat') {
      // For now, just show the search page with filtered results
      setSearchTerm('');
      setSourceType('chat');
      setPerson(result.source.split(':')[1]?.trim() || '');
      handleSearch();
    } else if (type === 'pdf') {
      // For now, just show the search page with filtered results
      setSearchTerm('');
      setSourceType('pdf');
      handleSearch();
    }
  };

  // Render icon based on result type
  const renderIcon = (type) => {
    switch (type) {
      case 'email':
        return <FaEnvelope className="h-5 w-5 text-blue-500" />;
      case 'chat':
        return <FaComment className="h-5 w-5 text-green-500" />;
      case 'pdf':
        return <FaFilePdf className="h-5 w-5 text-red-500" />;
      default:
        return <FaSearch className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <>
      <Head>
        <title>Search - Legal Evidence Organizer</title>
        <meta name="description" content="Search across all evidence data" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Search Evidence</h1>
            <p className="mt-1 text-sm text-gray-500">
              Search across emails, chat logs, and PDFs for specific information.
            </p>
          </div>
          
          {/* Search Form */}
          <div className="bg-white p-6 shadow rounded-lg">
            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label htmlFor="search-term" className="block text-sm font-medium text-gray-700">
                  Search Term
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <FaSearch className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    id="search-term"
                    className="focus:ring-primary-500 focus:border-primary-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
                    placeholder="Enter search terms..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label htmlFor="source-type" className="block text-sm font-medium text-gray-700">
                    Source Type
                  </label>
                  <select
                    id="source-type"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                  >
                    <option value="">All Sources</option>
                    <option value="email">Emails</option>
                    <option value="chat">Chat Logs</option>
                    <option value="pdf">PDFs</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="person" className="block text-sm font-medium text-gray-700">
                    Person
                  </label>
                  <input
                    type="text"
                    id="person"
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    placeholder="Name or email..."
                    value={person}
                    onChange={(e) => setPerson(e.target.value)}
                  />
                </div>
                
                <div>
                  <label htmlFor="start-date" className="block text-sm font-medium text-gray-700">
                    Start Date
                  </label>
                  <input
                    type="date"
                    id="start-date"
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                
                <div>
                  <label htmlFor="end-date" className="block text-sm font-medium text-gray-700">
                    End Date
                  </label>
                  <input
                    type="date"
                    id="end-date"
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>
              
              <div>
                <button
                  type="submit"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <FaSpinner className="animate-spin mr-2" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <FaSearch className="mr-2" />
                      Search
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
          
          {/* Search Results */}
          {searched && (
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                {loading && page === 0 ? 'Searching...' : `Search Results (${totalResults})`}
              </h2>
              
              {loading && page === 0 ? (
                <div className="flex items-center justify-center py-10">
                  <FaSpinner className="animate-spin text-primary-500 mr-2" size={20} />
                  <span className="text-gray-600">Searching...</span>
                </div>
              ) : results.length === 0 ? (
                <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
                  <FaSearch className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Try adjusting your search terms or filters.
                  </p>
                </div>
              ) : (
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200">
                    {results.map((result) => (
                      <li 
                        key={`${result.type}-${result.id}`} 
                        className="block hover:bg-gray-50 cursor-pointer"
                        onClick={() => handleResultClick(result)}
                      >
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
                                {renderIcon(result.type)}
                              </div>
                            </div>
                            <div className="ml-4 flex-1">
                              <div className="flex items-center justify-between">
                                <p className="text-sm font-medium text-primary-600 truncate">
                                  {result.title}
                                </p>
                                <div className="ml-2 flex-shrink-0 flex">
                                  <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                    ${result.type === 'email' ? 'bg-blue-100 text-blue-800' : 
                                      result.type === 'chat' ? 'bg-green-100 text-green-800' : 
                                      'bg-purple-100 text-purple-800'}`}
                                  >
                                    {result.type}
                                  </p>
                                </div>
                              </div>
                              <div className="mt-2 flex justify-between">
                                <p className="text-sm text-gray-600 truncate">
                                  {result.snippet}
                                </p>
                                {result.date && (
                                  <p className="text-sm text-gray-500">
                                    {format(new Date(result.date), 'MMM d, yyyy')}
                                  </p>
                                )}
                              </div>
                              <div className="mt-1">
                                <p className="text-xs text-gray-500">
                                  {result.source}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                  
                  {/* Load More Button */}
                  {hasMore && (
                    <div className="px-4 py-4 sm:px-6 border-t border-gray-200 flex justify-center">
                      <button
                        onClick={loadMore}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <FaSpinner className="animate-spin mr-2" />
                            Loading...
                          </>
                        ) : (
                          'Load More Results'
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </Layout>
      
      <ToastContainer position="bottom-right" />
    </>
  );
}