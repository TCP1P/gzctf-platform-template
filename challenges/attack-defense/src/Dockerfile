FROM python:3.12-alpine

# Warmup flag — the platform overwrites /flag every tick via docker exec.
# Read the flag from /flag at request time (path also in GZCTF_FLAG_FILE);
# there is no GZCTF_FLAG env var for the service (it would freeze at start).
RUN echo 'flag{warmup-no-round-yet}' > /flag && chmod 644 /flag

COPY service.py /service.py

EXPOSE 80

# Pure stdlib (http.server) — no pip install needed for the service.
CMD ["python3", "/service.py"]
