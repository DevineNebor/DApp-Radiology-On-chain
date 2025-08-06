import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { 
  Plus, 
  History, 
  FileText, 
  Users, 
  Activity, 
  TrendingUp,
  Calendar,
  Clock
} from 'lucide-react';
import axios from 'axios';

import { useAuth } from '../hooks/useAuth';
import { API_ENDPOINTS } from '../utils/config';

const Dashboard = () => {
  const { user } = useAuth();

  // Récupérer les statistiques
  const { data: stats, isLoading: statsLoading } = useQuery(
    'procedureStats',
    async () => {
      const response = await axios.get(API_ENDPOINTS.procedures.stats);
      return response.data;
    },
    {
      refetchInterval: 30000, // Rafraîchir toutes les 30 secondes
    }
  );

  // Récupérer les derniers actes
  const { data: recentProcedures, isLoading: proceduresLoading } = useQuery(
    'recentProcedures',
    async () => {
      const response = await axios.get(`${API_ENDPOINTS.procedures.list}?limit=5`);
      return response.data;
    }
  );

  const quickActions = [
    {
      title: 'Nouvel acte',
      description: 'Enregistrer un nouvel acte de radiologie interventionnelle',
      icon: Plus,
      href: '/procedure/new',
      color: 'bg-primary-500',
    },
    {
      title: 'Historique',
      description: 'Consulter l\'historique des actes',
      icon: History,
      href: '/procedure/history',
      color: 'bg-secondary-500',
    },
    {
      title: 'FHIR Viewer',
      description: 'Générer et visualiser les ressources FHIR',
      icon: FileText,
      href: '/fhir',
      color: 'bg-success-500',
    },
  ];

  const StatCard = ({ title, value, icon: Icon, color, change }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">
            {value || 0}
          </p>
          {change && (
            <p className="text-sm text-success-600 flex items-center">
              <TrendingUp className="h-4 w-4 mr-1" />
              +{change}%
            </p>
          )}
        </div>
      </div>
    </div>
  );

  const QuickActionCard = ({ title, description, icon: Icon, href, color }) => (
    <Link
      to={href}
      className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow duration-200"
    >
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>
    </Link>
  );

  const RecentProcedureCard = ({ procedure }) => (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-medium text-gray-900">
            Acte #{procedure.id}
          </h4>
          <p className="text-sm text-gray-600">
            {procedure.procedure_type}
          </p>
          <p className="text-xs text-gray-500">
            Patient: {procedure.patient_hash.substring(0, 8)}...
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">
            {new Date(procedure.created_at).toLocaleDateString('fr-FR')}
          </p>
          <p className="text-xs text-gray-500">
            {procedure.duration} min
          </p>
        </div>
      </div>
    </div>
  );

  if (statsLoading || proceduresLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Tableau de bord
        </h1>
        <p className="text-gray-600">
          Bienvenue, {user?.username}. Voici un aperçu de vos activités.
        </p>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total des actes"
          value={stats?.total_procedures}
          icon={Activity}
          color="bg-primary-500"
        />
        <StatCard
          title="Mes actes"
          value={stats?.user_procedures}
          icon={Users}
          color="bg-secondary-500"
        />
        <StatCard
          title="Patients uniques"
          value={stats?.unique_patients}
          icon={Users}
          color="bg-success-500"
        />
        <StatCard
          title="Aujourd'hui"
          value={0} // À implémenter
          icon={Calendar}
          color="bg-warning-500"
        />
      </div>

      {/* Actions rapides */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Actions rapides
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action) => (
            <QuickActionCard key={action.title} {...action} />
          ))}
        </div>
      </div>

      {/* Derniers actes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Derniers actes
          </h2>
          <div className="space-y-4">
            {recentProcedures?.length > 0 ? (
              recentProcedures.map((procedure) => (
                <RecentProcedureCard key={procedure.id} procedure={procedure} />
              ))
            ) : (
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Aucun acte enregistré</p>
                <Link
                  to="/procedure/new"
                  className="inline-flex items-center mt-2 text-primary-600 hover:text-primary-500"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Créer le premier acte
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Types d'interventions */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Types d'interventions
          </h2>
          <div className="bg-white rounded-lg shadow p-6">
            {stats?.procedure_types ? (
              <div className="space-y-3">
                {Object.entries(stats.procedure_types).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {type}
                    </span>
                    <span className="text-sm text-gray-500">
                      {count} acte{count > 1 ? 's' : ''}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-center">Aucune donnée disponible</p>
            )}
          </div>
        </div>
      </div>

      {/* Informations système */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Informations système
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Rôle</p>
            <p className="font-medium text-gray-900 capitalize">{user?.role}</p>
          </div>
          <div>
            <p className="text-gray-600">Email</p>
            <p className="font-medium text-gray-900">{user?.email}</p>
          </div>
          <div>
            <p className="text-gray-600">Membre depuis</p>
            <p className="font-medium text-gray-900">
              {new Date(user?.created_at).toLocaleDateString('fr-FR')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;