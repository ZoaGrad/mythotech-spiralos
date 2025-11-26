FROM node:20-alpine
WORKDIR /app
COPY swps/package.json ./package.json
RUN npm install --production
COPY swps ./
ENV NODE_ENV=production
CMD ["node", "api/server.js"]
