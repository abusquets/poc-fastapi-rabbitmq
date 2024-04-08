# Dockerfile

# Use an existing node alpine image as a base image.
FROM node:18-alpine

# Set the working directory.
WORKDIR /app

# Copy the package.json file.
COPY package*.json ./

# Install application dependencies.
RUN npm install

# # Copy the rest of the application files.
# COPY . .

ARG WAIT_BIN=wait

# Add wait script
ADD "https://github.com/ufoscout/docker-compose-wait/releases/download/2.12.1/${WAIT_BIN}" /wait
RUN chmod +x /wait
# wait script

# Expose the port.
EXPOSE 3000

# Run the application.
CMD ["npm", "start"]