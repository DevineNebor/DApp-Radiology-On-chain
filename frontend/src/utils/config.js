// Configuration de l'application
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configuration blockchain
export const BLOCKCHAIN_CONFIG = {
  networkId: process.env.REACT_APP_NETWORK_ID || '1337',
  contractAddress: process.env.REACT_APP_CONTRACT_ADDRESS || '',
  rpcUrl: process.env.REACT_APP_RPC_URL || 'http://localhost:8545',
};

// Configuration FHIR
export const FHIR_CONFIG = {
  baseUrl: process.env.REACT_APP_FHIR_BASE_URL || API_BASE_URL,
  version: 'R4',
};

// Types de procédures supportés
export const PROCEDURE_TYPES = [
  'embolisation',
  'ponction',
  'stent',
  'angioplastie',
  'biopsie',
  'drainage',
  'ablation',
  'radiofréquence',
  'cryothérapie',
  'chimioembolisation'
];

// Configuration des notifications
export const NOTIFICATION_CONFIG = {
  position: 'top-right',
  duration: 4000,
};

// Configuration de l'interface
export const UI_CONFIG = {
  theme: 'light',
  language: 'fr',
  dateFormat: 'DD/MM/YYYY',
  timeFormat: 'HH:mm',
};

// Configuration de sécurité
export const SECURITY_CONFIG = {
  tokenKey: 'radiology_dapp_token',
  refreshTokenKey: 'radiology_dapp_refresh_token',
  tokenExpiry: 30 * 60 * 1000, // 30 minutes
};

// Configuration des fichiers
export const FILE_CONFIG = {
  maxSize: 10 * 1024 * 1024, // 10MB
  allowedTypes: ['application/pdf', 'image/jpeg', 'image/png'],
  uploadPath: '/api/procedures/upload-consent',
};

// Configuration des endpoints API
export const API_ENDPOINTS = {
  // Authentification
  auth: {
    login: '/api/auth/login-json',
    register: '/api/auth/register',
    me: '/api/auth/me',
  },
  
  // Procédures
  procedures: {
    list: '/api/procedures',
    create: '/api/procedures',
    get: (id) => `/api/procedures/${id}`,
    update: (id) => `/api/procedures/${id}`,
    delete: (id) => `/api/procedures/${id}`,
    history: '/api/procedures/patient',
    stats: '/api/procedures/stats/summary',
    types: '/api/procedures/types',
    uploadConsent: '/api/procedures/upload-consent',
  },
  
  // Patients
  patients: {
    list: '/api/procedures/patients',
    create: '/api/procedures/patients',
    get: (hash) => `/api/procedures/patients/${hash}`,
    history: (hash) => `/api/procedures/patient/${hash}/history`,
  },
  
  // FHIR
  fhir: {
    claim: (id) => `/api/fhir/claim/${id}`,
    patient: (hash) => `/api/fhir/patient/${hash}`,
    practitioner: (id) => `/api/fhir/practitioner/${id}`,
    bundle: (hash) => `/api/fhir/patient/${hash}/bundle`,
    resources: '/api/fhir/resources',
    resource: (id) => `/api/fhir/resources/${id}`,
    validate: '/api/fhir/validate',
    stats: '/api/fhir/stats',
  },
  
  // Blockchain
  blockchain: {
    procedure: (id) => `/api/procedures/blockchain/${id}`,
    patientProcedures: (hash) => `/api/procedures/blockchain/patient/${hash}`,
  },
  
  // Système
  system: {
    health: '/health',
    info: '/api/info',
  },
};

// Configuration des messages d'erreur
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Erreur de connexion réseau',
  API_ERROR: 'Erreur de l\'API',
  AUTH_ERROR: 'Erreur d\'authentification',
  VALIDATION_ERROR: 'Erreur de validation',
  BLOCKCHAIN_ERROR: 'Erreur blockchain',
  FILE_UPLOAD_ERROR: 'Erreur lors de l\'upload du fichier',
  UNKNOWN_ERROR: 'Erreur inconnue',
};

// Configuration des messages de succès
export const SUCCESS_MESSAGES = {
  PROCEDURE_CREATED: 'Acte créé avec succès',
  PROCEDURE_UPDATED: 'Acte mis à jour avec succès',
  PROCEDURE_DELETED: 'Acte supprimé avec succès',
  CONSENT_UPLOADED: 'Consentement uploadé avec succès',
  FHIR_GENERATED: 'Ressource FHIR générée avec succès',
  LOGIN_SUCCESS: 'Connexion réussie',
  LOGOUT_SUCCESS: 'Déconnexion réussie',
};

// Configuration des validations
export const VALIDATION_RULES = {
  patientHash: {
    required: true,
    minLength: 64,
    maxLength: 64,
    pattern: /^[a-fA-F0-9]{64}$/,
  },
  procedureType: {
    required: true,
    allowedValues: PROCEDURE_TYPES,
  },
  duration: {
    required: true,
    min: 1,
    max: 1440, // 24 heures en minutes
  },
  consentHash: {
    required: true,
    minLength: 64,
    maxLength: 64,
    pattern: /^[a-fA-F0-9]{64}$/,
  },
};

// Configuration des permissions
export const PERMISSIONS = {
  PRACTITIONER: {
    canCreateProcedures: true,
    canViewOwnProcedures: true,
    canViewPatientHistory: true,
    canUploadConsent: true,
    canGenerateFHIR: true,
  },
  ADMIN: {
    canCreateProcedures: true,
    canViewAllProcedures: true,
    canViewPatientHistory: true,
    canUploadConsent: true,
    canGenerateFHIR: true,
    canManageUsers: true,
    canViewStats: true,
  },
};