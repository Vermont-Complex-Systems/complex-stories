# Local PostgreSQL Development Setup

This guide will help you set up PostgreSQL locally for developing the Complex Stories backend.

## 1. Install PostgreSQL

### macOS (using Homebrew)
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Windows
Download and install from: https://www.postgresql.org/download/windows/

## 2. Create Database and User

```bash
# Connect to PostgreSQL as the postgres user
sudo -u postgres psql

# Or on macOS:
psql postgres
```

Then in the PostgreSQL shell:
```sql
-- Create database
CREATE DATABASE complex_stories;

-- Create user
CREATE USER complex_stories_user WITH PASSWORD 'development_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE complex_stories TO complex_stories_user;

-- Grant schema permissions (PostgreSQL 15+)
\c complex_stories
GRANT ALL ON SCHEMA public TO complex_stories_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO complex_stories_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO complex_stories_user;

-- Exit
\q
```

## 3. Set Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# PostgreSQL Connection
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=complex_stories
POSTGRES_USER=complex_stories_user
POSTGRES_PASSWORD=development_password

# Or use a single DATABASE_URL
DATABASE_URL=postgresql+asyncpg://complex_stories_user:development_password@localhost:5432/complex_stories
```

## 4. Install Python Dependencies

```bash
cd backend
uv sync
```

## 5. Create Database Tables

Create a script to initialize the database tables:

```bash
cd backend
python -c "
import asyncio
from app.core.database import connect_to_database, get_engine
from app.models import Base

async def create_tables():
    await connect_to_database()
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Database tables created successfully!')

asyncio.run(create_tables())
"
```

## 6. Test the Connection

Start the FastAPI server:
```bash
cd backend
uv run fastapi dev app/main.py
```

Test the endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Test papers endpoint (will return empty data initially)
curl http://localhost:8000/open-academic-analytics/papers/test-author

# Test coauthors endpoint (will return empty data initially)
curl http://localhost:8000/open-academic-analytics/coauthors/test-author
```

## 7. Next Steps

1. **Update Dagster Pipeline**: Modify the export assets to POST data to these endpoints
2. **Run Pipeline**: Execute the Dagster pipeline to populate the database
3. **Test Frontend**: Update frontend to call the new API endpoints

## Troubleshooting

### Connection Issues
- Check if PostgreSQL is running: `pg_isready`
- Verify database exists: `psql -U complex_stories_user -d complex_stories -h localhost`
- Check environment variables are loaded

### Permission Issues
- Make sure the user has proper permissions on the database
- Check schema permissions if tables can't be created

### Port Conflicts
- PostgreSQL default port is 5432
- FastAPI dev server uses port 8000
- Change ports in configuration if needed