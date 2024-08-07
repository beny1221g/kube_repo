FROM nginx:alpine

# Copy the Nginx configuration file
COPY nginx_conf/default.conf /etc/nginx/conf.d/default.conf

# Copy the static website files
COPY Pages /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Run Nginx
CMD ["nginx", "-g", "daemon off;"]