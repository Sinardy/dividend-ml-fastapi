#!/bin/bash

echo "🔄 Resetting your Postgres database using reset.sql..."

# Run psql inside the container and execute the reset script
docker compose exec db psql -U postgres -d dividends -f /docker-entrypoint-initdb.d/reset.sql

echo "✅ Database has been reset!"
