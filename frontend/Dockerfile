# node 24 ships npm 11, which matches the npm that generated package-lock.json.
# npm 10 (node 22) rejects this lock with EUSAGE on optional native deps.
FROM node:24-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

# Vite inlines VITE_* at build time, so the API URL must arrive as a build arg.
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ARG VITE_WS_BASE_URL=ws://localhost:8000
ARG VITE_APP_NAME="Dictation Web"
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_WS_BASE_URL=$VITE_WS_BASE_URL \
    VITE_APP_NAME=$VITE_APP_NAME

COPY . .
RUN npm run build

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
