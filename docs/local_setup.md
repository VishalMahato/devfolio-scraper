# Local Setup Guide

Follow these instructions to run the Devfolio Scraper on your local machine without Docker.

## 1. Prerequisites
Ensure you have the following installed:
*   **Python 3.10+** (Verify with `python --version`)
*   **PostgreSQL** (Verify with `psql --version`)
*   **Git** (Verify with `git --version`)

## 2. Clone the Repository
Clone the project to your local machine:
```bash
git clone <your-repo-url>
cd devfolio-scraper
```

## 3. Create a Virtual Environment
A virtual environment isolates this project's dependencies from your global Python installation.

Run the following command inside the `devfolio-scraper` directory:
```bash
python -m venv venv
```

Activate the virtual environment:
*   **Windows (Command Prompt):** `venv\Scripts\activate`
*   **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
*   **macOS and Linux:** `source venv/bin/activate`

## 4. Install Dependencies
Once the virtual environment is activated (your terminal should show `(venv)`), install the required Python packages:
```bash
pip install -r requirements.txt
```

## 5. Database Setup (Docker)
Since you are using Docker for PostgreSQL, you don't need to install or configure it manually on your machine. Docker will handle creating the database and running the `init.sql` schema automatically.

Run the following command to start only the database container in the background:
```bash
docker-compose up -d db
```

Wait a few seconds for the database to initialize. You can verify it is running with:
```bash
docker ps
```

## 6. Configure Environment Variables
Copy the template `.env` file to set up your local credentials.

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Open the `.env` file and ensure the credentials match the `docker-compose.yml` defaults:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=devfolio
```
Do **not** commit the `.env` file to version control.

## 7. Run the Scraper
With the database running in Docker, you can now run the Python scraper locally from your virtual environment. The script will connect to the exposed `5432` port on `localhost`.

```bash
python -m src.main
```
