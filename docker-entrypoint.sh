#!/bin/sh
set -e

show_usage() {
  msg="Usage:"
  msg="${msg} docker run -it [options] <image> -v \$PWD:/scan/"
  msg="${msg} -e USER=<user> -e PASS=<pass>"
  msg="${msg} -e SECRET_ANSWER=<answer> -e SELENIUM_SERVER_URL=<url>"
  echo "$msg"
  exit 1
}

[ -z "$USER" ] && echo "USER env not set" && show_usage
[ -z "$PASS" ] && echo "PASS env not set" && show_usage
[ -z "$SECRET_ANSWER" ] && echo "SECRET_ANSWER env not set" && show_usage

[ -z "$SELENIUM_SERVER_URL" ] && echo "SELENIUM_SERVER_URL" && show_usage

selenium_wait_timeout="${SELENIUM_WAIT_TIMEOUT:-60}"
out_file="/scan/scan.json"

python -m upwork \
  --user "$USER" \
  --pass "$PASS" \
  --secret-answer "$SECRET_ANSWER" \
  --selenium-server-url "$SELENIUM_SERVER_URL" \
  --selenium-wait-timeout "$selenium_wait_timeout" \
  --out-file "$out_file"
