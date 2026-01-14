# Build Angular
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install --no-audit --no-fund; fi

COPY . ./
RUN npm run build

# Normalize Angular output for nginx (Angular application builder often outputs dist/<app>/browser)
RUN mkdir -p /tmp/nginx-html \
	&& if [ -d "/app/dist/front/browser" ]; then cp -a /app/dist/front/browser/. /tmp/nginx-html/; \
	elif [ -d "/app/dist/front" ]; then cp -a /app/dist/front/. /tmp/nginx-html/; \
	else echo "ERROR: Angular build output not found" && ls -la /app/dist && exit 1; fi

# Serve with nginx
FROM nginx:1.27-alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Angular build output (Angular CLI default for this project is dist/front)
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /tmp/nginx-html /usr/share/nginx/html

EXPOSE 80
