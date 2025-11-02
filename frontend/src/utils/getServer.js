// src/utils/getServer.js - AGREGAR ESTAS FUNCIONES
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
      }
    },

    // NUEVAS FUNCIONES PARA CICLO 3
    getTeachers: async function () {
      try {
        const response = await fetch('api/teachers', {
          credentials: 'include',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          },
        });
        if (!response.ok) throw new Error('Error al cargar docentes');
        return await response.json();
      } catch (error) {
        console.error(error);
        throw error;
      }
    },

    getScores: async function (filters = {}) {
      try {
        const queryParams = new URLSearchParams(filters).toString();
        const response = await fetch(`api/scores?${queryParams}`, {
          credentials: 'include',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          },
        });
        if (!response.ok) throw new Error('Error al cargar calificaciones');
        return await response.json();
      } catch (error) {
        console.error(error);
        throw error;
      }
    },

    getRoles: async function () {
      try {
        const response = await fetch('api/roles', {
          credentials: 'include',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          },
        });
        if (!response.ok) throw new Error('Error al cargar roles');
        return await response.json();
      } catch (error) {
        console.error(error);
        throw error;
      }
    },
  };
}