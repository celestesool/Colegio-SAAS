/* eslint-disable prettier/prettier */
import Cargar from './../components/document/Cargar';
import { Extraer } from '../components/document/Extraer';
import { SubirExcel } from '../components/document/SubirExcel';
import styles from './Document.module.css'; 

export function Document() {
  return (
    <div className={styles.documentContainer}>
      <h1 className={styles.title}>Gestión de Documentos</h1>
      <div className={styles.documentGrid}>
        <div className={styles.documentCard}>
          <h2>Cargar Documento</h2>
          <Cargar />
        </div>
        <div className={styles.documentCard}>
          <h2>Extraer Datos</h2>
          <Extraer />
        </div>
        <div className={styles.documentCard}>
          <h2>Subir Excel</h2>
          <SubirExcel />
        </div>
      </div>
    </div>
  );
}
