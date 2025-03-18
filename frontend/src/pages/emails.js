import React from 'react';
import Head from 'next/head';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Layout from '../components/Layout';
import EmailList from '../components/EmailList';

export default function EmailsPage() {
  return (
    <>
      <Head>
        <title>Emails - Legal Evidence Organizer</title>
        <meta name="description" content="View and manage email evidence" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <EmailList />
      </Layout>
      
      <ToastContainer position="bottom-right" />
    </>
  );
}