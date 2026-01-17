# Development stage - for docker-compose
FROM node:22-alpine AS development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Default port for dev
EXPOSE 5173

# Dev command (can be overridden by docker-compose)
CMD ["npm", "run", "dev", "--", "--host"]

# Build stage - for production builds
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Accept build-time environment variables
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy source code
COPY . .

# Build the application (this might fail with TypeScript errors)
RUN npm run build

# Production stage - serve with simple server
FROM node:22-alpine AS production

WORKDIR /app

# Install a simple static file server
RUN npm install -g serve

# Copy built assets from builder stage
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 8080

# Start server on Railway's PORT
CMD serve -s dist -l ${PORT:-8080}