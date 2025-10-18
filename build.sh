#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Warm up AI models (download on first build)
echo "🤖 Warming up AI models..."
python manage.py warm_up_ai || echo "⚠️  AI models warm-up skipped (optional feature)"

echo "✅ Build completed successfully!"