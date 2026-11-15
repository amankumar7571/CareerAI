# CareerAI frontend — React 19 + Vite, multi-stage build.
# Build from the repo root:  docker build -t careerai-frontend --build-arg VITE_API_BASE_URL=http://localhost:8000 ./frontend
# Or with Compose (recommended):  docker compose up --build
#
# VITE_API_BASE_URL is baked into the static bundle at BUILD time, so the
# deployed backend URL must be passed as a build arg (see docker-compose.yml).
# For local dev the default below points at the Compose backend on :8000.
FROM node:20-alpine AS build

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime: nginx serving the static bundle, with an SPA fallback so
# react-router routes (/login, /register, /dashboard) resolve to index.html.
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
