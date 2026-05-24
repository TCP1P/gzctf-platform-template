#!/bin/sh
# Reference checker for the example echo service. The platform sets:
#   GZCTF_TARGET_IP / GZCTF_TARGET_PORT  -> the team's service
#   GZCTF_FLAG                           -> the flag planted THIS tick
#   GZCTF_ROUND / GZCTF_TEAM_ID          -> context (unused here)
#
# Exit code -> check status:
#   0 Ok       flag retrieved as planted
#   1 Mumble   service up but flag wrong / missing
#   2 Offline  TCP refused / timeout
#   3 InternalError  checker bug / missing env
set -u

[ -z "${GZCTF_TARGET_IP:-}" ] && { echo "no target ip" >&2; exit 3; }
[ -z "${GZCTF_TARGET_PORT:-}" ] && { echo "no target port" >&2; exit 3; }

body="$(curl -sS --max-time 5 "http://${GZCTF_TARGET_IP}:${GZCTF_TARGET_PORT}/" 2>&1)"
rc=$?
case "$rc" in
    0) ;;
    6|7|28|56) echo "offline: $body" >&2; exit 2 ;;
    *) echo "offline (curl $rc): $body" >&2; exit 2 ;;
esac

# No flag context (warmup) -> reachability only.
[ -z "${GZCTF_FLAG:-}" ] && exit 0

case "$body" in
    *"${GZCTF_FLAG}"*) exit 0 ;;
    *) echo "flag missing from response" >&2; exit 1 ;;
esac
