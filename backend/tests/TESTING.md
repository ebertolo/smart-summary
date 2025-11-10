# Running Tests 🧪

## Prerequisites

Make sure you have initialized the database first:

```bash
cd backend
python scripts/init_db.py
```

This creates the demo user required for authentication tests.

## Run All Tests

```bash
# From backend directory
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py
pytest tests/test_services.py
```


## Common Issues

### Database Not Initialized
```
Error: User not found
Solution: Run python scripts/init_db.py
```

### Import Errors
```
Error: ModuleNotFoundError
Solution: Make sure you're in the backend directory
```

### Port Already in Use
```
Error: Address already in use
Solution: Stop the running server or use a different port
```


## Quick Reference

```bash
# Most common command
cd backend && pytest -v

# With coverage
cd backend && pytest --cov=app

# Specific file
cd backend && pytest tests/test_api.py -v

# Fail fast
cd backend && pytest -x -v
```
