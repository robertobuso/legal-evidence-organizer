import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { format } from 'date-fns';
import { FaSpinner, FaCalendarAlt, FaTrash, FaFileAlt } from 'react-icons/fa';
import { getTimelines, generateTimeline, deleteTimeline } from '../utils/api';
import { toast } from 'react-toastify';

const TimelineComponent = () => {
  const router = useRouter();
  const [timelines, setTimelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [title, setTitle] = useState('Timeline of Contract Dispute');

  // Fetch timelines on component mount
  useEffect(() => {
    fetchTimelines();
  }, []);

  // Fetch timelines from API
  const fetchTimelines = async () => {
    setLoading(true);
    try {
      const response = await getTimelines();
      setTimelines(response.data);
    } catch (error) {
      console.error('Error fetching timelines:', error);
      toast.error('Failed to fetch timelines');
    } finally {
      setLoading(false);
    }
  };

  // Handle timeline generation
  const handleGenerateTimeline = async (e) => {
    e.preventDefault();
    setGenerating(true);

    try {
      const response = await generateTimeline({
        start_date: startDate,
        end_date: endDate,
        title: title,
      });

      toast.success('Timeline generation started. This may take a few minutes.');
      
      // Refresh timelines list after a short delay
      setTimeout(fetchTimelines, 2000);
    } catch (error) {
      console.error('Error generating timeline:', error);
      toast.error('Failed to generate timeline');
    } finally {
      setGenerating(false);
    }
  };

  // Handle timeline click - navigate to detail view
  const handleTimelineClick = (id) => {
    router.push(`/timeline/${id}`);
  };

  // Handle timeline deletion
  const handleDeleteTimeline = async (e, id) => {
    e.stopPropagation(); // Prevent clicking through to timeline detail
    
    if (window.confirm('Are you sure you want to delete this timeline?')) {
      try {
        await deleteTimeline(id);
        toast.success('Timeline deleted successfully');
        // Update timelines list
        setTimelines(timelines.filter(timeline => timeline.id !== id));
      } catch (error) {
        console.error('Error deleting timeline:', error);
        toast.error('Failed to delete timeline');
      }
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Timelines</h1>
        <p className="mt-1 text-sm text-gray-500">
          Generate and view timelines of events related to the contract dispute.
        </p>
      </div>

      {/* Timeline Generation Form */}
      <div className="bg-white p-6 shadow rounded-lg">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Timeline</h2>
        
        <form onSubmit={handleGenerateTimeline} className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Timeline Title
            </label>
            <input
              type="text"
              id="title"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-700">
                Start Date (Optional)
              </label>
              <input
                type="date"
                id="start-date"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            
            <div>
              <label htmlFor="end-date" className="block text-sm font-medium text-gray-700">
                End Date (Optional)
              </label>
              <input
                type="date"
                id="end-date"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
          
          <div>
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              disabled={generating}
            >
              {generating ? (
                <>
                  <FaSpinner className="animate-spin mr-2" />
                  Generating Timeline...
                </>
              ) : (
                <>
                  <FaCalendarAlt className="mr-2" />
                  Generate Timeline
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Timelines List */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Your Timelines</h2>
        
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <FaSpinner className="animate-spin text-primary-500 mr-2" size={20} />
            <span className="text-gray-600">Loading timelines...</span>
          </div>
        ) : timelines.length === 0 ? (
          <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
            <FaCalendarAlt className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No timelines yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Generate a timeline to see it here.
            </p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {timelines.map((timeline) => (
                <li key={timeline.id} className="block hover:bg-gray-50">
                  <div
                    className="px-4 py-4 flex items-center sm:px-6 cursor-pointer"
                    onClick={() => handleTimelineClick(timeline.id)}
                  >
                    <div className="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between">
                      <div>
                        <div className="flex text-sm">
                          <p className="font-medium text-primary-600 truncate">{timeline.title}</p>
                        </div>
                        <div className="mt-2 flex">
                          <div className="flex items-center text-sm text-gray-500">
                            <FaCalendarAlt className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                            <p>
                              Created on{' '}
                              {timeline.created_at
                                ? format(new Date(timeline.created_at), 'MMM d, yyyy')
                                : 'Unknown date'}
                            </p>
                          </div>
                        </div>
                        <p className="mt-2 text-sm text-gray-500 line-clamp-2">
                          {timeline.description || 'No description available'}
                        </p>
                      </div>
                    </div>
                    <div className="ml-5 flex-shrink-0">
                      <button
                        onClick={(e) => handleDeleteTimeline(e, timeline.id)}
                        className="inline-flex items-center p-2 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      >
                        <FaTrash className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default TimelineComponent;