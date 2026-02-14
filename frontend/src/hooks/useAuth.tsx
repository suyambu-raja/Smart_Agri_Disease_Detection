/**
 * Auth Context – Firebase Authentication
 * ========================================
 * Provides user authentication state and methods to the entire app.
 * Supports: Email/Password sign-up, sign-in, sign-out, and Google sign-in.
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import {
    onAuthStateChanged,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut as firebaseSignOut,
    GoogleAuthProvider,
    signInWithPopup,
    updateProfile,
    sendPasswordResetEmail,
    type User,
} from 'firebase/auth';
import { auth } from '@/lib/firebase';

// ──────────────────────────────────────────
// Types
// ──────────────────────────────────────────

interface AuthContextType {
    user: User | null;
    loading: boolean;
    signIn: (email: string, password: string) => Promise<void>;
    signUp: (email: string, password: string, displayName?: string) => Promise<void>;
    signOut: () => Promise<void>;
    signInWithGoogle: () => Promise<void>;
    resetPassword: (email: string) => Promise<void>;
    getIdToken: () => Promise<string | null>;
}

// ──────────────────────────────────────────
// Context
// ──────────────────────────────────────────

const AuthContext = createContext<AuthContextType | null>(null);

// ──────────────────────────────────────────
// Provider
// ──────────────────────────────────────────

const googleProvider = new GoogleAuthProvider();

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    // Listen for auth state changes (persisted across page reloads)
    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
            setUser(firebaseUser);
            setLoading(false);
        });
        return () => unsubscribe();
    }, []);

    // ── Email/Password Sign In ──
    const signIn = async (email: string, password: string) => {
        await signInWithEmailAndPassword(auth, email, password);
    };

    // ── Email/Password Sign Up ──
    const signUp = async (email: string, password: string, displayName?: string) => {
        const cred = await createUserWithEmailAndPassword(auth, email, password);
        if (displayName) {
            await updateProfile(cred.user, { displayName });
        }
    };

    // ── Sign Out ──
    const signOut = async () => {
        await firebaseSignOut(auth);
    };

    // ── Google Sign In ──
    const signInWithGoogle = async () => {
        await signInWithPopup(auth, googleProvider);
    };

    // ── Password Reset ──
    const resetPassword = async (email: string) => {
        await sendPasswordResetEmail(auth, email);
    };

    // ── Get Firebase ID Token (for backend API calls) ──
    const getIdToken = async (): Promise<string | null> => {
        if (!user) return null;
        return user.getIdToken();
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                signIn,
                signUp,
                signOut,
                signInWithGoogle,
                resetPassword,
                getIdToken,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

// ──────────────────────────────────────────
// Hook
// ──────────────────────────────────────────

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
