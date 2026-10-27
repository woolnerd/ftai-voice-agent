FROM node:24.22.1-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@10.34.9

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Build the application
RUN pnpm build

# Expose port
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]
