#!/bin/sh
# First boot only: copy the bundled demo database into the persistent volume
mkdir -p /data
if [ ! -f /data/parking.db ] && [ -f /app/parking.db ]; then
  cp /app/parking.db /data/parking.db
  echo "Seeded /data/parking.db from bundled demo database"
fi
exec "$@"
