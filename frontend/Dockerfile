FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Remove app/ directory if it exists (conflicts with pages/)
RUN rm -rf src/app app

EXPOSE 3000

CMD ["npm", "run", "dev"]