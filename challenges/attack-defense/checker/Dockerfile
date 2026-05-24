FROM alpine:3.21

RUN apk add --no-cache curl

COPY check.sh /check.sh
RUN chmod +x /check.sh

# enochecker3 exit-code contract: 0 Ok / 1 Mumble / 2 Offline / 3 InternalError.
# The platform runs this image once per (team, tick) with the target +
# planted flag in the environment. Build + push, then reference the tag
# under `ad.checkerImage` in challenge.yml.
ENTRYPOINT ["/check.sh"]
