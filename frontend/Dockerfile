FROM node:18

WORKDIR /app

ENV PORT=5001
ENV HOST=0.0.0.0

COPY frontend/package.json ./package.json
COPY frontend/package-lock.json ./package-lock.json
RUN npm install

COPY frontend/ .

EXPOSE 5001

CMD ["npm", "start"]
