import React from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { FlowTab } from '../components/tabs/FlowTab';

export const FlowPage: React.FC = () => {
  return (
    <DashboardLayout>
      <FlowTab />
    </DashboardLayout>
  );
}; 