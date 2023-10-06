import { initializeApp } from 'firebase/app'
import { ref as dbRef } from 'firebase/database'
import { getDatabase } from 'firebase/database';
import { getAuth } from 'firebase/auth';


const firebaseApp = initializeApp({
  apiKey: import.meta.env.VITE_apiKey,
  authDomain: import.meta.env.VITE_authDomain,
  databaseURL: import.meta.env.VITE_databaseURL,
  projectId: import.meta.env.VITE_projectId,
  storageBucket: import.meta.env.VITE_storageBucket,
  messagingSenderId: import.meta.env.VITE_messagingSenderId,
  appId: import.meta.env.VITE_appId,
  measurementId: import.meta.env.VITE_measurementId,
});

const db = getDatabase(firebaseApp)
const auth = getAuth(firebaseApp);

export default firebaseApp;
export { auth, db };
export const todosRef = dbRef(db, 'todos');

