# Estructura del frontend (Colegio-SAAS)

Este documento describe la estructura del frontend dentro de la carpeta `frontend/` y la función de cada archivo/carpeta. Incluye dónde integrar la interfaz de asistencia y escaneo QR.

Resumen del árbol principal (`frontend/`):

frontend/
├── package.json                     # Dependencias y scripts (dev/build)
├── vite.config.js                   # Configuración Vite
├── index.html                       # HTML principal
├── src/
│   ├── main.jsx                     # Punto de entrada React
│   ├── App.jsx                      # Rutas y layout global
│   ├── index.css                    # Estilos globales
│   ├── assets/                      # Imágenes y recursos estáticos
│   ├── components/                  # Componentes reutilizables (UI)
│   │   ├── NavBar.jsx
│   │   ├── SideBar.jsx
│   │   ├── DataTable.jsx
│   │   ├── Modal.jsx
│   │   └── ...
│   ├── pages/                       # Páginas principales
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
````markdown
# Estructura del frontend (Colegio-SAAS) — Actualizado

Este documento describe la estructura del frontend y las nuevas páginas/componentes pensadas para la funcionalidad de asistencia y QR.

Resumen del árbol principal (`frontend/`):

frontend/
├── package.json                     # Dependencias y scripts (dev/build)
├── vite.config.js                   # Configuración Vite
├── index.html                       # HTML principal
├── src/
│   ├── main.jsx                     # Punto de entrada React
│   ├── App.jsx                      # Rutas y layout global
│   ├── index.css                    # Estilos globales
│   ├── assets/                      # Imágenes y recursos estáticos
│   ├── components/                  # Componentes reutilizables (UI)
│   │   ├── NavBar.jsx
│   │   ├── SideBar.jsx
│   │   ├── DataTable.jsx
│   │   ├── Modal.jsx
│   │   ├── QRViewer.jsx
│   │   └── ...
│   ├── pages/                       # Páginas principales
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── PanelAdminPage.jsx
│   │   ├── RegisterSchoolPage.jsx
│   │   ├── SignUpPage.jsx
│   │   └── Attendance/              # Páginas relacionadas a asistencia
│   │       ├── AttendanceList.jsx
│   │       ├── AttendanceSession.jsx
│   │       ├── QRScanner.jsx
│   │       └── StudentQRCodeManager.jsx
│   ├── secure/                      # Protecciones y rutas privadas
│   │   └── ProtectedRoute.jsx
│   └── utils/                       # Utilidades (API client, helpers)
│       ├── getServer.js             # URL base para llamadas al backend
│       └── api.js                   # cliente axios/fetch centralizado
└── public/                          # Archivos estáticos públicos

Flujos UI recomendados

- AttendanceList: muestra sesiones creadas, estado (OPEN/CLOSED) y botón para entrar a la sesión.
- AttendanceSession: detalle de los estudiantes matriculados, columnas (nombre, código QR, estado, llegada, acciones)
  - Acciones: marcar presente/manual, abrir modal de escaneo QR, exportar reporte PDF/CSV
- QRScanner: componente/modal que puede:
  - Recibir códigos desde pistola lectora (entrada de texto/POST automático si la pistola emula teclado)
  - Usar la cámara (WebRTC) para leer QR en el navegador (opcional)
- StudentQRCodeManager: generar/regenerar QR por estudiante y descargar imagen / imprimir

Componentes y responsabilidades

- `components/DataTable.jsx`: tabla genérica con paginación y acciones por fila.
- `components/QRViewer.jsx`: muestra el código QR (imagen) y botones para descargar/imprimir.
- `components/Modal.jsx`: modal reutilizable para confirmaciones y formularios.
- `pages/Attendance/*`: páginas que gestionan los flujos y llamadas al backend.

Integración con backend — Endpoints claves

- Sessions
  - GET  /api/attendance-sessions/
  - POST /api/attendance-sessions/
  - POST /api/attendance-sessions/{id}/bulk-attendance/

- Scan
  - POST /api/attendance/qr-scan/  -> usado por pistola y por frontend (cámara)

- QR Codes
  - POST /api/student-qr-codes/
  - POST /api/student-qr-codes/bulk-generate/

Modos de escaneo y recomendaciones

- Pistola lectora (hardware): muchas pistolas envían el código como si fuera teclado seguido de "Enter". Opciones:
  1) Si la pistola está conectada al equipo donde corre el frontend: escuchar foco en un input oculto que capture la cadena y haga POST al endpoint `/api/attendance/qr-scan/`.
  2) Si la pistola envía los escaneos a un dispositivo intermedio (servidor/PLC), ese dispositivo debe reenviarlos al endpoint POST con autorización.

- Cámara (opcional): usar librería JS de QR reading (p. ej. `jsqr`, `qr-scanner`) dentro de `QRScanner.jsx`.

Autenticación y UX

- Usar `ProtectedRoute` para proteger páginas.
- Mostrar feedback inmediato tras escaneo (toast con resultado: PRESENCE recorded / EXPIRED / NOT_FOUND).

Comandos y pruebas (frontend)

```powershell
# instalar dependencias
npm install
# desarrollo
npm run dev
# probar flujo con autenticación y una sesión creada
```

Pruebas con pistola (recomendación rápida)

1. Abrir `AttendanceSession` en el frontend y enfocar el input oculto para recibir el código.
2. Escanear con la pistola; validar que frontend capture el código y haga POST a `/api/attendance/qr-scan/`.
3. Alternativa: usar `curl` desde otra máquina para simular el POST al backend (ver ejemplo en `backend/estructura_b.md`).

Siguientes pasos sugeridos

1. Crear las páginas `Attendance` y `QRScanner` básicas (puedo generar plantillas React listas para pegar).
2. Implementar el cliente API (`src/utils/api.js`) con axios y manejar tokens.
3. Probar integración con backend y registrar casos de error para mejorar mensajes UX.

Si quieres, genero los componentes React (plantillas) y el cliente API listos para pegar en `frontend/src/`.
````