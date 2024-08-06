# Use the official Nginx image as the base image
FROM nginx:stable-perl

# Copy the Nginx configuration file into the container
COPY NGINX/nginx.conf /etc/nginx/nginx.conf

# Copy the static website files into the container
COPY NGINX/Pages/index.html /usr/share/nginx/html

# Expose the port that Nginx will run on
EXPOSE 8002

