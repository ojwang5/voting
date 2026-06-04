web: gunicorn voting_system.wsgi --workers 1 --worker-class sync --timeout 120 --max-requests 200 --max-requests-jitter 50 --access-logfile - --error-logfile - --log-level info
