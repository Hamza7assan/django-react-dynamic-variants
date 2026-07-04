# Use a lightweight Node.js image
FROM node:22-alpine
# Set the working directory inside the container
WORKDIR /app

# Copy package files and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the project files
COPY . .

# Expose the port 5173 (Vite's default port)
EXPOSE 5173

# Run the development server with host access allowed
CMD ["npm", "run", "dev", "--", "--host"]