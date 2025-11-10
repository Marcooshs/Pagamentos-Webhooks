#!/usr/bin/env sh
set -e

WEB_INTERNAL_PORT="${WEB_INTERNAL_PORT:-9000}"

# Espera o Postgres subir (lendo DATABASE_URL)
if [ -n "$DATABASE_URL" ]; then
  echo "Aguardando Postgres em: $DATABASE_URL"
  DB_HOST=$(python - <<'PY'
import os, re
u=os.getenv("DATABASE_URL","")
m=re.match(r'^\w+://[^:]+:[^@]+@([^:/]+):?(\d+)?', u)
print(m.group(1) if m else "db")
PY
)
  DB_PORT=$(python - <<'PY'
import os, re
u=os.getenv("DATABASE_URL","")
m=re.match(r'^\w+://[^:]+:[^@]+@([^:/]+):?(\d+)?', u)
print(m.group(2) if (m and m.group(2)) else "5432")
PY
)
  echo "Esperando $DB_HOST:$DB_PORT ..."
  for i in $(seq 1 60); do
    if nc -z "$DB_HOST" "$DB_PORT"; then
      echo "Postgres disponível!"
      break
    fi
    echo "Aguardando Postgres... ($i)"
    sleep 1
  done
fi

python manage.py migrate --noinput

# Se nenhum comando foi passado, inicia o Django na porta interna configurada
if [ $# -eq 0 ]; then
  set -- python manage.py runserver "0.0.0.0:${WEB_INTERNAL_PORT}"
fi

exec "$@"
