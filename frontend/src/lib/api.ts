/**
 * Smart Agriculture – API Service
 * =================================
 * Centralized API client for communicating with the Django backend.
 * All /api calls are proxied to http://127.0.0.1:8000 via Vite config.
 * Auth tokens are automatically included when available.
 */

import { auth } from '@/lib/firebase';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

// ──────────────────────────────────────────
// Get current user's Firebase ID token
// ──────────────────────────────────────────

async function getAuthToken(): Promise<string | null> {
    const user = auth.currentUser;
    if (!user) return null;
    try {
        return await user.getIdToken();
    } catch {
        return null;
    }
}

// ──────────────────────────────────────────
// Generic fetch wrapper with auto-auth
// ──────────────────────────────────────────

export async function apiFetch<T>(
    endpoint: string,
    options: RequestInit = {},
    includeAuth = true
): Promise<T> {
    const url = `${API_BASE}${endpoint}`;

    const headers: Record<string, string> = {};

    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    // Include auth token if available
    if (includeAuth) {
        const token = await getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    const res = await fetch(url, {
        ...options,
        headers: {
            ...headers,
            ...(options.headers as Record<string, string>),
        },
    });

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.error || data.detail || `API Error ${res.status}`);
    }

    return data as T;
}

// ──────────────────────────────────────────
// Disease Detection API
// ──────────────────────────────────────────

export interface DiseaseResult {
    success: boolean;
    disease_name: string;
    confidence: number;
    is_healthy: boolean;
}

export interface RecommendationResult {
    success: boolean;
    disease_name: string;
    fertilizers: string[];
    pesticides: string[];
    organic_treatments: string[];
    preventive_measures: string[];
}

export interface DiseaseHistoryItem {
    id: string;
    disease_name: string;
    confidence: number;
    is_healthy: boolean;
    raw_label: string;
    filename: string;
    image_url?: string;
    created_at: string;
}

/**
 * Upload a leaf image and get disease prediction from the AI model.
 */
export async function predictDisease(imageFile: File, crop?: string): Promise<DiseaseResult> {
    const formData = new FormData();
    formData.append('image', imageFile);

    if (crop) {
        formData.append('crop', crop);
    }

    return apiFetch<DiseaseResult>('/disease/predict/', {
        method: 'POST',
        body: formData,
    });
}

/**
 * Get disease prediction history for the current user.
 */
export async function getDiseaseHistory(): Promise<{ success: boolean; data: DiseaseHistoryItem[] }> {
    return apiFetch('/disease/history/');
}

/**
 * Get treatment recommendations for a detected disease.
 */
export async function getRecommendation(diseaseName: string, lang: string = 'en'): Promise<RecommendationResult> {
    const encoded = encodeURIComponent(diseaseName);
    return apiFetch<RecommendationResult>(`/recommendation/?disease_name=${encoded}&lang=${lang}`);
}

/**
 * Get list of all diseases the system can detect.
 */
export async function getAvailableDiseases(): Promise<{ diseases: string[]; count: number }> {
    return apiFetch('/recommendation/diseases/', {}, false);
}

// ──────────────────────────────────────────
// Yield Prediction API
// ──────────────────────────────────────────

export interface YieldInput {
    district: string;
    soil_type: string;
    crop: string;
    rainfall: number;
    temperature: number;
}

export interface YieldResult {
    success: boolean;
    predicted_yield: number;
    unit: string;
    risk_level: string;
}

export interface YieldHistoryItem {
    id: string;
    district: string;
    soil_type: string;
    crop: string;
    rainfall: number;
    temperature: number;
    predicted_yield: number;
    unit: string;
    risk_level: string;
    created_at: string;
}

/**
 * Submit crop parameters and get yield prediction.
 */
export async function predictYield(input: YieldInput): Promise<YieldResult> {
    return apiFetch<YieldResult>('/yield/predict/', {
        method: 'POST',
        body: JSON.stringify(input),
    });
}

/**
 * Get yield prediction history for the current user.
 */
export async function getYieldHistory(): Promise<{ success: boolean; data: YieldHistoryItem[] }> {
    return apiFetch('/yield/history/');
}

// ──────────────────────────────────────────
// Health Check
// ──────────────────────────────────────────

export async function healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const res = await fetch('/');
    return res.json();
}
