#!/bin/bash

# Script de démarrage pour la DApp de radiologie interventionnelle
# Inspiré d'Avaneer Health

set -e

echo "🏥 Démarrage de la DApp de radiologie interventionnelle..."
echo "=================================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les prérequis
check_prerequisites() {
    print_status "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez installer Docker."
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé. Veuillez installer Docker Compose."
        exit 1
    fi
    
    # Vérifier Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js n'est pas installé. Il sera utilisé via Docker."
    fi
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 n'est pas installé. Il sera utilisé via Docker."
    fi
    
    print_success "Prérequis vérifiés"
}

# Installer les dépendances
install_dependencies() {
    print_status "Installation des dépendances..."
    
    # Installer les dépendances des smart contracts
    if [ -d "contracts" ]; then
        print_status "Installation des dépendances des smart contracts..."
        cd contracts
        if [ -f "package.json" ]; then
            npm install
        fi
        cd ..
    fi
    
    # Installer les dépendances du backend
    if [ -d "backend" ]; then
        print_status "Installation des dépendances du backend..."
        cd backend
        if [ -f "requirements.txt" ]; then
            pip3 install -r requirements.txt || print_warning "Impossible d'installer les dépendances Python localement"
        fi
        cd ..
    fi
    
    # Installer les dépendances du frontend
    if [ -d "frontend" ]; then
        print_status "Installation des dépendances du frontend..."
        cd frontend
        if [ -f "package.json" ]; then
            npm install
        fi
        cd ..
    fi
    
    print_success "Dépendances installées"
}

# Démarrer les services
start_services() {
    print_status "Démarrage des services..."
    
    # Démarrer Hardhat Network
    print_status "Démarrage du réseau blockchain Hardhat..."
    docker-compose up -d hardhat
    
    # Attendre que Hardhat soit prêt
    print_status "Attente du démarrage de Hardhat..."
    sleep 10
    
    # Déployer les smart contracts
    print_status "Déploiement des smart contracts..."
    docker-compose --profile deploy up contract-deployer
    
    # Récupérer l'adresse du contrat déployé
    if [ -f "contracts/deployment.json" ]; then
        CONTRACT_ADDRESS=$(grep -o '"contractAddress": "[^"]*"' contracts/deployment.json | cut -d'"' -f4)
        export CONTRACT_ADDRESS
        print_success "Contrat déployé à l'adresse: $CONTRACT_ADDRESS"
    else
        print_warning "Impossible de récupérer l'adresse du contrat"
    fi
    
    # Démarrer le backend
    print_status "Démarrage du backend FastAPI..."
    docker-compose up -d backend
    
    # Attendre que le backend soit prêt
    print_status "Attente du démarrage du backend..."
    sleep 5
    
    # Démarrer le frontend
    print_status "Démarrage du frontend React..."
    docker-compose up -d frontend
    
    print_success "Tous les services démarrés"
}

# Afficher les informations de connexion
show_connection_info() {
    echo ""
    echo "=================================================="
    print_success "DApp démarrée avec succès !"
    echo "=================================================="
    echo ""
    echo "🌐 Frontend React:    http://localhost:3000"
    echo "🔧 Backend FastAPI:   http://localhost:8000"
    echo "📚 Documentation API: http://localhost:8000/docs"
    echo "⛓️  Hardhat Network:  http://localhost:8545"
    echo ""
    echo "📋 Informations importantes:"
    echo "   - Créez un compte praticien pour commencer"
    echo "   - Les actes sont enregistrés sur la blockchain locale"
    echo "   - Les données FHIR sont générées automatiquement"
    echo ""
    echo "🛑 Pour arrêter: docker-compose down"
    echo "📊 Pour voir les logs: docker-compose logs -f"
    echo ""
}

# Fonction principale
main() {
    case "${1:-start}" in
        "start")
            check_prerequisites
            install_dependencies
            start_services
            show_connection_info
            ;;
        "stop")
            print_status "Arrêt des services..."
            docker-compose down
            print_success "Services arrêtés"
            ;;
        "restart")
            print_status "Redémarrage des services..."
            docker-compose down
            start_services
            show_connection_info
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "clean")
            print_status "Nettoyage des données..."
            docker-compose down -v
            docker system prune -f
            print_success "Nettoyage terminé"
            ;;
        "help")
            echo "Usage: $0 [start|stop|restart|logs|clean|help]"
            echo ""
            echo "Commandes:"
            echo "  start   - Démarrer tous les services (défaut)"
            echo "  stop    - Arrêter tous les services"
            echo "  restart - Redémarrer tous les services"
            echo "  logs    - Afficher les logs en temps réel"
            echo "  clean   - Nettoyer toutes les données"
            echo "  help    - Afficher cette aide"
            ;;
        *)
            print_error "Commande inconnue: $1"
            echo "Utilisez '$0 help' pour voir les commandes disponibles"
            exit 1
            ;;
    esac
}

# Exécuter la fonction principale
main "$@"