import { useState, useEffect } from 'react';
import DataTable from '../../components/DataTable';
import Modal from '../../components/Modal';

export default function ScoresContent() {
  const [scores, setScores] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [periods, setPeriods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingScore, setEditingScore] = useState(null);
  const [formData, setFormData] = useState({
    teacher: '',
    subject: '',
    student: '',
    period: '',
    trimester: '1',
    dimension_ser: '',
    dimension_saber: '',
    dimension_hacer: '',
    dimension_decidir: '',
    final_score: '',
    observations: '',
  });

  const columns = [
    {
      key: 'student_name',
      title: 'Estudiante',
      render: (item) => item.student_name || 'N/A',
    },
    {
      key: 'subject_name',
      title: 'Materia',
      render: (item) => item.subject_name || 'N/A',
    },
    {
      key: 'teacher_name',
      title: 'Docente',
      render: (item) => item.teacher_name || 'N/A',
    },
    {
      key: 'period_name',
      title: 'Período',
      render: (item) => item.period_name || 'N/A',
    },
    {
      key: 'trimester',
      title: 'Trimestre',
      render: (item) => `Trimestre ${item.trimester}`,
    },
    {
      key: 'final_score',
      title: 'Nota Final',
      render: (item) => (
        <span className={`font-bold ${
          item.final_score >= 7 ? 'text-green-600' : 
          item.final_score >= 5 ? 'text-yellow-600' : 'text-red-600'
        }`}>
          {item.final_score || 'N/A'}
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
  const fetchTeachers = async () => {
    try {
      const response = await fetch(`api/teachers`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      if (!response.ok) throw new Error('Error al cargar docentes');
      const data = await response.json();
      setTeachers(data);
    } catch (err) {
      console.error('Error loading teachers:', err);
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

  const fetchStudents = async () => {
    try {
      const response = await fetch(`api/students`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      if (!response.ok) throw new Error('Error al cargar estudiantes');
      const data = await response.json();
      setStudents(data);
    } catch (err) {
      console.error('Error loading students:', err);
    }
  };

  const fetchPeriods = async () => {
    try {
      const response = await fetch(`api/periods`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      if (!response.ok) throw new Error('Error al cargar períodos');
      const data = await response.json();
      setPeriods(data);
    } catch (err) {
      console.error('Error loading periods:', err);
    }
  };

  const fetchScores = async () => {
    try {
      setLoading(true);
      const response = await fetch(`api/scores`, {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (!response.ok) throw new Error('Error al cargar calificaciones');

      const data = await response.json();

      // Enriquecer datos con nombres
      const scoresWithNames = data.map((score) => ({
        ...score,
        student_name: students.find(s => s.id === score.student)?.person_name || 'N/A',
        subject_name: subjects.find(s => s.id === score.subject)?.name || 'N/A',
        teacher_name: teachers.find(t => t.id === score.teacher)?.person_name || 'N/A',
        period_name: periods.find(p => p.id === score.period)?.name || 'N/A',
      }));

      setScores(scoresWithNames);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingScore ? `api/scores/${editingScore.id}` : `api/scores`;
      const method = editingScore ? 'PUT' : 'POST';

      // Calcular nota final automáticamente
      const finalScore = calculateFinalScore();

      const submitData = {
        ...formData,
        teacher: parseInt(formData.teacher),
        subject: parseInt(formData.subject),
        student: parseInt(formData.student),
        period: parseInt(formData.period),
        trimester: parseInt(formData.trimester),
        dimension_ser: parseFloat(formData.dimension_ser) || 0,
        dimension_saber: parseFloat(formData.dimension_saber) || 0,
        dimension_hacer: parseFloat(formData.dimension_hacer) || 0,
        dimension_decidir: parseFloat(formData.dimension_decidir) || 0,
        final_score: finalScore,
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
        throw new Error(errorData.detail || 'Error al guardar calificación');
      }

      await fetchScores();
      setShowModal(false);
      resetForm();
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  const calculateFinalScore = () => {
    const ser = parseFloat(formData.dimension_ser) || 0;
    const saber = parseFloat(formData.dimension_saber) || 0;
    const hacer = parseFloat(formData.dimension_hacer) || 0;
    const decidir = parseFloat(formData.dimension_decidir) || 0;
    
    // Promedio simple de las 4 dimensiones
    return ((ser + saber + hacer + decidir) / 4).toFixed(2);
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Está seguro de eliminar esta calificación?')) return;

    try {
      const response = await fetch(`api/scores/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Error al eliminar calificación');

      await fetchScores();
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (score) => {
    setEditingScore(score);
    setFormData({
      teacher: score.teacher.toString(),
      subject: score.subject.toString(),
      student: score.student.toString(),
      period: score.period.toString(),
      trimester: score.trimester.toString(),
      dimension_ser: score.dimension_ser?.toString() || '',
      dimension_saber: score.dimension_saber?.toString() || '',
      dimension_hacer: score.dimension_hacer?.toString() || '',
      dimension_decidir: score.dimension_decidir?.toString() || '',
      final_score: score.final_score?.toString() || '',
      observations: score.observations || '',
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      teacher: '',
      subject: '',
      student: '',
      period: '',
      trimester: '1',
      dimension_ser: '',
      dimension_saber: '',
      dimension_hacer: '',
      dimension_decidir: '',
      final_score: '',
      observations: '',
    });
    setEditingScore(null);
  };

  const handleNew = () => {
    resetForm();
    setShowModal(true);
  };

  // Calcular nota final cuando cambien las dimensiones
  useEffect(() => {
    const finalScore = calculateFinalScore();
    setFormData(prev => ({ ...prev, final_score: finalScore }));
  }, [formData.dimension_ser, formData.dimension_saber, formData.dimension_hacer, formData.dimension_decidir]);

  // Cargar datos iniciales
  useEffect(() => {
    const loadInitialData = async () => {
      await Promise.all([
        fetchTeachers(),
        fetchSubjects(),
        fetchStudents(),
        fetchPeriods()
      ]);
    };
    loadInitialData();
  }, []);

  // Cuando se carguen los datos dependientes, cargar scores
  useEffect(() => {
    if (teachers.length > 0 && subjects.length > 0 && students.length > 0 && periods.length > 0) {
      fetchScores();
    }
  }, [teachers, subjects, students, periods]);

  if (loading) return <div className='py-8 text-center'>Cargando calificaciones...</div>;
  if (error) return <div className='py-8 text-center text-red-600'>Error: {error}</div>;

  return (
    <div>
      <div className='mb-6 flex items-center justify-between'>
        <h2 className='text-2xl font-semibold'>Registro de Calificaciones</h2>
        <button
          onClick={handleNew}
          className='rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700'
          disabled={teachers.length === 0 || students.length === 0}
        >
          + Nueva Calificación
        </button>
      </div>

      {(teachers.length === 0 || students.length === 0) && (
        <div className='mb-4 rounded-lg bg-yellow-100 p-4 text-yellow-700'>
          {teachers.length === 0 && 'Primero debe crear docentes en el módulo de Gestión de Docentes. '}
          {students.length === 0 && 'Primero debe crear estudiantes en el módulo de Gestión de Estudiantes.'}
        </div>
      )}

      {error && <div className='mb-4 rounded-lg bg-red-100 p-4 text-red-700'>{error}</div>}

      <DataTable columns={columns} data={scores} />

      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          resetForm();
        }}
        title={editingScore ? 'Editar Calificación' : 'Nueva Calificación'}
        size="lg"
      >
        <form onSubmit={handleSubmit} className='space-y-4'>
          <div className='grid grid-cols-2 gap-4'>
            <div>
              <label className='block text-sm font-medium text-gray-700'>Docente *</label>
              <select
                required
                value={formData.teacher}
                onChange={(e) => setFormData({ ...formData, teacher: e.target.value })}
                className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              >
                <option value=''>Seleccione un docente</option>
                {teachers.map((teacher) => (
                  <option key={teacher.id} value={teacher.id}>
                    {teacher.person_first_name} {teacher.person_last_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className='block text-sm font-medium text-gray-700'>Materia *</label>
              <select
                required
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              >
                <option value=''>Seleccione una materia</option>
                {subjects.map((subject) => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className='grid grid-cols-2 gap-4'>
            <div>
              <label className='block text-sm font-medium text-gray-700'>Estudiante *</label>
              <select
                required
                value={formData.student}
                onChange={(e) => setFormData({ ...formData, student: e.target.value })}
                className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              >
                <option value=''>Seleccione un estudiante</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.person_name} - {student.code}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className='block text-sm font-medium text-gray-700'>Período *</label>
              <select
                required
                value={formData.period}
                onChange={(e) => setFormData({ ...formData, period: e.target.value })}
                className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              >
                <option value=''>Seleccione un período</option>
                {periods.map((period) => (
                  <option key={period.id} value={period.id}>
                    {period.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className='grid grid-cols-2 gap-4'>
            <div>
              <label className='block text-sm font-medium text-gray-700'>Trimestre *</label>
              <select
                required
                value={formData.trimester}
                onChange={(e) => setFormData({ ...formData, trimester: e.target.value })}
                className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              >
                <option value='1'>Trimestre 1</option>
                <option value='2'>Trimestre 2</option>
                <option value='3'>Trimestre 3</option>
              </select>
            </div>

            <div className='bg-gray-50 p-3 rounded-lg'>
              <label className='block text-sm font-medium text-gray-700'>Nota Final</label>
              <div className={`text-2xl font-bold mt-1 ${
                parseFloat(formData.final_score) >= 7 ? 'text-green-600' : 
                parseFloat(formData.final_score) >= 5 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {formData.final_score || '0.00'}
              </div>
              <p className='text-xs text-gray-500 mt-1'>Calculada automáticamente</p>
            </div>
          </div>

          <div className='border-t pt-4'>
            <h3 className='text-lg font-medium text-gray-900 mb-3'>Dimensiones de Evaluación</h3>
            <div className='grid grid-cols-2 gap-4'>
              <div>
                <label className='block text-sm font-medium text-gray-700'>Ser (0-10)</label>
                <input
                  type='number'
                  min='0'
                  max='10'
                  step='0.1'
                  value={formData.dimension_ser}
                  onChange={(e) => setFormData({ ...formData, dimension_ser: e.target.value })}
                  className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
                  placeholder='0.0 - 10.0'
                />
              </div>

              <div>
                <label className='block text-sm font-medium text-gray-700'>Saber (0-10)</label>
                <input
                  type='number'
                  min='0'
                  max='10'
                  step='0.1'
                  value={formData.dimension_saber}
                  onChange={(e) => setFormData({ ...formData, dimension_saber: e.target.value })}
                  className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
                  placeholder='0.0 - 10.0'
                />
              </div>

              <div>
                <label className='block text-sm font-medium text-gray-700'>Hacer (0-10)</label>
                <input
                  type='number'
                  min='0'
                  max='10'
                  step='0.1'
                  value={formData.dimension_hacer}
                  onChange={(e) => setFormData({ ...formData, dimension_hacer: e.target.value })}
                  className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
                  placeholder='0.0 - 10.0'
                />
              </div>

              <div>
                <label className='block text-sm font-medium text-gray-700'>Decidir (0-10)</label>
                <input
                  type='number'
                  min='0'
                  max='10'
                  step='0.1'
                  value={formData.dimension_decidir}
                  onChange={(e) => setFormData({ ...formData, dimension_decidir: e.target.value })}
                  className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
                  placeholder='0.0 - 10.0'
                />
              </div>
            </div>
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700'>Observaciones</label>
            <textarea
              value={formData.observations}
              onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
              className='mt-1 block w-full rounded-lg border border-gray-300 p-2'
              rows={3}
              placeholder='Observaciones adicionales...'
              maxLength={500}
            />
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
              {editingScore ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}