#!/bin/bash

# project.sh

start() {
    echo "🚀 Starting containers..."
    docker-compose up -d
}

rebuild() {
    echo "🔨 Rebuilding containers..."
    docker-compose down
    docker-compose up --build -d
}

train() {
    echo "🎯 Running training..."
    docker-compose exec api python train_model.py
}

fetch() {
    echo "📊 Fetching data..."
    docker-compose exec api python fetch_data.py
}

reset_db() {
    echo "🗑️ Resetting database..."
    docker-compose exec db psql -U postgres -d dividends -f /docker-entrypoint-initdb.d/reset.sql
}

add_company() {
    local ticker=$1
    local name=$2
    echo "➕ Adding company: $ticker - $name"
    curl -X POST "http://localhost:8000/companies/add" \
        -H "Content-Type: application/json" \
        -d "{\"ticker\":\"$ticker\", \"name\":\"$name\"}" | jq
}

case "$1" in
    start)
        start
        ;;
    rebuild)
        rebuild
        ;;
    train)
        train
        ;;
    fetch)
        fetch
        ;;
    reset)
        reset_db
        ;;
    add_company)
        add_company "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {start|rebuild|train|fetch|reset|add_company TICKER \"COMPANY NAME\"}"
        exit 1
esac
