import { useEffect, useState } from 'react';

export default function BarcodeScanner({ onResult }) {
  const [buffer, setBuffer] = useState('');

  useEffect(() => {
    const handleKey = e => {
      // Lector finaliza con Enter o Tab
      if (e.key === 'Enter' || e.key === 'Tab') {
        const code = buffer.trim();
        if (code) onResult?.(code);
        setBuffer('');
      } else if (e.key.length === 1) {
        setBuffer(prev => prev + e.key);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [buffer, onResult]);

  return (
    <div className="p-4 border rounded text-gray-700 text-sm">
      Conecte el lector <b>ZKT USB</b> y escanee el código.  
      Al presionar <b>Enter</b> o <b>Tab</b> el sistema registrará la asistencia.
    </div>
  );
}
