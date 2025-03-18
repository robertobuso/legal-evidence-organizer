import React from 'react';
import Head from 'next/head';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Layout from '../components/Layout';
import ReportComponent from '../components/ReportComponent';

export default function ReportPage() {
  return (
    <>
      <Head>
        <title>Reports - Legal Evidence Organizer</title>
        <meta name="description" content="Generate and view comprehensive legal reports" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <ReportComponent />
      </Layout>
      
      <ToastContainer position="bottom-right" />
    </>
  );
}