import React from 'react';
import Head from 'next/head';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Layout from '../components/Layout';
import UploadForm from '../components/UploadForm';

export default function Home() {
  return (
    <>
      <Head>
        <title>Legal Evidence Organizer</title>
        <meta name="description" content="Organize and analyze legal evidence for contract disputes" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <UploadForm />
      </Layout>
      
      <ToastContainer position="bottom-right" />
    </>
  );
}