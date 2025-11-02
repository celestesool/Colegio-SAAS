
import { useState, useEffect } from 'react';
import DataTable from '../../components/DataTable';
import Modal from '../../components/Modal';

export default function TeachersContent() {
  const [teachers, setTeachers] = useState([]);
  const [persons, setPersons] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [grades, setGrades] = useState([]);
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState(null);
  const [formData, setFormData] = useState({
    person: '',
    subjects: [],
    grades: [],
    sections: [],
    is_active: true,
  });

  const columns = [
    {
      key: 'person_name',
      title: 'Docente',
      render: (item) => `${item.person_first_name} ${item.person_last_name}`,
    },
    {
      key: 'subjects',
      title: 'Materias',
      render: (item) => item.subjects_names?.join(', ') || 'N/A',
    },
    {
      key: 'grades_sections',
      title: 'Grados/Secciones',
      render: (item) => item.grades_sections_names?.join(', ') || 'N/A',
    },
    {
      key: 'is_active',
      title: 'Estado',
      render: (item) => (
        <span
          className={`rounded-full px-2 py-1 text-xs ${
            item.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}
        >
          {item.is_active ? 'Activo' : 'Inactivo'}
        </span>
      ),
    },
    {
      key: 'actions',
      title: 'Acciones',
      render: (item) => (
        <div className='flex space-x-2'>
          <button
            onClick={() => handleEdit(item)}
            className='text-indigo-600 hover:text-indigo-900'
          >
            Editar
          </button>
          <button onClick={() => handleDelete(item.id)} className='text-red-600 hover:text-red-900'>
            Eliminar
          </button>
        </div>
      ),
    },
  ];

  // Funciones para cargar datos dependientes
  const fetchPersons = async () => {
    try {
      const response = await fetch(`api/persons`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      if (!response.ok) throw new Error('Error al cargar personas');
      const data = await response.json();
      setPersons(data);
    } catch (err) {
      console.error('Error loading persons:', err);
    }
  };

  const fetchSubjects = async () => {
    try {
      const response = await fetch(`api/subjects`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      if (!response.ok) throw new Error('Error al cargar materias');
      const data = await response.json();
      setSubjects(data);
    } catch (err) {
      console.error('Error loading subjects:', err);
    }
  };

  const fetchGrades = async () => {
    try {
      const response = await fetch(`api/grades`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      if (!response.ok) throw new Error('Error al cargar grados');
      const data = await response.json();
      setGrades(data);
    } catch (err) {
      console.error('Error loading grades:', err);
    }
  };

  const fetchSections = async () => {
    try {
      const response = await fetch(`api/sections`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      if (!response.ok) throw new Error('Error al cargar secciones');
      const data = await response.json();
      setSections(data);
    } catch (err) {
      console.error('Error loading sections:', err);
    }
  };

  const fetchTeachers = async () => {
    try {
      setLoading(true);
      const response = await fetch(`api/teachers`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (!response.ok) throw new Error('Error al cargar docentes');

      const data = await response.json();

      // Enriquecer datos con nombres
      const teachersWithNames = data.map((teacher) => ({
        ...teacher,
        person_first_name: persons.find(p => p.id === teacher.person)?.first_name || 'N/A',
        person_last_name: persons.find(p => p.id === teacher.person)?.last_name || 'N/A',
        subjects_names: teacher.subjects?.map(subId => 
          subjects.find(s => s.id === subId)?.name || 'N/A'
        ) || [],
        grades_sections_names: teacher.grades?.map(gradeId => {
          const grade = grades.find(g => g.id === gradeId);
          const sectionNames = teacher.sections
            ?.filter(secId => sections.find(s => s.id === secId)?.grade === gradeId)
            .map(secId => sections.find(s => s.id === secId)?.name)
            .join(', ');
          return sectionNames ? `${grade?.name} (${sectionNames})` : grade?.name;
        }) || [],
      }));

      setTeachers(teachersWithNames);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingTeacher ? `api/teachers/${editingTeacher.id}` : `api/teachers`;
      const method = editingTeacher ? 'PUT' : 'POST';

      const submitData = {
        ...formData,
        person: parseInt(formData.person),
        subjects: formData.subjects.map(id => parseInt(id)),
        grades: formData.grades.map(id => parseInt(id)),
        sections: formData.sections.map(id => parseInt(id)),
      };

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify(submitData),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al guardar docente');
      }

      await fetchTeachers();
      setShowModal(false);
      resetForm();
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Está seguro de eliminar este docente?')) return;

    try {
      const response = await fetch(`api/teachers/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Error al eliminar docente');

      await fetchTeachers();
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (teacher) => {
    setEditingTeacher(teacher);
    setFormData({
      person: teacher.person.toString(),
      subjects: teacher.subjects?.map(id => id.toString()) || [],
      grades: teacher.grades?.map(id => id.toString()) || [],
      sections: teacher.sections?.map(id => id.toString()) || [],
      is_active: teacher.is_active,
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      person: '',
      subjects: [],
      grades: [],
      sections: [],
      is_active: true,
    });
    setEditingTeacher(null);
  };

  const handleNew = () => {
    resetForm();
    setShowModal(true);
  };

  // Cargar datos iniciales
  useEffect(() => {
    const loadInitialData = async () => {
      await Promise.all([
        fetchPersons(),
        fetchSubjects(),
        fetchGrades(),
        fetchSections()
      ]);
    };
    loadInitialData();
  }, []);

  // Cuando se carguen los datos dependientes, cargar teachers
  useEffect(() => {
    if (persons.length > 0 && subjects.length > 0 && grades.length > 0 && sections.length > 0) {
      fetchTeachers();
    }
  }, [persons, subjects, grades, sections]);

  if (loading) return <div className='py-8 text-center'>Cargando docentes...</div>;
  if (error) return <div className='py-8 text-center text-red-600'>Error: {error}</div>;

  return (
    <div>
      <div className='mb-6 flex items-center justify-between'>
        <h2 className='text-2xl font-semibold'>Gestión de Docentes</h2>
        <button
          onClick={handleNew}
          className='rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700'
          disabled={persons.length === 0}
        >
          + Nuevo Docente
        </button>
      </div>

      {persons.length === 0 && (
        <div className='mb-4 rounded-lg bg-yellow-100 p-4 text-yellow-700'>
          Primero debe crear personas en el módulo de Gestión de Personas.
        </div>
      )}

      {error && <div className='mb-4 rounded-lg bg-red-100 p-4 text-red-700'>{error}</div>}

      <DataTable columns={columns} data={teachers} />

      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          resetForm();
        }}
        title={editingTeacher ? 'Editar Docente' : 'Nuevo Docente'}
      >
        <form onSubmit={handleSubmit} className='space-y-4'>
          <div>
            <label className='block text-sm font-medium text-gray-700'>Persona *</label>
            <select
              required
              value={formData.person}
              onChange={(e) => setFormData({ ...formData, person: e.target.value })}
              className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
            >
              <option value=''>Seleccione una persona</option>
              {persons.map((person) => (
                <option key={person.id} value={person.id}>
                  {person.first_name} {person.last_name} - {person.doc_number}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700'>Materias Asignadas</label>
            <select
              multiple
              value={formData.subjects}
              onChange={(e) => setFormData({ 
                ...formData, 
                subjects: Array.from(e.target.selectedOptions, option => option.value)
              })}
              className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              size={4}
            >
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.name} ({subject.short_name})
                </option>
              ))}
            </select>
            <p className='mt-1 text-sm text-gray-500'>
              Mantén Ctrl/Cmd para seleccionar múltiples materias
            </p>
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700'>Grados Asignados</label>
            <select
              multiple
              value={formData.grades}
              onChange={(e) => setFormData({ 
                ...formData, 
                grades: Array.from(e.target.selectedOptions, option => option.value)
              })}
              className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              size={4}
            >
              {grades.map((grade) => (
                <option key={grade.id} value={grade.id}>
                  {grade.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700'>Secciones Asignadas</label>
            <select
              multiple
              value={formData.sections}
              onChange={(e) => setFormData({ 
                ...formData, 
                sections: Array.from(e.target.selectedOptions, option => option.value)
              })}
              className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              size={4}
            >
              {sections.map((section) => (
                <option key={section.id} value={section.id}>
                  {section.name} - {grades.find(g => g.id === section.grade)?.name || 'N/A'}
                </option>
              ))}
            </select>
          </div>

          <div className='flex items-center'>
            <input
              type='checkbox'
              id='is_active'
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className='mr-2'
            />
            <label htmlFor='is_active' className='text-sm font-medium text-gray-700'>
              Docente activo
            </label>
          </div>

          <div className='flex justify-end space-x-3 pt-4'>
            <button
              type='button'
              onClick={() => {
                setShowModal(false);
                resetForm();
              }}
              className='rounded-lg bg-gray-300 px-4 py-2 hover:bg-gray-400'
            >
              Cancelar
            </button>
            <button
              type='submit'
              className='rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700'
            >
              {editingTeacher ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}