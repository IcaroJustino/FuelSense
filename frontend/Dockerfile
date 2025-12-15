FROM node

WORKDIR /app

COPY package*.json ./

##legac6y-peer-deps flag para o chart js
RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 4200

CMD ["npm", "run", "start", "--", "--host", "0.0.0.0"]
