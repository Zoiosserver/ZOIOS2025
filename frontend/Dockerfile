# Multi-stage build for production optimization
FROM node:20-alpine AS base

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Development stage
FROM base AS development
EXPOSE 3000
CMD ["yarn", "start"]

# Build stage
FROM base AS build
RUN yarn build

# Production stage
FROM nginx:alpine AS production
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]