# Music Streaming Database Platform — Flask App, SQL Analytics & Author-Built Dataset

> **StreamInsight** · Full-stack platform with a 7-table relational database, author-created synthetic sample data, advanced SQL (CTEs, OLAP, window functions), Flask web dashboard, and CLI CRUD tool.

## Impact

Built a music streaming analytics platform that simulates how a streaming service stores and analyzes artists, songs, listeners, and interactions. The project demonstrates relational database design, complex SQL analytics, and a web-based dashboard for artists and listeners.

## About the Data

> **All sample data in this project is original and author-created.** The relational schema, entity relationships, and CSV records were designed and generated for this project to simulate a music streaming platform. This is not scraped, licensed, or proprietary data from any commercial service. Artist names are used only as illustrative placeholders in a fictional dataset.

See [docs/04-synthetic-dataset.md](docs/04-synthetic-dataset.md) and [data/README.md](data/README.md) for details.

## Key Results

- 7-table normalized relational schema (artists, songs, listeners, interactions, subscriptions)
- Advanced SQL: CTEs, subqueries, window functions, OLAP-style aggregations
- Flask web app with artist dashboard and listener interface
- CLI tool for full CRUD operations

## Tech Stack

Python · Flask · MySQL · SQL · HTML/CSS/JavaScript

## Documentation

| Doc | Description |
|-----|-------------|
| [Database Design](docs/01-database-design.pdf) | ERD, schema design, normalization |
| [SQL Features Reference](docs/02-sql-features-reference.md) | CTEs, subqueries, OLAP, set operations |
| [Setup Guide](docs/03-setup-guide.md) | Installation and usage |
| [Synthetic Dataset](docs/04-synthetic-dataset.md) | Author-created data documentation |

## Project Structure

```
music-streaming-data-engineering-pipeline/
├── app.py                  # Flask web application
├── cli.py                  # Command-line CRUD tool
├── spotify_app.py          # CLI dashboard entry point
├── sql/                    # Database setup and queries
├── data/                   # Author-created sample CSVs
├── docs/                   # Project documentation
├── templates/              # Flask HTML templates
└── static/                 # CSS and JavaScript
```

## Setup & Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure database

Copy `.env.example` to `.env` and set your MySQL credentials.

### 3. Create and load the database

```bash
mysql -u root -p < sql/01_create_database_and_load_data.sql
mysql -u root -p < sql/02_add_indices_and_functions.sql
```

### 4. Run the web application

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

### 5. Run the CLI tool (optional)

```bash
python cli.py
```

## Skills Demonstrated

- Relational database design and normalization
- Synthetic dataset creation
- Advanced SQL (CTEs, subqueries, window functions)
- Full-stack web development with Flask
- Data analytics dashboards

## License

MIT
