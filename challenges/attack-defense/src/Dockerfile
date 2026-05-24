FROM alpine:3.21

RUN apk add --no-cache socat

# Warmup flag — the platform overwrites /flag every tick via docker exec,
# and also injects the first round's flag through the GZCTF_FLAG env var.
RUN echo 'flag{warmup-no-round-yet}' > /flag && chmod 644 /flag

COPY serve.sh /serve.sh
RUN chmod +x /serve.sh

EXPOSE 80

# socat forks per connection; serve.sh reads /flag fresh each request so
# the per-tick rotation is visible immediately (no caching).
CMD ["socat", "-T", "5", "TCP-LISTEN:80,reuseaddr,fork", "SYSTEM:/serve.sh"]
