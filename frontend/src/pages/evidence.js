import React from 'react';
import Head from 'next/head';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Layout from '../components/Layout';
import EvidenceComponent from '../components/EvidenceList';

export default function EvidencePage() {
  return (
    <>
      <Head>
        <title>Evidence - Legal Evidence Organizer</title>
        <meta name="description" content="Analyze and recommend evidence" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <EvidenceComponent />
      </Layout>
      
      <ToastContainer position="bottom-right" />
    </>
  );
}