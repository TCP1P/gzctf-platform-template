FROM python:3.12-alpine

COPY challenge.py /challenge.py

EXPOSE 8011

# GZCTF injects GZCTF_FLAG (per-team, from flagTemplate in challenge.yml)
# as an env var when it starts each team's container. Pure stdlib — no
# pip install, no socat.
CMD ["python3", "/challenge.py"]
