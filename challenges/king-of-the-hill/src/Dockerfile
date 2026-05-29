FROM python:3.12-alpine

# supervisor runs as PID 1 (see supervisord.conf) so the service runs as a child:
# if it crashes, supervisord auto-restarts it in place WITHOUT the container
# exiting, keeping the hill up. The platform has no in-place restart — recreating
# the container (or a hill refresh) reverts to this image and clears /koth/king.
RUN pip install --no-cache-dir supervisor

# KotH has no per-team flag — nothing to bind-mount. The only platform contract
# is the marker file /koth/king: the platform reads it each tick to decide who
# is king. Pre-create the dir so the service (and the players' exploit) can
# write the marker from the first tick.
RUN mkdir -p /koth

COPY service.py /service.py
COPY supervisord.conf /etc/supervisord.conf

EXPOSE 80

# supervisord as PID 1; it runs service.py (pure stdlib http.server) as a child.
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
