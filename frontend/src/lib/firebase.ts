/**
 * Firebase Configuration
 * =======================
 * Initialized with your actual Firebase project config.
 */

import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyBWQ8kDLrJNpyeafiIA3SVWQhplZjOT_iU",
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "smart-agri-f2ccd.firebaseapp.com",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "smart-agri-f2ccd",
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "smart-agri-f2ccd.firebasestorage.app",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "1023136360620",
    appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:1023136360620:web:b6c5bbd62f29b7bf131709",
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-7HYFQJNHMF",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;
