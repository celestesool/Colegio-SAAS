import { useEffect, useMemo, useState } from 'react';
import { apiFetch } from '../../utils/api';
import BarcodeScanner from '../../components/BarcodeScanner';
import DataTable from '../../components/DataTable';

export default function AttendanceContent() {
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [grade, setGrade] = useState('');
  const [section, setSection] = useState('');
  const [subject, setSubject] = useState('');
  const [period, setPeriod] = useState('');
  const [session, setSession] = useState(null);
  const [tab, setTab] = useState('manual');
  const [grades, setGrades] = useState([]);
  const [sections, setSections] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [periods, setPeriods] = useState([]);
  const [students, setStudents] = useState([]);
  const [records, setRecords] = useState({});
  const [loading, setLoading] = useState(false);

  // === Cargar catálogos ===
  useEffect(() => { apiFetch('/grades').then(r => r.json()).then(setGrades); }, []);
  useEffect(() => { apiFetch('/periods').then(r => r.json()).then(setPeriods); }, []);
  useEffect(() => {
    if (!grade) return;
    apiFetch(`/sections?grade=${grade}`).then(r => r.json()).then(setSections);
    apiFetch(`/subjects?level=${grade}`).then(r => r.json()).then(setSubjects);
  }, [grade]);

  // === Crear sesión ===
  async function createSession() {
    if (!grade || !section || !subject || !period) {
      alert('Seleccione grado, sección, materia y período');
      return;
    }
    const body = {
      grade,
      section,
      subject,
      period,
      date,
      start_time: "08:00:00"
    };
    const res = await apiFetch('/attendance-sessions/', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (!res.ok) return alert('Error al crear sesión');
    const data = await res.json();
    setSession(data);
    fetchStudents();
  }

  // === Obtener alumnos ===
  async function fetchStudents() {
    setLoading(true);
    const res = await apiFetch(`/students?section=${section}`);
    const data = res.ok ? await res.json() : [];
    setStudents(data);
    setLoading(false);
  }

  // === Registrar manual ===
  async function saveManual() {
    if (!session) return alert('Crea una sesión primero');
    const toSend = Object.entries(records)
      .filter(([, s]) => s)
      .map(([student, status]) => ({ session: session.id, student, status }));
    if (!toSend.length) return alert('Sin cambios');
    await Promise.all(toSend.map(i =>
      apiFetch('/attendance-records/', { method: 'POST', body: JSON.stringify(i) })
    ));
    alert('Asistencia registrada');
  }

  // === Registrar con lector ===
  async function onScan(code) {
    if (!session) return alert('Crea o selecciona una sesión primero');
    const res = await apiFetch('/attendance/qr-scan/', {
      method: 'POST',
      body: JSON.stringify({ code, session_id: session.id }),
    });
    const data = await res.json();
    if (res.ok) {
      alert(`Asistencia: ${data.status}`);
      await fetchRecords(); // actualizar lista
    } else alert(data.error || 'Error en escaneo');
  }

  // === Obtener registros ya existentes ===
  async function fetchRecords() {
    if (!session) return;
    const res = await apiFetch(`/attendance-records/?session=${session.id}`);
    const list = res.ok ? await res.json() : [];
    const map = {};
    list.forEach(r => { map[r.student] = r.status; });
    setRecords(map);
  }

  // === Columnas tabla ===
  const columns = useMemo(() => ([
    { title: 'Código', render: s => s.code },
    { title: 'Nombre', render: s => s.person_name },
    {
      title: 'Estado',
      render: s => (
        <select
          value={records[s.id] || ''}
          onChange={e => setRecords(prev => ({ ...prev, [s.id]: e.target.value }))}
          className="rounded border px-2 py-1"
        >
          <option value="">—</option>
          <option value="PRESENTE">Presente</option>
          <option value="RETRASO">Retraso</option>
          <option value="AUSENTE">Ausente</option>
          <option value="FALTA_JUSTIFICADA">Justificada</option>
        </select>
      ),
    },
  ]), [records]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Control de Asistencia</h2>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <input type="date" value={date} onChange={e => setDate(e.target.value)} className="rounded border px-3 py-2" />
        <select value={grade} onChange={e => setGrade(e.target.value)} className="rounded border px-3 py-2">
          <option value="">Grado</option>
          {grades.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
        <select value={section} onChange={e => setSection(e.target.value)} className="rounded border px-3 py-2">
          <option value="">Sección</option>
          {sections.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select value={subject} onChange={e => setSubject(e.target.value)} className="rounded border px-3 py-2">
          <option value="">Materia</option>
          {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select value={period} onChange={e => setPeriod(e.target.value)} className="rounded border px-3 py-2">
          <option value="">Período</option>
          {periods.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>

      {!session && (
        <button onClick={createSession} className="bg-indigo-600 text-white px-4 py-2 rounded">
          Crear Sesión
        </button>
      )}

      {session && (
        <>
          <div className="flex w-max rounded border">
            <button onClick={() => setTab('manual')}
              className={`px-4 py-2 ${tab === 'manual' ? 'bg-indigo-600 text-white' : ''}`}>
              Manual
            </button>
            <button onClick={() => setTab('scanner')}
              className={`px-4 py-2 ${tab === 'scanner' ? 'bg-indigo-600 text-white' : ''}`}>
              Lector
            </button>
          </div>

          {tab === 'manual' ? (
            <>
              {loading ? (
                <p>Cargando estudiantes...</p>
              ) : (
                <>
                  <DataTable columns={columns} data={students} />
                  <div className="flex justify-end">
                    <button onClick={saveManual} className="bg-indigo-600 text-white px-4 py-2 rounded">
                      Guardar
                    </button>
                  </div>
                </>
              )}
            </>
          ) : (
            <BarcodeScanner onResult={onScan} />
          )}
        </>
      )}
    </div>
  );
}