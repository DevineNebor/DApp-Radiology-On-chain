import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';

// Composants
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProcedureForm from './pages/ProcedureForm';
import ProcedureHistory from './pages/ProcedureHistory';
import FHIRViewer from './pages/FHIRViewer';
import BlockchainStatus from './components/BlockchainStatus';

// Hooks
import { useAuth } from './hooks/useAuth';

// Utilitaires
import { API_BASE_URL } from './utils/config';

function App() {
  const { user, isAuthenticated, isLoading } = useAuth();

  // Vérifier la santé de l'API
  const { data: apiHealth, isLoading: healthLoading } = useQuery(
    'apiHealth',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    },
    {
      refetchInterval: 30000, // Vérifier toutes les 30 secondes
      retry: 3,
      retryDelay: 1000,
    }
  );

  if (isLoading || healthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement de l'application...</p>
        </div>
      </div>
    );
  }

  // Si l'API n'est pas disponible
  if (!apiHealth || apiHealth.status !== 'healthy') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-6xl mb-4">🏥</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Radiology DApp
          </h1>
          <p className="text-gray-600 mb-4">
            Application de radiologie interventionnelle
          </p>
          <div className="bg-error-50 border border-error-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-error-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-error-800">
                  API non disponible
                </h3>
                <p className="text-sm text-error-700 mt-1">
                  L'API backend n'est pas accessible. Veuillez vérifier que le serveur est démarré.
                </p>
              </div>
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-500">
            <p>URL de l'API: {API_BASE_URL}</p>
            <p>Status: {apiHealth?.status || 'inconnu'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <BlockchainStatus />
      
      {!isAuthenticated ? (
        <Login />
      ) : (
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/procedure/new" element={<ProcedureForm />} />
            <Route path="/procedure/history" element={<ProcedureHistory />} />
            <Route path="/fhir" element={<FHIRViewer />} />
            <Route path="/fhir/:resourceId" element={<FHIRViewer />} />
          </Routes>
        </Layout>
      )}
    </div>
  );
}

export default App;