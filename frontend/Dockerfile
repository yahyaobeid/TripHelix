# Use Node.js 18 Alpine image as base
# Alpine is a lightweight Linux distribution
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first to leverage Docker cache
# This way, if dependencies don't change, we don't need to reinstall them
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Next.js application
# This creates an optimized production build
RUN npm run build

# Expose the port the application will run on
EXPOSE 3000

# Command to run the application
# This starts the production server
CMD ["npm", "start"] 