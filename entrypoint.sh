#!/usr/bin/env bash
set -e

# Espera o Postgres subir
if [ -n "$DATABASE_URL" ]; then
  echo "Aguardando Postgres em: $DATABASE_URL"
  # tenta extrair host e port do DATABASE_URL
  DB_HOST=$(python - <<'PY'
import os, re
u=os.getenv("DATABASE_URL","")
m=re.match(r'^\w+://[^:]+:[^@]+@([^:/]+):?(\d+)?/', u)
print(m.group(1) if m else "db")
PY
)
  DB_PORT=$(python - <<'PY'
import os, re
u=os.getenv("DATABASE_URL","")
m=re.match(r'^\w+://[^:]+:[^@]+@([^:/]+):?(\d+)?/', u)
print(m.group(2) if (m and m.group(2)) else "5432")
PY
)
  echo "Esperando $DB_HOST:$DB_PORT ..."
  for i in {1..60}; do
    if nc -z "$DB_HOST" "$DB_PORT"; then
      echo "Postgres disponível!"
      break
    fi
    echo "Aguardando Postgres... ($i)"
    sleep 1
  done
fi

# Migrações (idempotente)
python manage.py migrate --noinput

# Coleta de estáticos (se um dia adicionar whitenoise/nginx)
# python manage.py collectstatic --noinput || true

exec "$@"
