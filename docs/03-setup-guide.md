# Setup Guide

## Prerequisites

- Python 3.8+
- MySQL Server 8.0+

## Installation

```bash
git clone https://github.com/Shikha2u/music-streaming-data-engineering-pipeline.git
cd music-streaming-data-engineering-pipeline
pip install -r requirements.txt
```

## Database Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` with your MySQL credentials:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=spotify_db
```

Alternatively, edit defaults in `db_connection.py`.

## Database Setup

Run the SQL scripts in order:

```bash
mysql -u root -p < sql/01_create_database_and_load_data.sql
mysql -u root -p < sql/02_add_indices_and_functions.sql
```

Script 1 creates the database, tables, and loads sample data.  
Script 2 adds indexes, views, stored procedures, and triggers.

## Running the Application

### Web application (Flask)

```bash
python app.py
```

Visit `http://127.0.0.1:5000`. Log in as an artist or listener to access dashboards.

### CLI tool

```bash
python cli.py
```

Interactive menu for CRUD operations on all entities.

### Extended CLI (artist/listener dashboards)

```bash
python spotify_app.py
```

## Analytical Queries

Ad-hoc analytical SQL examples are in `sql/03_analytical_queries.sql`. Complex queries used by the Python app are in `complex_queries.py`.

## Troubleshooting

- **Connection refused:** Ensure MySQL is running and credentials in `.env` are correct.
- **Database not found:** Run `01_create_database_and_load_data.sql` first.
- **Import errors:** Run `pip install -r requirements.txt` from the project root.
