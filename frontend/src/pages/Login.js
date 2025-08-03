import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Eye, EyeOff, User, Lock, Mail, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

import { useAuth } from '../hooks/useAuth';

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const { login, register, loginMutation, registerMutation } = useAuth();
  const navigate = useNavigate();

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm();

  const onSubmit = async (data) => {
    try {
      if (isRegistering) {
        await register(data);
        setIsRegistering(false);
        toast.success('Compte créé avec succès. Vous pouvez maintenant vous connecter.');
      } else {
        await login(data);
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const isLoading = loginMutation.isLoading || registerMutation.isLoading;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
            <div className="text-2xl">🏥</div>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isRegistering ? 'Créer un compte' : 'Se connecter'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {isRegistering ? (
              <>
                Ou{' '}
                <button
                  type="button"
                  onClick={() => setIsRegistering(false)}
                  className="font-medium text-primary-600 hover:text-primary-500"
                >
                  se connecter à un compte existant
                </button>
              </>
            ) : (
              <>
                Ou{' '}
                <button
                  type="button"
                  onClick={() => setIsRegistering(true)}
                  className="font-medium text-primary-600 hover:text-primary-500"
                >
                  créer un nouveau compte
                </button>
              </>
            )}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            {isRegistering && (
              <>
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                    Nom d'utilisateur
                  </label>
                  <div className="mt-1 relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <User className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="username"
                      type="text"
                      {...registerField('username', {
                        required: 'Le nom d\'utilisateur est requis',
                        minLength: {
                          value: 3,
                          message: 'Le nom d\'utilisateur doit contenir au moins 3 caractères',
                        },
                      })}
                      className="input pl-10"
                      placeholder="Nom d'utilisateur"
                    />
                  </div>
                  {errors.username && (
                    <p className="mt-1 text-sm text-error-600">{errors.username.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <div className="mt-1 relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="email"
                      type="email"
                      {...registerField('email', {
                        required: 'L\'email est requis',
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: 'Adresse email invalide',
                        },
                      })}
                      className="input pl-10"
                      placeholder="email@exemple.com"
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1 text-sm text-error-600">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                    Rôle
                  </label>
                  <div className="mt-1 relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Shield className="h-5 w-5 text-gray-400" />
                    </div>
                    <select
                      id="role"
                      {...registerField('role', {
                        required: 'Le rôle est requis',
                      })}
                      className="select pl-10"
                    >
                      <option value="practitioner">Praticien</option>
                      <option value="admin">Administrateur</option>
                    </select>
                  </div>
                  {errors.role && (
                    <p className="mt-1 text-sm text-error-600">{errors.role.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="wallet_address" className="block text-sm font-medium text-gray-700">
                    Adresse Wallet (optionnel)
                  </label>
                  <div className="mt-1">
                    <input
                      id="wallet_address"
                      type="text"
                      {...registerField('wallet_address')}
                      className="input"
                      placeholder="0x..."
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <label htmlFor="loginUsername" className="block text-sm font-medium text-gray-700">
                {isRegistering ? 'Nom d\'utilisateur' : 'Nom d\'utilisateur'}
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="loginUsername"
                  type="text"
                  {...registerField('username', {
                    required: 'Le nom d\'utilisateur est requis',
                  })}
                  className="input pl-10"
                  placeholder="Nom d'utilisateur"
                />
              </div>
              {errors.username && (
                <p className="mt-1 text-sm text-error-600">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Mot de passe
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  {...registerField('password', {
                    required: 'Le mot de passe est requis',
                    minLength: {
                      value: 6,
                      message: 'Le mot de passe doit contenir au moins 6 caractères',
                    },
                  })}
                  className="input pl-10 pr-10"
                  placeholder="Mot de passe"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-error-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <span>{isRegistering ? 'Créer le compte' : 'Se connecter'}</span>
              )}
            </button>
          </div>

          <div className="text-center">
            <p className="text-xs text-gray-500">
              {isRegistering
                ? 'En créant un compte, vous acceptez nos conditions d\'utilisation.'
                : 'Application de radiologie interventionnelle avec traçabilité blockchain'}
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;