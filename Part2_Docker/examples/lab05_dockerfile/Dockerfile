FROM nginx:1.27-alpine
LABEL description="Dockerfile lab nginx image"
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
