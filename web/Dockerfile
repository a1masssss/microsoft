FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./


RUN npm install

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install certbot for SSL certificate management
RUN apk add certbot certbot-nginx

COPY --from=builder /app/dist /usr/share/nginx/html

RUN mkdir -p /var/www/certbot


COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80 443

CMD ["/bin/sh", "-c", "envsubst '$$DOMAIN_NAME' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]