import React from 'react';
import Head from 'next/head';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Layout from '../components/Layout';
import TimelineComponent from '../components/Timeline';

export default function TimelinePage() {
  return (
    <>
      <Head>
        <title>Timeline - Legal Evidence Organizer</title>
        <meta name="description" content="Generate and view timelines of events" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <TimelineComponent />
      </Layout>
      
      <ToastContainer position="bottom-right" />
    </>
  );
}