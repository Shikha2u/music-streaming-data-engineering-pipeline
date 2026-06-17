# Synthetic Dataset Documentation

## Overview

All data in this project is **original and author-created**. The dataset was designed to simulate a music streaming platform for learning and portfolio purposes. It is safe to share publicly and carries no licensing restrictions from commercial data providers.

## Why Synthetic Data?

- Demonstrates ability to **design schemas** and **generate realistic sample records**
- Avoids legal and privacy issues with proprietary or scraped data
- Fully reproducible — anyone can reload the database from included CSVs and SQL scripts

## Schema Design (7 Tables)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `artist` | Music artist profiles | name, country, genre, bio, join_date |
| `song` | Song catalog | title, duration, genre, release_date |
| `listener_account_type` | Subscription plans | account_type, start_date, auto_renew |
| `listener` | User accounts | demographics, email, country, account_id |
| `song_artist` | Many-to-many: songs ↔ artists | song_id, artist_id |
| `song_interaction` | User engagement events | interaction_type (Play, Like, Share, Skip) |
| `follow_artist` | Listener follows artist | listener_id, artist_id |

## Entity Relationships

- A **song** can have multiple **artists** (via `song_artist`)
- A **listener** has one **account type** (subscription tier)
- **Interactions** link listeners to songs with event types and timestamps
- **Follows** track which artists each listener follows

## How Records Were Crafted

- **Artists:** Mix of genres and countries; bios describe musical style
- **Songs:** Realistic durations, genres aligned with artists
- **Listeners:** Diverse demographics across countries and age groups
- **Interactions:** Weighted toward Plays with smaller counts of Likes, Shares, Skips
- **Subscriptions:** Mix of Free, Individual, Family, Duo, and Student tiers

Artist and listener names in the dataset are **fictional placeholders** — they illustrate a realistic catalog structure, not real user or rights-holder data.

## Data Files

CSV exports are in the [`data/`](../data/) folder. The SQL load script (`sql/01_create_database_and_load_data.sql`) inserts the same records into MySQL.

## Disclaimer

This project is **not affiliated with, endorsed by, or sourced from** any commercial music streaming service. The platform concept is used only as a familiar domain for demonstrating database and analytics skills.
