# Stage 1: Build the Node.js SPA
FROM node:23 AS node-build
WORKDIR /app
COPY ./app-ui/package*.json ./
RUN npm install
COPY ./app-ui .
RUN npm run build

# Stage 2: Build the Python app
FROM python:3.9-slim AS python-build
WORKDIR /app
COPY ./app-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app-api .

# Stage 3: Final stage with Uvicorn
FROM python:3.12-slim
WORKDIR /app
COPY --from=python-build /app/requirements.txt /app
RUN pip install -r requirements.txt
COPY --from=python-build /app /app
COPY --from=node-build /app/dist /app/static
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
