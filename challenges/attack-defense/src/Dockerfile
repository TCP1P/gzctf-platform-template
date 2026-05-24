FROM python:3.12-alpine

# Warmup flag — the platform overwrites /flag every tick via docker exec,
# and injects the first round's flag through the GZCTF_FLAG env var.
RUN echo 'flag{warmup-no-round-yet}' > /flag && chmod 644 /flag

COPY service.py /service.py

EXPOSE 80

# Pure stdlib (http.server) — no pip install needed for the service.
CMD ["python3", "/service.py"]
