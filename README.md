# AI Travel Agent

Simple travel recommendation system for Iran.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

Open http://localhost:8000 in your browser.

## What it does

- Suggests travel routes in Iran
- Chat interface for travel planning
- Interactive maps
- Cultural recommendations

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload

# Production
python main_production.py
```

## Docker

```bash
docker-compose up
```

That's it. The app should work out of the box. 