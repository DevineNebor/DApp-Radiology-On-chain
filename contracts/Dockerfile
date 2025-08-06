FROM node:18-alpine

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apk add --no-cache git

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le code source
COPY . .

# Exposer le port Hardhat
EXPOSE 8545

# Commande par défaut
CMD ["npx", "hardhat", "node", "--hostname", "0.0.0.0"]