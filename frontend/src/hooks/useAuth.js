import { useState, useEffect, createContext, useContext } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

import { API_ENDPOINTS, SECURITY_CONFIG, SUCCESS_MESSAGES, ERROR_MESSAGES } from '../utils/config';

// Configuration axios avec intercepteur pour le token
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Intercepteur pour ajouter le token aux requêtes
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(SECURITY_CONFIG.tokenKey);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs d'authentification
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(SECURITY_CONFIG.tokenKey);
      localStorage.removeItem(SECURITY_CONFIG.refreshTokenKey);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Contexte d'authentification
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  // Vérifier l'utilisateur actuel
  const { data: currentUser, isLoading: userLoading } = useQuery(
    'currentUser',
    async () => {
      const token = localStorage.getItem(SECURITY_CONFIG.tokenKey);
      if (!token) {
        throw new Error('Aucun token trouvé');
      }
      
      const response = await axios.get(API_ENDPOINTS.auth.me);
      return response.data;
    },
    {
      retry: false,
      enabled: !!localStorage.getItem(SECURITY_CONFIG.tokenKey),
      onSuccess: (data) => {
        setUser(data);
        setIsAuthenticated(true);
      },
      onError: () => {
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem(SECURITY_CONFIG.tokenKey);
        localStorage.removeItem(SECURITY_CONFIG.refreshTokenKey);
      },
    }
  );

  // Mutation de connexion
  const loginMutation = useMutation(
    async (credentials) => {
      const response = await axios.post(API_ENDPOINTS.auth.login, credentials);
      return response.data;
    },
    {
      onSuccess: (data) => {
        localStorage.setItem(SECURITY_CONFIG.tokenKey, data.access_token);
        setUser(data.user);
        setIsAuthenticated(true);
        toast.success(SUCCESS_MESSAGES.LOGIN_SUCCESS);
        queryClient.invalidateQueries('currentUser');
      },
      onError: (error) => {
        const message = error.response?.data?.detail || ERROR_MESSAGES.AUTH_ERROR;
        toast.error(message);
      },
    }
  );

  // Mutation d'inscription
  const registerMutation = useMutation(
    async (userData) => {
      const response = await axios.post(API_ENDPOINTS.auth.register, userData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success('Compte créé avec succès. Vous pouvez maintenant vous connecter.');
      },
      onError: (error) => {
        const message = error.response?.data?.detail || 'Erreur lors de l\'inscription';
        toast.error(message);
      },
    }
  );

  // Fonction de déconnexion
  const logout = () => {
    localStorage.removeItem(SECURITY_CONFIG.tokenKey);
    localStorage.removeItem(SECURITY_CONFIG.refreshTokenKey);
    setUser(null);
    setIsAuthenticated(false);
    queryClient.clear();
    toast.success(SUCCESS_MESSAGES.LOGOUT_SUCCESS);
  };

  // Fonction de connexion
  const login = (credentials) => {
    return loginMutation.mutateAsync(credentials);
  };

  // Fonction d'inscription
  const register = (userData) => {
    return registerMutation.mutateAsync(userData);
  };

  // Vérifier l'état initial de l'authentification
  useEffect(() => {
    const token = localStorage.getItem(SECURITY_CONFIG.tokenKey);
    if (token) {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  // Mettre à jour l'état de chargement
  useEffect(() => {
    setIsLoading(userLoading);
  }, [userLoading]);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
    loginMutation,
    registerMutation,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook pour vérifier les permissions
export const usePermissions = () => {
  const { user } = useAuth();
  
  const hasPermission = (permission) => {
    if (!user) return false;
    
    const userPermissions = {
      practitioner: {
        canCreateProcedures: true,
        canViewOwnProcedures: true,
        canViewPatientHistory: true,
        canUploadConsent: true,
        canGenerateFHIR: true,
      },
      admin: {
        canCreateProcedures: true,
        canViewAllProcedures: true,
        canViewPatientHistory: true,
        canUploadConsent: true,
        canGenerateFHIR: true,
        canManageUsers: true,
        canViewStats: true,
      },
    };
    
    const rolePermissions = userPermissions[user.role] || {};
    return rolePermissions[permission] || false;
  };
  
  return {
    hasPermission,
    isAdmin: user?.role === 'admin',
    isPractitioner: user?.role === 'practitioner',
  };
};

// Hook pour gérer les tokens
export const useToken = () => {
  const getToken = () => {
    return localStorage.getItem(SECURITY_CONFIG.tokenKey);
  };
  
  const setToken = (token) => {
    localStorage.setItem(SECURITY_CONFIG.tokenKey, token);
  };
  
  const removeToken = () => {
    localStorage.removeItem(SECURITY_CONFIG.tokenKey);
  };
  
  const isTokenValid = () => {
    const token = getToken();
    if (!token) return false;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiry = payload.exp * 1000; // Convertir en millisecondes
      return Date.now() < expiry;
    } catch (error) {
      return false;
    }
  };
  
  return {
    getToken,
    setToken,
    removeToken,
    isTokenValid,
  };
};