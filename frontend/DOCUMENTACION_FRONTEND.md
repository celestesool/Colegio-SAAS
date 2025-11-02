# Documentación Técnica del Frontend - Sistema de Gestión Académica SaaS

## Índice
1. [Arquitectura General](#arquitectura-general)
2. [Estructura de Directorios](#estructura-de-directorios)
3. [Tecnologías y Dependencias](#tecnologías-y-dependencias)
4. [Sistema de Routing](#sistema-de-routing)
5. [Componentes](#componentes)
6. [Páginas Principales](#páginas-principales)
7. [Gestión de Estado](#gestión-de-estado)
8. [Sistema de Autenticación](#sistema-de-autenticación)
9. [Integración con Backend](#integración-con-backend)
10. [Estilos y UI](#estilos-y-ui)
11. [Deployment](#deployment)

---

## Arquitectura General

El frontend está desarrollado con **React 19.1.1** y **Vite 7.1.2**, implementando una **Single Page Application (SPA)** que consume las APIs REST del backend Django. La aplicación utiliza **Tailwind CSS 4.1.13** para el diseño y **React Router DOM 7.9.1** para la navegación.

### Características Principales:
- **React 19.1.1**: Framework de UI moderno con Hooks
- **Vite**: Build tool rápido para desarrollo y producción
- **Tailwind CSS**: Framework de CSS utility-first
- **React Router**: Navegación declarativa del lado del cliente
- **ESLint + Prettier**: Linting y formateo de código
- **Responsive Design**: Diseño adaptativo para móviles y desktop

---

## Estructura de Directorios

```
frontend/
├── public/                    # Archivos estáticos públicos
│   ├── vite.svg              # Favicon de Vite
│   └── images/               # Imágenes del proyecto
│       ├── logo.png          # Logo principal
│       ├── logo_y_nombre.png # Logo con nombre
│       └── logo_y_nombre_sin_fondo.jpg
├── src/                      # Código fuente principal
│   ├── main.jsx             # Punto de entrada de la aplicación
│   ├── App.jsx              # Componente raíz con rutas
│   ├── index.css            # Estilos globales y Tailwind
│   ├── assets/              # Recursos de desarrollo
│   │   └── react.svg        # Logo de React
│   ├── components/          # Componentes reutilizables
│   │   ├── DataTable.jsx    # Tabla de datos genérica
│   │   ├── FeatureCard.jsx  # Tarjeta de características
│   │   ├── Modal.jsx        # Modal genérico
│   │   ├── NavBar.jsx       # Barra de navegación
│   │   ├── PriceCard.jsx    # Tarjeta de precios
│   │   ├── SideBar.jsx      # Barra lateral del panel admin
│   │   └── TestimonialCard.jsx # Tarjeta de testimonios
│   ├── constants/           # Constantes globales
│   │   └── index.js         # Configuraciones del sistema
│   ├── pages/               # Páginas principales
│   │   ├── LandingPage.jsx  # Página de inicio/marketing
│   │   ├── LoginPage.jsx    # Página de inicio de sesión
│   │   ├── SignUpPage.jsx   # Página de registro
│   │   ├── RegisterSchoolPage.jsx # Registro de colegios
│   │   ├── PanelAdminPage.jsx # Panel de administración
│   │   └── content/         # Contenidos del panel admin
│   │       ├── index.jsx    # Exportaciones centralizadas
│   │       ├── DashboardContent.jsx     # Dashboard principal
│   │       ├── LevelsContent.jsx        # Gestión de niveles educativos
│   │       ├── PeriodsContent.jsx       # Gestión de períodos académicos
│   │       ├── GradesContent.jsx        # Gestión de grados
│   │       ├── SectionsContent.jsx      # Gestión de secciones
│   │       ├── SubjectsContent.jsx      # Gestión de materias
│   │       ├── PersonsContent.jsx       # Gestión de personas
│   │       ├── StudentsContent.jsx      # Gestión de estudiantes
│   │       ├── EnrollmentsContent.jsx   # Gestión de matrículas
│   │       └── ReportsContent.jsx       # Reportes (futuro)
│   ├── secure/              # Componentes de seguridad
│   │   └── ProtectedRoute.jsx # Rutas protegidas
│   └── utils/               # Utilidades
│       └── getServer.js     # Funciones para comunicación con API
├── package.json             # Dependencias y scripts npm
├── vite.config.js          # Configuración de Vite
├── eslint.config.js        # Configuración de ESLint
├── index.html              # Template HTML principal
├── Dockerfile              # Imagen Docker para desarrollo
├── Dockerfile.prod         # Imagen Docker para producción
└── README.md               # Documentación básica
```

---

## Tecnologías y Dependencias

### Dependencias de Producción (`package.json`)
```json
{
  "dependencies": {
    "@tailwindcss/vite": "4.1.13",    // Plugin de Tailwind para Vite
    "react": "19.1.1",               // Librería principal de React
    "react-dom": "19.1.1",           // DOM renderer para React
    "react-router-dom": "7.9.1",     // Routing del lado del cliente
    "tailwindcss": "4.1.13"          // Framework CSS utility-first
  }
}
```

### Dependencias de Desarrollo
```json
{
  "devDependencies": {
    "@eslint/js": "9.33.0",                    // ESLint core
    "@types/react": "19.1.10",                 // TypeScript types para React
    "@types/react-dom": "19.1.7",              // TypeScript types para React DOM
    "@vitejs/plugin-react": "5.0.0",           // Plugin de React para Vite
    "eslint": "9.35.0",                        // Linter de JavaScript
    "eslint-config-prettier": "10.1.8",        // Configuración ESLint compatible con Prettier
    "eslint-plugin-prettier": "5.5.4",         // Plugin de Prettier para ESLint
    "eslint-plugin-react-hooks": "5.2.0",      // Reglas ESLint para React Hooks
    "eslint-plugin-react-refresh": "0.4.20",   // Plugin para React Refresh
    "globals": "16.3.0",                       // Variables globales para ESLint
    "prettier": "3.6.2",                       // Formateador de código
    "prettier-plugin-tailwindcss": "0.6.14",   // Plugin de Prettier para Tailwind
    "vite": "7.1.2"                           // Build tool y dev server
  }
}
```

### Scripts de NPM
```json
{
  "scripts": {
    "dev": "vite",              // Servidor de desarrollo
    "build": "vite build",      // Build para producción
    "lint": "eslint .",         // Ejecutar linter
    "lint:fix": "eslint . --fix", // Ejecutar y corregir errores de linting
    "preview": "vite preview"   // Preview del build de producción
  }
}
```

---

## Sistema de Routing

### Configuración Principal (`App.jsx`)

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import PanelAdminPage from './pages/PanelAdminPage';
import SignUpPage from './pages/SignUpPage';
import RegisterSchoolPage from './pages/RegisterSchoolPage';
import ProtectedRoute from './secure/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<LandingPage />} />
        <Route path='/login' element={<LoginPage />} />
        <Route path='/signup' element={<SignUpPage />} />
        <Route path='/register-school' element={<RegisterSchoolPage />} />
        <Route
          path='/panel-admin'
          element={
            <ProtectedRoute>
              <PanelAdminPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
```

### Rutas Principales

| Ruta | Componente | Descripción | Protegida |
|------|------------|-------------|-----------|
| `/` | `LandingPage` | Página de inicio y marketing | No |
| `/login` | `LoginPage` | Inicio de sesión | No |
| `/signup` | `SignUpPage` | Registro de usuarios | No |
| `/register-school` | `RegisterSchoolPage` | Registro de colegios | No |
| `/panel-admin` | `PanelAdminPage` | Panel de administración | Sí |

### Protección de Rutas (`secure/ProtectedRoute.jsx`)

```jsx
// Lógica para verificar autenticación
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('accessToken');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};
```

---

## Componentes

### Componentes Reutilizables

#### 1. **DataTable** (`components/DataTable.jsx`)
**Propósito**: Tabla genérica para mostrar datos tabulares con acciones CRUD.

**Props**:
- `columns`: Configuración de columnas
- `data`: Datos a mostrar
- `onEdit`: Callback para editar
- `onDelete`: Callback para eliminar

**Características**:
- Renderizado dinámico de columnas
- Acciones personalizables por fila
- Responsive design
- Soporte para campos computed/calculados

#### 2. **Modal** (`components/Modal.jsx`)
**Propósito**: Modal genérico para formularios y confirmaciones.

**Props**:
- `isOpen`: Estado de visibilidad
- `onClose`: Callback para cerrar
- `title`: Título del modal
- `children`: Contenido del modal

**Características**:
- Overlay con blur
- Animaciones de entrada/salida
- Cierre por escape o click fuera
- Responsive

#### 3. **NavBar** (`components/NavBar.jsx`)
**Propósito**: Barra de navegación para la landing page.

**Props**:
- `routes`: Array de rutas de navegación

**Características**:
- Navegación suave con scroll
- Responsive con hamburger menu
- Logo y branding integrado

#### 4. **SideBar** (`components/SideBar.jsx`)
**Propósito**: Barra lateral del panel de administración.

**Props**:
- `activeSection`: Sección actualmente activa
- `setActiveSection`: Callback para cambiar sección

**Características**:
- Menú jerárquico con submenús
- Iconos descriptivos
- Estado expandido/colapsado por sección
- Indicador visual de sección activa

#### 5. **FeatureCard** (`components/FeatureCard.jsx`)
**Propósito**: Tarjeta para mostrar características del sistema.

**Props**:
- `icon`: Icono SVG
- `title`: Título de la característica
- `description`: Descripción detallada

#### 6. **PriceCard** (`components/PriceCard.jsx`)
**Propósito**: Tarjeta para mostrar planes de precios.

**Props**:
- `plan`: Nombre del plan
- `price`: Precio del plan
- `period`: Período (mes/año)
- `description`: Descripción del plan
- `features`: Array de características
- `isPopular`: Si es el plan destacado

#### 7. **TestimonialCard** (`components/TestimonialCard.jsx`)
**Propósito**: Tarjeta para testimonios de clientes.

**Props**:
- `name`: Nombre del cliente
- `role`: Cargo del cliente
- `content`: Testimonial
- `rating`: Puntuación (estrellas)

---

## Páginas Principales

### 1. **LandingPage** (`pages/LandingPage.jsx`)

**Propósito**: Página de marketing y presentación del sistema.

**Estructura**:
```jsx
function LandingPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Carga planes desde API
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const data = await server().getPlanes();
        setPlans(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchPlans();
  }, []);
}
```

**Secciones**:
- **Header**: Título principal y CTA
- **Features**: Características del sistema
- **Pricing**: Planes de suscripción dinámicos
- **Testimonials**: Testimonios de clientes
- **Footer**: Enlaces e información de contacto

**Características**:
- Carga dinámica de planes desde API
- Responsive design
- Animaciones y transiciones suaves
- SEO optimizado

### 2. **LoginPage** (`pages/LoginPage.jsx`)

**Propósito**: Autenticación de usuarios existentes.

**Funcionalidades**:
- Formulario de login con email/password
- Validación de campos
- Integración con JWT
- Redirección automática tras login exitoso
- Manejo de errores de autenticación

### 3. **SignUpPage** (`pages/SignUpPage.jsx`)

**Propósito**: Registro de nuevos usuarios.

**Funcionalidades**:
- Formulario de registro
- Validación de datos
- Creación de cuenta
- Redirección a login tras registro exitoso

### 4. **RegisterSchoolPage** (`pages/RegisterSchoolPage.jsx`)

**Propósito**: Registro de nuevos colegios con selección de plan.

**Estructura**:
```jsx
const plans = [
  {
    id: 1,
    name: 'Plan Básico',
    price: 120,
    period: 'M',
    description: 'Perfecto para pequeñas academias',
    features: [
      'Hasta 1000 alumnos',
      'Gestión académica básica',
      'Gestión de matrículas',
      'Comunicación con padres',
    ],
  },
  // Más planes...
];
```

**Funcionalidades**:
- Selección de plan de suscripción
- Formulario de datos del colegio
- Validación de información
- Creación de tenant/colegio

### 5. **PanelAdminPage** (`pages/PanelAdminPage.jsx`)

**Propósito**: Panel principal de administración del colegio.

**Estructura**:
```jsx
export default function PanelAdminPage() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const navigate = useNavigate();

  const handleLogOut = () => {
    // Lógica de logout
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard': return <DashboardContent />;
      case 'levels': return <LevelsContent />;
      case 'periods': return <PeriodsContent />;
      case 'grades': return <GradesContent />;
      case 'sections': return <SectionsContent />;
      case 'subjects': return <SubjectsContent />;
      case 'persons': return <PersonsContent />;
      case 'students': return <StudentsContent />;
      case 'enrollments': return <EnrollmentsContent />;
      default: return <DashboardContent />;
    }
  };
}
```

**Características**:
- Layout con sidebar navegable
- Contenido dinámico por sección
- Header con información del usuario
- Logout functionality

---

## Contenidos del Panel de Administración

### Estructura de Contenidos (`pages/content/`)

Todos los contenidos siguen un patrón similar de gestión CRUD:

#### Patrón Base de Componente de Gestión
```jsx
export default function ExampleContent() {
  // Estados principales
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({});

  // Configuración de columnas para DataTable
  const columns = [
    { key: 'name', title: 'Nombre' },
    { key: 'status', title: 'Estado', render: (item) => /* JSX */ },
    // Más columnas...
  ];

  // Funciones CRUD
  const fetchItems = async () => { /* Cargar datos */ };
  const handleSave = async () => { /* Guardar/actualizar */ };
  const handleDelete = async (id) => { /* Eliminar */ };
  const handleEdit = (item) => { /* Preparar edición */ };
  const handleNew = () => { /* Nuevo elemento */ };

  // Efectos para carga inicial
  useEffect(() => {
    fetchItems();
  }, []);

  return (
    <div>
      {/* Header con botón nuevo */}
      <div className='mb-6 flex items-center justify-between'>
        <h2 className='text-2xl font-bold text-gray-900'>Título</h2>
        <button onClick={handleNew} className='btn-primary'>
          Nuevo
        </button>
      </div>

      {/* Tabla de datos */}
      <DataTable
        columns={columns}
        data={items}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {/* Modal para formulario */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
        {/* Formulario */}
      </Modal>
    </div>
  );
}
```

### Contenidos Específicos

#### 1. **DashboardContent** (`content/DashboardContent.jsx`)
- **Propósito**: Panel de control principal con métricas
- **Contenido**: Estadísticas generales, widgets informativos

#### 2. **LevelsContent** (`content/LevelsContent.jsx`)
- **Gestiona**: Niveles educativos (Inicial, Primaria, Secundaria)
- **Campos**: name, short_name, is_active
- **API**: `/api/levels`

#### 3. **PeriodsContent** (`content/PeriodsContent.jsx`)
- **Gestiona**: Períodos académicos (años lectivos, semestres)
- **Campos**: name, start_date, end_date, is_active
- **API**: `/api/periods`

#### 4. **GradesContent** (`content/GradesContent.jsx`)
- **Gestiona**: Grados dentro de niveles educativos
- **Campos**: level, name, order, is_active
- **API**: `/api/grades`
- **Relaciones**: Depende de LevelsContent

#### 5. **SectionsContent** (`content/SectionsContent.jsx`)
- **Gestiona**: Secciones/paralelos de grados
- **Campos**: grade, name, capacity, is_active
- **API**: `/api/sections`
- **Relaciones**: Depende de GradesContent y LevelsContent

**Estructura detallada**:
```jsx
export default function SectionsContent() {
  const [sections, setSections] = useState([]);
  const [grades, setGrades] = useState([]);
  const [levels, setLevels] = useState([]);

  // Carga jerárquica de datos
  useEffect(() => {
    fetchLevels();
  }, []);

  useEffect(() => {
    if (levels.length > 0) {
      fetchGrades();
    }
  }, [levels]);

  useEffect(() => {
    if (grades.length > 0) {
      fetchSections();
    }
  }, [grades]);

  const fetchSections = async () => {
    // Enriquecer datos con nombres de nivel y grado
    const sectionsWithRelations = data.map((section) => ({
      ...section,
      grade_name: grades.find((grade) => grade.id === section.grade)?.name || 'N/A',
      level_name: levels.find((level) => 
        level.id === grades.find((grade) => grade.id === section.grade)?.level
      )?.name || 'N/A',
    }));
  };
}
```

#### 6. **SubjectsContent** (`content/SubjectsContent.jsx`)
- **Gestiona**: Materias/asignaturas por nivel
- **Campos**: level, name, short_name, is_active
- **API**: `/api/subjects`

#### 7. **PersonsContent** (`content/PersonsContent.jsx`)
- **Gestiona**: Datos personales de individuos
- **Campos**: first_name, last_name, doc_type, doc_number, birth_date, email, phone, address
- **API**: `/api/persons`

#### 8. **StudentsContent** (`content/StudentsContent.jsx`)
- **Gestiona**: Estudiantes vinculados a personas
- **Campos**: person, code, enrollment_date, is_active
- **API**: `/api/students`
- **Relaciones**: Depende de PersonsContent

#### 9. **EnrollmentsContent** (`content/EnrollmentsContent.jsx`)
- **Gestiona**: Matrículas de estudiantes
- **Campos**: student, period, grade, section, enrollment_date, status
- **API**: `/api/enrollments`
- **Relaciones**: Depende de múltiples entidades

#### 10. **ReportsContent** (`content/ReportsContent.jsx`)
- **Estado**: En desarrollo futuro
- **Propósito**: Generación de reportes académicos

---

## Gestión de Estado

### Estados Locales con useState

Cada componente maneja su estado local usando React Hooks:

```jsx
// Estados típicos en componentes de gestión
const [data, setData] = useState([]);           // Datos principales
const [loading, setLoading] = useState(true);   // Estado de carga
const [error, setError] = useState('');         // Mensajes de error
const [showModal, setShowModal] = useState(false); // Control de modales
const [editingItem, setEditingItem] = useState(null); // Item en edición
const [formData, setFormData] = useState({});   // Datos del formulario
```

### Patrón de Manejo de Estados

#### Carga de Datos
```jsx
const fetchData = async () => {
  try {
    setLoading(true);
    setError('');
    const response = await fetch('api/endpoint', {
      credentials: 'include',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      },
    });

    if (!response.ok) throw new Error('Error al cargar datos');

    const data = await response.json();
    setData(data);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

#### Operaciones CRUD
```jsx
const handleSave = async () => {
  try {
    const method = editingItem ? 'PUT' : 'POST';
    const url = editingItem ? `api/endpoint/${editingItem.id}` : 'api/endpoint';

    const response = await fetch(url, {
      method,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) throw new Error('Error al guardar');

    await fetchData(); // Recargar datos
    setShowModal(false);
    resetForm();
  } catch (err) {
    setError(err.message);
  }
};
```

### Sin Estado Global

La aplicación **no utiliza Redux, Zustand o Context API** para estado global por diseño:

**Razones**:
- **Simplicidad**: Cada sección es independiente
- **Performance**: Evita re-renders innecesarios
- **Mantenibilidad**: Estado local más fácil de debuggear
- **Escalabilidad**: Cada módulo se puede desarrollar independientemente

**Datos Compartidos**:
- **Autenticación**: Almacenada en localStorage
- **Configuración**: Constantes estáticas
- **Comunicación**: A través de props cuando es necesario

---

## Sistema de Autenticación

### Flujo de Autenticación

#### 1. **Login Process**
```jsx
// LoginPage.jsx
const handleLogin = async (e) => {
  e.preventDefault();
  try {
    const response = await fetch('api/auth/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) throw new Error('Credenciales inválidas');

    const data = await response.json();
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    
    navigate('/panel-admin');
  } catch (err) {
    setError(err.message);
  }
};
```

#### 2. **Token Storage**
```javascript
// Almacenamiento en localStorage
localStorage.setItem('accessToken', token);
localStorage.setItem('refreshToken', refreshToken);

// Recuperación para requests
const token = localStorage.getItem('accessToken');
```

#### 3. **Protected Routes**
```jsx
// secure/ProtectedRoute.jsx
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('accessToken');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  // TODO: Validar expiración del token
  return children;
};
```

#### 4. **Logout Process**
```jsx
// PanelAdminPage.jsx
const handleLogOut = () => {
  fetch('api/auth/logout/', { 
    method: 'POST', 
    credentials: 'include' 
  })
  .then((response) => {
    if (response.ok) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      navigate('/login');
    }
  })
  .catch((error) => {
    console.error('Error al cerrar sesión:', error);
  });
};
```

### Headers de Autenticación

Todas las requests a APIs protegidas incluyen el token JWT:

```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
};
```

### Limitaciones Actuales

1. **No hay refresh automático de tokens**
2. **No se valida expiración en el frontend**
3. **No hay logout automático por inactividad**
4. **Tokens en localStorage (vulnerabilidad XSS)**

### Mejoras Futuras

1. **Token refresh automático**
2. **HttpOnly cookies para mayor seguridad**
3. **Interceptores de Axios para manejo centralizado**
4. **Context de autenticación global**

---

## Integración con Backend

### Utilidades de API (`utils/getServer.js`)

**Funciones disponibles**:
```javascript
export function server() {
  return {
    getPlanes: async function () {
      try {
        const response = await fetch('api/plans');
        if (!response.ok) {
          throw new Error('Error al cargar los planes');
        }
        return await response.json();
      } catch (error) {
        console.error(error);
        throw error;
      }
    },
  };
}
```

### Patrón de Comunicación con API

#### Request Base
```javascript
const makeRequest = async (endpoint, options = {}) => {
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    },
  };

  const response = await fetch(endpoint, { ...defaultOptions, ...options });
  
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
};
```

#### Operaciones CRUD Típicas
```javascript
// GET - Listar
const fetchItems = () => makeRequest('api/endpoint');

// POST - Crear
const createItem = (data) => makeRequest('api/endpoint', {
  method: 'POST',
  body: JSON.stringify(data)
});

// PUT - Actualizar
const updateItem = (id, data) => makeRequest(`api/endpoint/${id}`, {
  method: 'PUT',
  body: JSON.stringify(data)
});

// DELETE - Eliminar
const deleteItem = (id) => makeRequest(`api/endpoint/${id}`, {
  method: 'DELETE'
});
```

### Manejo de Errores

#### En Componentes
```jsx
const [error, setError] = useState('');

try {
  // API call
} catch (err) {
  setError(err.message);
  console.error('Error:', err);
}

// En JSX
{error && (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
    Error: {error}
  </div>
)}
```

#### Estados de Carga
```jsx
{loading ? (
  <div className='py-8 text-center'>Cargando...</div>
) : error ? (
  <div className='py-8 text-center text-red-600'>Error: {error}</div>
) : (
  <DataTable data={data} />
)}
```

---

## Estilos y UI

### Tailwind CSS

#### Configuración (`index.css`)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Estilos personalizados adicionales */
```

#### Clases Utilitarias Comunes

**Layout y Espaciado**:
```css
.container { @apply mx-auto max-w-6xl px-4; }
.card { @apply bg-white rounded-lg shadow-lg p-6; }
.section { @apply py-16 px-4; }
```

**Botones**:
```css
.btn-primary { 
  @apply bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition;
}
.btn-secondary { 
  @apply bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-lg transition;
}
.btn-danger { 
  @apply bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition;
}
```

**Estados**:
```css
.badge-active { @apply bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs; }
.badge-inactive { @apply bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs; }
```

### Responsive Design

#### Breakpoints de Tailwind
- `sm`: 640px+
- `md`: 768px+ 
- `lg`: 1024px+
- `xl`: 1280px+
- `2xl`: 1536px+

#### Patrones Responsive Comunes
```jsx
// Grids responsivos
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

// Texto responsivo
<h1 className="text-2xl md:text-4xl lg:text-6xl font-bold">

// Espaciado responsivo
<div className="p-4 md:p-6 lg:p-8">

// Flex responsivo
<div className="flex flex-col md:flex-row items-center gap-4">
```

### Componentes de UI

#### Modal
```jsx
<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6">
    {/* Contenido */}
  </div>
</div>
```

#### DataTable
```jsx
<div className="overflow-x-auto">
  <table className="min-w-full bg-white">
    <thead className="bg-gray-50">
      <tr>
        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
          Nombre
        </th>
      </tr>
    </thead>
    <tbody className="bg-white divide-y divide-gray-200">
      {/* Filas */}
    </tbody>
  </table>
</div>
```

#### Sidebar
```jsx
<div className="flex w-64 flex-col bg-indigo-800 text-white">
  <nav className="flex-1 overflow-y-auto pt-2">
    {/* Items de navegación */}
  </nav>
</div>
```

### Tema de Colores

#### Paleta Principal
- **Primary**: Indigo (indigo-600, indigo-700, indigo-800)
- **Secondary**: Gray (gray-100, gray-200, gray-700, gray-900)
- **Success**: Green (green-100, green-800)
- **Danger**: Red (red-100, red-600, red-700, red-800)
- **Warning**: Yellow/Orange

#### Gradientes
```css
bg-gradient-to-br from-blue-50 to-indigo-100
```

---

## Deployment

### Desarrollo Local

#### Requisitos
- Node.js 18+ y npm
- Backend Django ejecutándose en puerto 8000

#### Comandos
```bash
# Instalar dependencias
npm install

# Servidor de desarrollo
npm run dev          # http://localhost:5173

# Linting
npm run lint         # Verificar código
npm run lint:fix     # Corregir errores automáticamente
```

### Build de Producción

```bash
# Generar build optimizado
npm run build

# Preview del build
npm run preview
```

### Docker

#### Desarrollo (`Dockerfile`)
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
```

#### Producción (`Dockerfile.prod`)
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Variables de Entorno

#### Desarrollo
```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

#### Producción
- **API_BASE_URL**: URL del backend
- **VITE_APP_TITLE**: Título de la aplicación
- **VITE_APP_VERSION**: Versión de la aplicación

---

## Configuración de Herramientas

### ESLint (`eslint.config.js`)
```javascript
import js from '@eslint/js'
import globals from 'globals'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    settings: { react: { version: '18.3' } },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      'react/jsx-no-target-blank': 'off',
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
]
```

### Prettier
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

### Vite (`vite.config.js`)
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## Flujos de Usuario

### 1. **Flujo de Registro de Colegio**
1. Usuario visita landing page (`/`)
2. Clic en "Comenzar ahora" → `/register-school`
3. Selección de plan de suscripción
4. Formulario con datos del colegio
5. Creación de tenant en backend
6. Redirección a login (`/login`)

### 2. **Flujo de Login y Gestión**
1. Usuario inicia sesión (`/login`)
2. Obtención de JWT tokens
3. Redirección a panel admin (`/panel-admin`)
4. Navegación por sidebar a diferentes secciones
5. Operaciones CRUD en cada módulo

### 3. **Flujo de Gestión Académica**
1. **Configuración inicial**:
   - Niveles educativos
   - Períodos académicos
   - Grados por nivel
   - Secciones por grado
   - Materias por nivel

2. **Gestión de personas**:
   - Registro de personas
   - Creación de estudiantes
   - Matrículas en períodos/grados/secciones

### 4. **Flujo de Operaciones CRUD**
1. Selección de módulo en sidebar
2. Carga de datos desde API
3. Visualización en DataTable
4. Acciones: Nuevo/Editar/Eliminar
5. Modal con formulario
6. Validación y envío
7. Actualización de datos

---

## Optimizaciones y Performance

### Técnicas Implementadas

#### 1. **Code Splitting**
- Componentes cargados dinámicamente
- Rutas con lazy loading (futuro)

#### 2. **Optimización de Renders**
- useState para estado local específico
- useEffect con dependencias correctas
- Evitar re-renders innecesarios

#### 3. **Bundle Optimization**
- Vite para builds optimizados
- Tree shaking automático
- Compresión y minificación

### Mejoras Futuras

#### 1. **React Query/SWR**
- Cache de datos de API
- Sincronización automática
- Optimistic updates

#### 2. **Virtual Scrolling**
- Para tablas con muchos datos
- Mejora performance en listas largas

#### 3. **Service Workers**
- Cache offline
- Push notifications
- Progressive Web App (PWA)

#### 4. **Image Optimization**
- Lazy loading de imágenes
- Formatos optimizados (WebP)
- Responsive images

---

## Testing (Futuro)

### Herramientas Planificadas
- **Vitest**: Testing framework
- **React Testing Library**: Testing de componentes
- **Cypress**: Tests E2E
- **MSW**: Mock Service Worker para APIs

### Tipos de Tests
1. **Unit Tests**: Componentes individuales
2. **Integration Tests**: Flujos de usuario
3. **E2E Tests**: Scenarios completos
4. **API Tests**: Integración con backend

---

## Consideraciones de Seguridad

### Implementadas
1. **HTTPS en producción**
2. **Validación de inputs en frontend**
3. **Headers de autenticación en requests**
4. **Sanitización de datos mostrados**

### Pendientes
1. **CSP (Content Security Policy)**
2. **Tokens en HttpOnly cookies**
3. **Validación de permisos en UI**
4. **Rate limiting en frontend**

---

## Roadmap y Funcionalidades Futuras

### Corto Plazo
1. **Mejoras UX**:
   - Loading skeletons
   - Toast notifications
   - Confirmaciones de acciones

2. **Funcionalidades**:
   - Búsqueda global
   - Filtros avanzados
   - Exportación de datos

### Mediano Plazo
1. **PWA**:
   - Service workers
   - Instalación como app
   - Funcionalidad offline

2. **Tiempo Real**:
   - WebSockets
   - Notificaciones push
   - Actualizaciones automáticas

### Largo Plazo
1. **Mobile App**:
   - React Native
   - Funcionalidades específicas móviles
   - Sincronización offline

2. **Advanced Features**:
   - Dashboard analytics
   - Reportes avanzados
   - Integración con sistemas externos

---

*Esta documentación está actualizada al 4 de octubre de 2025 y refleja el estado actual del frontend del Sistema de Gestión Académica SaaS.*