# Use the official Node.js image as a parent image
FROM node:22

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the app
RUN npm run build

# Install serve to serve the build
RUN npm install -g serve

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Serve the app
CMD ["npm", "run", "start"]