# Cotiza-inador

## Backend

1. Duplicate `Backend/.env.example` to `Backend/.env` and adjust credentials if needed.
2. Install dependencies: `pip install -r Backend/requirements.txt`.
3. Ensure PostgreSQL is running (see `docker-compose.yml` for a ready-to-use setup).
4. Start the API from the `Backend` folder:
   ```bash
   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Frontend

1. Copy `Frontend/Frontend/.env.example` to `Frontend/Frontend/.env` (update `VITE_API_URL` if the backend is on a different host/port).
2. Install dependencies: `npm install` (inside `Frontend/Frontend`).
3. Run the app:
   ```bash
   npm run dev
   ```

With both services up, visit the frontend (default `http://localhost:5173`). Create an account from the login screen to start managing collections connected to the backend API.
