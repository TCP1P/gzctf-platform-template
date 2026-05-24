#!/bin/sh
# Toy vulnerable service: echoes /flag to anyone who asks. Replace this
# with your real service — the only platform contract is that the round's
# flag lives at /flag (and $GZCTF_FLAG holds the first round's flag).
# Defenders patch the bug; attackers exploit it to read another team's /flag.
while IFS= read -r line; do
    line="${line%$'\r'}"
    [ -z "$line" ] && break
done

flag="$(cat /flag 2>/dev/null || echo 'no flag yet')"
body="flag is: ${flag}
"
printf 'HTTP/1.1 200 OK\r\n'
printf 'Content-Type: text/plain\r\n'
printf 'Content-Length: %d\r\n' "${#body}"
printf 'Connection: close\r\n'
printf '\r\n'
printf '%s' "$body"
