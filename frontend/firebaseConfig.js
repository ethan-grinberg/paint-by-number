// Import the functions you need from the SDKs you need

import { initializeApp } from "firebase/app";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyAirRHf4hv-GPC98NaShaeDSGyzuG4rcsw",
  authDomain: "paint-by-number-21987.firebaseapp.com",
  projectId: "paint-by-number-21987",
  storageBucket: "paint-by-number-21987.appspot.com",
  messagingSenderId: "80512782339",
  appId: "1:80512782339:web:338d25014baed9536d7e36",
  measurementId: "G-3WNNQ5VT0P",
};

// Initialize Firebase

const app = initializeApp(firebaseConfig);
const storage = getStorage(app);

export { storage as default };
