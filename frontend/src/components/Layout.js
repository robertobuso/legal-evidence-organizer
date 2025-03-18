import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { FaFolder, FaSearch, FaStream, FaGavel, FaFileAlt } from 'react-icons/fa';

const Layout = ({ children }) => {
  const router = useRouter();
  
  // Helper function to check if a path is active
  const isActive = (path) => {
    return router.pathname === path || router.pathname.startsWith(`${path}/`);
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link href="/">
                  <span className="text-xl font-bold text-primary-700">Legal Evidence Organizer</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-6">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Sidebar */}
            <div className="w-full md:w-64 flex-shrink-0">
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-4 py-5 sm:p-6">
                  <nav className="space-y-1">
                    <Link href="/" className={`${isActive('/') ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'} group flex items-center px-3 py-2 text-sm font-medium rounded-md`}>
                      <FaFolder className={`${isActive('/') ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'} flex-shrink-0 -ml-1 mr-3 h-6 w-6`} />
                      <span className="truncate">Upload Data</span>
                    </Link>
                    
                    <Link href="/emails" className={`${isActive('/emails') ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'} group flex items-center px-3 py-2 text-sm font-medium rounded-md`}>
                      <FaFileAlt className={`${isActive('/emails') ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'} flex-shrink-0 -ml-1 mr-3 h-6 w-6`} />
                      <span className="truncate">Email Data</span>
                    </Link>
                    
                    <Link href="/search" className={`${isActive('/search') ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'} group flex items-center px-3 py-2 text-sm font-medium rounded-md`}>
                      <FaSearch className={`${isActive('/search') ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'} flex-shrink-0 -ml-1 mr-3 h-6 w-6`} />
                      <span className="truncate">Search</span>
                    </Link>
                    
                    <Link href="/timeline" className={`${isActive('/timeline') ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'} group flex items-center px-3 py-2 text-sm font-medium rounded-md`}>
                      <FaStream className={`${isActive('/timeline') ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'} flex-shrink-0 -ml-1 mr-3 h-6 w-6`} />
                      <span className="truncate">Timeline</span>
                    </Link>
                    
                    <Link href="/evidence" className={`${isActive('/evidence') ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'} group flex items-center px-3 py-2 text-sm font-medium rounded-md`}>
                      <FaGavel className={`${isActive('/evidence') ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'} flex-shrink-0 -ml-1 mr-3 h-6 w-6`} />
                      <span className="truncate">Evidence</span>
                    </Link>
                    
                    <Link href="/report" className={`${isActive('/report') ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'} group flex items-center px-3 py-2 text-sm font-medium rounded-md`}>
                      <FaFileAlt className={`${isActive('/report') ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'} flex-shrink-0 -ml-1 mr-3 h-6 w-6`} />
                      <span className="truncate">Reports</span>
                    </Link>
                  </nav>
                </div>
              </div>
            </div>
            
            {/* Main content */}
            <div className="flex-1">
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  {children}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <p className="text-center text-sm text-gray-500">
              Legal Evidence Organizer &copy; {new Date().getFullYear()}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;