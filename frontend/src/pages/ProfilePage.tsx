import React from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { ProfileTab } from '../components/tabs/ProfileTab';

export const ProfilePage: React.FC = () => {
  return (
    <DashboardLayout>
      <ProfileTab />
    </DashboardLayout>
  );
}; 