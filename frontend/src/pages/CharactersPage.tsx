import React from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { CharactersTab } from '../components/tabs/CharactersTab';

export const CharactersPage: React.FC = () => {
  return (
    <DashboardLayout>
      <CharactersTab />
    </DashboardLayout>
  );
}; 