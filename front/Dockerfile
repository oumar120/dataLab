# Build Angular
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install --no-audit --no-fund; fi

COPY . ./
RUN npm run build

# Serve with nginx
FROM nginx:1.27-alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Angular build output (Angular CLI default for this project is dist/front)
COPY --from=build /app/dist/front /usr/share/nginx/html

EXPOSE 80
