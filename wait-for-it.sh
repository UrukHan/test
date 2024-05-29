#!/usr/bin/env bash

set -e

cmd="$@"

until pg_isready -h "postgres" -U "your_user"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
