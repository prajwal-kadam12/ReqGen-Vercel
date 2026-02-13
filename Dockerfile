# Node.js Backend Dockerfile for Koyeb
FROM node:20-slim

# Install Chromium for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Puppeteer to use installed Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source files
COPY server ./server
COPY shared ./shared
COPY tsconfig.json ./
COPY drizzle.config.ts ./

# Build the server
RUN npm install -g esbuild && \
    esbuild server/index.ts --platform=node --packages=external --bundle --format=esm --outdir=dist

# Expose port
EXPOSE 8080

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8080

# Start the server
CMD ["node", "dist/index.js"]
