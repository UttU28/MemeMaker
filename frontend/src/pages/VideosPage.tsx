import React from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { VideosTab } from '../components/tabs/VideosTab';

export const VideosPage: React.FC = () => {
  return (
    <DashboardLayout>
      <VideosTab />
    </DashboardLayout>
  );
}; 