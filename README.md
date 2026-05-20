# ⚡ PokémonDB — Pokémon Trading Card Database

> A full-stack Django 5.2 web application for browsing, searching, and managing Pokémon Trading Card Game data. Built for the Database Design course ISE3235-001 at Inha University.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.2_LTS-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Windows](#windows)
  - [Mac](#mac)
  - [Linux](#linux)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
  - [SQLite (Default — Development)](#sqlite-default--development)
  - [PostgreSQL (Production)](#postgresql-production)
- [Importing Card Data](#importing-card-data)
- [Running the Server](#running-the-server)
- [Available Pages](#available-pages)
- [CRUD Operations](#crud-operations)
- [SQL Showcase](#sql-showcase)
- [Exporting to MySQL (XAMPP)](#exporting-to-mysql-xampp)
- [Deployment (Railway)](#deployment-railway)
- [Project Structure](#project-structure)
- [Team](#team)

---

## Features

| Feature | Description |
|---------|-------------|
| 🃏 Card Browser | Browse 20,000+ cards with images, HP, types, rarity |
| 🔍 Search & Filter | Filter by name, type, set, rarity, HP range, price |
| 💰 Market Prices | Live TCGPlayer and CardMarket prices per card |
| ⚔️ Attacks | Full attack list with damage and energy cost |
| 📦 Sets | All 160+ official TCG sets with stats |
| 📊 Dashboard | KPIs, charts, most valuable cards |
| 🗄️ SQL Showcase | 8 live queries with ORM code + raw SQL + results |
| ⚔️ Battle Simulator | Compare two cards head to head |
| 🔄 Set Compare | Side-by-side set comparison |
| ❤️ Favourites | Save favourite cards (requires login) |
| 👤 User Auth | Register, login, account management |
| ✏️ Full CRUD | Create, edit, delete cards from the browser |
| 🛡️ Jazzmin Admin | Premium admin panel |
| 🐛 Debug Toolbar | Live SQL query inspector |
| 🗃️ Dual Database | SQLite for dev, PostgreSQL for production |
| 📤 MySQL Export | Export data for XAMPP/phpMyAdmin |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 5.2 LTS |
| Language | Python 3.12 |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL 16 |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Admin Panel | Jazzmin |
| Static Files | WhiteNoise |
| Web Server | Gunicorn |
| Fonts | Google Fonts (Cinzel, DM Sans) |
| Data Source | PokémonTCG API v2 |
| Debug | Django Debug Toolbar |

---

## Prerequisites

Before starting make sure you have:

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **Git** — [git-scm.com](https://git-scm.com)
- **PostgreSQL 14+** — optional, for production database
- **PokémonTCG API key** — free at [dev.pokemontcg.io](https://dev.pokemontcg.io)

---

## Installation

### Windows

```cmd
:: Check Python
python --version

:: Clone the repo
git clone https://github.com/YOUR_USERNAME/pokemon-card-db.git
cd pokemon-card-db

:: Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt
```

### Mac

```bash
# Check Python
python3 --version

# Clone the repo
git clone https://github.com/YOUR_USERNAME/pokemon-card-db.git
cd pokemon-card-db

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Linux

```bash
# Install system dependencies
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y

# Clone the repo
git clone https://github.com/YOUR_USERNAME/pokemon-card-db.git
cd pokemon-card-db

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root (same folder as `manage.py`):

```env
POKEMONTCG_API_KEY=your-api-key-here
```

> ⚠️ Never commit `.env` to GitHub — it is already in `.gitignore`.

Get your free API key from [dev.pokemontcg.io](https://dev.pokemontcg.io).

---

## Database Setup

### SQLite (Default — Development)

No extra setup needed. Just run migrations:

**Windows:**
```cmd
python manage.py migrate
python manage.py collectstatic
```

**Mac/Linux:**
```bash
python3 manage.py migrate
python3 manage.py collectstatic
```

---

### PostgreSQL (Production)

**Step 1 — Install PostgreSQL**

- Windows: [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
- Mac: `brew install postgresql && brew services start postgresql`
- Linux: `sudo apt install postgresql postgresql-contrib -y`

**Step 2 — Create database and user**

Open PostgreSQL shell:
- Windows: pgAdmin or `psql -U postgres`
- Mac: `psql postgres`
- Linux: `sudo psql -U postgres`

Run these commands:
```sql
CREATE USER pokemon_user WITH PASSWORD 'pokemon123';
CREATE DATABASE pokemon_db OWNER pokemon_user;
GRANT ALL PRIVILEGES ON DATABASE pokemon_db TO pokemon_user;
GRANT ALL ON SCHEMA public TO pokemon_user;
\q
```

**Step 3 — Run migrations on PostgreSQL**

Windows:
```cmd
set DB_ENGINE=postgres && python manage.py migrate
```

Mac/Linux:
```bash
DB_ENGINE=postgres python3 manage.py migrate
```

---

## Importing Card Data

### Import a specific set

**Windows:**
```cmd
python manage.py import_cards --set base1
```

**Mac/Linux:**
```bash
python3 manage.py import_cards --set base1
```

### Import into PostgreSQL

**Windows:**
```cmd
set DB_ENGINE=postgres && python manage.py import_cards --set base1
```

**Mac/Linux:**
```bash
DB_ENGINE=postgres python3 manage.py import_cards --set base1
```

### Popular set IDs

| Set ID | Name | Cards |
|--------|------|-------|
| `base1` | Base Set | 102 |
| `base2` | Jungle | 64 |
| `fossil` | Fossil | 62 |
| `neo1` | Neo Genesis | 111 |
| `neo2` | Neo Discovery | 75 |
| `gym1` | Gym Heroes | 132 |
| `gym2` | Gym Challenge | 132 |
| `swsh1` | Sword & Shield | 216 |
| `sv1` | Scarlet & Violet | 264 |

### Import all cards (~20,000, takes 10-15 min)

```bash
DB_ENGINE=postgres python3 manage.py import_cards
```

### Import only sets (no cards)

```bash
python3 manage.py import_cards --sets-only
```

---

## Running the Server

### SQLite (development)

**Windows:**
```cmd
python manage.py runserver
```

**Mac/Linux:**
```bash
python3 manage.py runserver
```

### PostgreSQL (default)

**Windows:**
```cmd
python manage.py runserver
```

**Mac/Linux:**
```bash
python3 manage.py runserver
```

Open browser at `http://127.0.0.1:8000`

> PostgreSQL is the default database. To use SQLite instead run:
> ```bash
> DB_ENGINE=sqlite python3 manage.py runserver
> ```

---

## Available Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Hero, stats, featured cards, recent sets |
| Card List | `/cards/` | Browse with search, filters, sorting, pagination |
| Card Detail | `/cards/<id>/` | Full info, prices, attacks, favourites |
| Add Card | `/cards/new/` | Create a new card (login required) |
| Set List | `/sets/` | All TCG sets with search |
| Set Detail | `/sets/<id>/` | Cards in a set with stats |
| Set Compare | `/sets/compare/` | Side-by-side set comparison |
| Search | `/search/` | Search cards and sets |
| Dashboard | `/dashboard/` | KPIs, charts, most valuable cards |
| SQL Showcase | `/sql-showcase/` | 8 live queries with ORM + SQL + results |
| Battle | `/battle/` | Simulate card battles |
| Account | `/account/` | Profile and favourites |
| Signup | `/account/signup/` | Register |
| Login | `/accounts/login/` | Sign in |
| Admin | `/admin/` | Jazzmin admin panel |

---

## CRUD Operations

### From the browser

- **Create:** Go to `/cards/new/` or click **+ Add Card** in navbar (login required)
- **Read:** Browse `/cards/` or click any card
- **Update:** Open any card → click **Edit** button (login required)
- **Delete:** Open any card → click **Delete** button (login required)

### Django Admin Panel

Create a superuser first:

```bash
python3 manage.py createsuperuser
```

Then visit `http://127.0.0.1:8000/admin/`

---

## SQL Showcase

Visit `http://127.0.0.1:8000/sql-showcase/` to see 8 live database queries:

| # | Query Type | Description |
|---|-----------|-------------|
| 1 | Multi-Table JOIN | Top HP cards with set and type info |
| 2 | GROUP BY + AVG | Average HP per Pokémon type |
| 3 | GROUP BY + COUNT | Card count per rarity |
| 4 | JOIN + AVG | Average market price per rarity |
| 5 | GROUP BY + ORDER | Top artists by card count |
| 6 | FILTER + LIMIT | Highest energy cost attacks |
| 7 | NULL CHECK | Data completeness report |
| 8 | MULTI-JOIN + COUNT | Type battle statistics |

Each query shows:
- 🐍 Django ORM Python code
- 🗄️ Auto-generated SQL sent to PostgreSQL
- 📊 Live results from the database

### Django Debug Toolbar

With `DEBUG=True`, a toolbar appears on every page showing:
- Every SQL query executed per request
- Query execution times
- Request/response headers
- Template rendering times

---

## Exporting to MySQL (XAMPP)

Generate a MySQL-compatible SQL dump:

```bash
python3 export_mysql.py
```

This creates `mysql_dump.sql`. To import into phpMyAdmin:

1. Open XAMPP → start **Apache** and **MySQL**
2. Go to `http://localhost/phpmyadmin`
3. Create a new database called `pokemon_db`
4. Click the **Import** tab
5. Select `mysql_dump.sql`
6. Click **Go**

---

## Deployment (Railway)

**Step 1 — Push your code to GitHub**

```bash
git add .
git commit -m "Ready for deployment"
git push
```

**Step 2 — Create a Railway project**

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository

**Step 3 — Add PostgreSQL**

In Railway dashboard:
1. Click **Add Service** → **Database** → **PostgreSQL**
2. Railway auto-sets `DATABASE_URL`

**Step 4 — Set environment variables**

In Railway → your service → **Variables**:
```
POKEMONTCG_API_KEY=your-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
SECRET_KEY=your-secret-key
DB_ENGINE=postgres
```

**Step 5 — Deploy**

Railway auto-deploys on every push to `main`.

---

## Project Structure

```
pokemon_db/
├── manage.py                          # Django entry point
├── requirements.txt                   # Python dependencies
├── Procfile                           # Railway/Heroku process file
├── railway.json                       # Railway config
├── export_mysql.py                    # MySQL dump generator
├── mysql_dump.sql                     # MySQL export for XAMPP
├── .env                               # Environment variables (not in git)
├── .gitignore
│
├── pokemondb/                         # Django project config
│   ├── settings.py                    # All settings
│   ├── urls.py                        # Root URL config
│   └── wsgi.py
│
├── cards/                             # Main Django app
│   ├── models.py                      # Card, Set, Type, Attack, Price, Favorite
│   ├── views.py                       # All page views
│   ├── urls.py                        # URL routing
│   ├── services.py                    # PokémonTCG API integration
│   ├── admin.py                       # Jazzmin admin config
│   └── management/
│       └── commands/
│           └── import_cards.py        # Data import command
│
├── templates/
│   ├── base.html                      # Bootstrap 5 base layout
│   ├── cards/
│   │   ├── home.html
│   │   ├── card_list.html
│   │   ├── card_detail.html
│   │   ├── card_form.html
│   │   ├── card_confirm_delete.html
│   │   ├── set_list.html
│   │   ├── set_detail.html
│   │   ├── set_compare.html
│   │   ├── search_results.html
│   │   ├── dashboard.html
│   │   ├── sql_showcase.html
│   │   └── battle_simulator.html
│   ├── components/
│   │   ├── card_grid.html             # Reusable card grid
│   │   └── pagination.html            # Reusable pagination
│   ├── errors/
│   │   ├── 404.html
│   │   └── 500.html
│   └── registration/
│       ├── login.html
│       ├── signup.html
│       ├── account.html
│       └── password_change_form.html
│
└── static/
    ├── css/main.css                   # Custom styles
    └── js/main.js                     # Vanilla JavaScript
```

---

## Team

| # | Name | Student ID |
|---|------|------------|
| 1 | Asralkhanov Zikrilloh Davronbek Ugli | 12245027 |
| 2 | Ibragimov Asadbek | 12245008 |
| 3 | Lifrov Vadim | 12240192 |
| 4 | Sara Beslic | 12260051 |
| 5 | Murzabekov Alymbek | 12240190 |
| 6 | Li Mikhail | 12236295 |

---

**Course:** Database Design · ISE3235-001 · Inha University  
**Data Source:** [PokémonTCG API](https://api.pokemontcg.io/v2)  
**Not affiliated with Nintendo or The Pokémon Company.**