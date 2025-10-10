import { useState } from 'react';
import { SYSTEM_NAME } from '../constants/index';

function Sidebar({ activeSection, setActiveSection }) {
  const [openSections, setOpenSections] = useState({
    academics: true,
    people: false,
    management: false,
  });

  const toggleSection = (section) => {
    setOpenSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const menuItems = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: '📊',
    },
    {
      id: 'academics',
      name: 'Gestión Académica',
      icon: '🎓',
      children: [
        { id: 'levels', name: 'Niveles Educativos' },
        { id: 'periods', name: 'Períodos Académicos' },
        { id: 'grades', name: 'Grados' },
        { id: 'sections', name: 'Secciones' },
        { id: 'subjects', name: 'Materias' },
        { id: 'attendance', name: 'Asistencia' },
      ],
    },
    {
      id: 'people',
      name: 'Gestión de Personas',
      icon: '👥',
      children: [
        { id: 'persons', name: 'Personas' },
        { id: 'students', name: 'Estudiantes' },
        { id: 'enrollments', name: 'Matrículas' },
      ],
    },
  ];

  return (
    <div className='flex w-64 flex-col bg-indigo-800 text-white'>
      <div className='flex items-center p-4'>
        <span className='text-xl font-bold'>🎯 {SYSTEM_NAME}</span>
      </div>

      <nav className='flex-1 overflow-y-auto pt-2'>
        <ul className='space-y-1 px-2'>
          {menuItems.map((item) => (
            <li key={item.id}>
              {item.children ? (
                <>
                  <button
                    onClick={() => toggleSection(item.id)}
                    className={`flex w-full items-center justify-between rounded-lg p-3 transition hover:bg-indigo-700 ${
                      openSections[item.id] ? 'bg-indigo-700' : ''
                    }`}
                  >
                    <div className='flex items-center'>
                      <span className='mr-3 text-lg'>{item.icon}</span>
                      <span>{item.name}</span>
                    </div>
                    <span
                      className={`transition-transform ${openSections[item.id] ? 'rotate-180 transform' : ''}`}
                    >
                      ▼
                    </span>
                  </button>

                  {openSections[item.id] && (
                    <ul className='mt-1 ml-6 space-y-1'>
                      {item.children.map((child) => (
                        <li key={child.id}>
                          <button
                            onClick={() => setActiveSection(child.id)}
                            className={`w-full rounded-lg p-2 pl-8 text-left transition hover:bg-indigo-700 ${
                              activeSection === child.id ? 'bg-indigo-600' : ''
                            }`}
                          >
                            {child.name}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              ) : (
                <button
                  onClick={() => setActiveSection(item.id)}
                  className={`flex w-full items-center rounded-lg p-3 transition hover:bg-indigo-700 ${
                    activeSection === item.id ? 'bg-indigo-600' : ''
                  }`}
                >
                  <span className='mr-3 text-lg'>{item.icon}</span>
                  <span>{item.name}</span>
                </button>
              )}
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}

export default Sidebar;
