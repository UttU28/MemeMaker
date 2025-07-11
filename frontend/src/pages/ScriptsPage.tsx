import React from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { ScriptsTab } from '../components/tabs/ScriptsTab';

export const ScriptsPage: React.FC = () => {
  return (
    <DashboardLayout>
      <ScriptsTab />
    </DashboardLayout>
  );
}; 