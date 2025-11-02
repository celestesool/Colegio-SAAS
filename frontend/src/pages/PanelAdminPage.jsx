// pages/PanelAdminPage.js
import { useState } from 'react';
import Sidebar from '../components/SideBar';
import { SYSTEM_NAME } from '../constants/index';
import { useNavigate } from 'react-router-dom';
import {
  DashboardContent,
  LevelsContent,
  PeriodsContent,
  GradesContent,
  SectionsContent,
  SubjectsContent,
  PersonsContent,
  StudentsContent,
  EnrollmentsContent,
  AttendanceContent,
  TeachersContent,
  // ReportsContent,
} from './content';
import { Document } from './Document';
import { Asistencia } from './Jhonatan/Asistencia';

export default function PanelAdminPage() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const navigate = useNavigate();

  const handleLogOut = () => {
    fetch('api/auth/logout/', { method: 'POST', credentials: 'include' })
      .then((response) => {
        if (response.ok) {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          navigate('/login');
        } else {
          alert('Error al cerrar sesión');
        }
      })
      .catch((error) => {
        console.error('Error al cerrar sesión:', error);
      });
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardContent />;
      case 'levels':
        return <LevelsContent />;
      case 'periods':
        return <PeriodsContent />;
      case 'grades':
        return <GradesContent />;
      case 'sections':
        return <SectionsContent />;
      case 'subjects':
        return <SubjectsContent />;
      case 'persons':
        return <PersonsContent />;
      case 'students':
        return <StudentsContent />;
      case 'teachers': 
        return <TeachersContent />;
      case 'scores': 
        return <ScoresContent />;
      case 'Document':
        return <Document />;
      case 'Asistencia':
        return <Asistencia />;
      case 'enrollments':
        return <EnrollmentsContent />;
      // case 'reports':
      //   return <ReportsContent />;
      case 'attendance':
        return <AttendanceContent />; // asistencia
      default:
        return <DashboardContent />;
    }
  };

  return (
    <div className='flex h-screen bg-gray-100'>
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />
      <div className='flex flex-1 flex-col overflow-hidden'>
        <header className='bg-white shadow-sm'>
          <div className='flex items-center justify-between px-6 py-4'>
            <h1 className='text-2xl font-semibold text-gray-900'>
              Panel de Administración - {SYSTEM_NAME}
            </h1>
            <div className='flex items-center'>
              <span className='mr-4 text-gray-700'>Bienvenido, Admin</span>
              <button
                onClick={handleLogOut}
                className='rounded-lg bg-indigo-600 px-4 py-2 text-white transition hover:bg-indigo-700'
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </header>
        <main className='flex-1 overflow-y-auto p-6'>{renderContent()}</main>
      </div>
    </div>
  );
}
