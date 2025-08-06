import React from 'react';
import { useQuery } from 'react-query';
import { Wifi, WifiOff, Clock } from 'lucide-react';
import axios from 'axios';

import { API_ENDPOINTS } from '../utils/config';

const BlockchainStatus = () => {
  const { data: blockchainStatus, isLoading } = useQuery(
    'blockchainStatus',
    async () => {
      try {
        // Vérifier la santé de l'API blockchain
        const response = await axios.get(`${API_ENDPOINTS.system.health}`);
        return {
          connected: response.data.services?.blockchain === 'connected',
          status: response.data.services?.blockchain || 'unknown',
        };
      } catch (error) {
        return {
          connected: false,
          status: 'disconnected',
          error: error.message,
        };
      }
    },
    {
      refetchInterval: 10000, // Vérifier toutes les 10 secondes
      retry: 3,
      retryDelay: 2000,
    }
  );

  const getStatusIcon = () => {
    if (isLoading) {
      return <Clock size={16} className="animate-spin" />;
    }
    
    if (blockchainStatus?.connected) {
      return <Wifi size={16} className="text-success-600" />;
    }
    
    return <WifiOff size={16} className="text-error-600" />;
  };

  const getStatusText = () => {
    if (isLoading) {
      return 'Vérification...';
    }
    
    if (blockchainStatus?.connected) {
      return 'Blockchain connectée';
    }
    
    return 'Blockchain déconnectée';
  };

  const getStatusClass = () => {
    if (isLoading) {
      return 'blockchain-status pending';
    }
    
    if (blockchainStatus?.connected) {
      return 'blockchain-status connected';
    }
    
    return 'blockchain-status disconnected';
  };

  return (
    <div className="fixed bottom-4 right-4 z-40">
      <div className={getStatusClass()}>
        {getStatusIcon()}
        <span className="text-xs font-medium">{getStatusText()}</span>
      </div>
    </div>
  );
};

export default BlockchainStatus;