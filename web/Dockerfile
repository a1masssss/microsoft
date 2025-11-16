FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

RUN npm install

# Copy source files
COPY . .

# Build the application with increased memory
ENV NODE_OPTIONS="--max-old-space-size=1536"
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Create directory for certbot webroot
RUN mkdir -p /var/www/certbot

# Copy nginx configuration (direct copy, no template substitution needed)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]