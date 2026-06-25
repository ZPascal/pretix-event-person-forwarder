#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SSL_DIR="$PROJECT_ROOT/../pretix-docker-compose/docker/pretix/files/config/ssl"

echo "Generating test certificates..."
mkdir -p "$SSL_DIR"
cd "$PROJECT_ROOT/../pretix-docker-compose"

openssl genrsa -out "$SSL_DIR/test-ca.key" 2048 2>/dev/null
openssl req -new -x509 -days 365 \
  -key "$SSL_DIR/test-ca.key" \
  -out "$SSL_DIR/test-ca.crt" \
  -subj "/C=DE/ST=State/L=City/O=Test/CN=Test-CA" 2>/dev/null

openssl genrsa -out "$SSL_DIR/domain.key" 2048 2>/dev/null
openssl req -new \
  -key "$SSL_DIR/domain.key" \
  -out "$SSL_DIR/domain.csr" \
  -subj "/C=DE/ST=State/L=City/O=Test/CN=localhost" 2>/dev/null

cat > "$SSL_DIR/san.ext" << 'EOF'
subjectAltName=DNS:localhost,DNS:127.0.0.1
EOF

openssl x509 -req -days 365 \
  -in "$SSL_DIR/domain.csr" \
  -CA "$SSL_DIR/test-ca.crt" \
  -CAkey "$SSL_DIR/test-ca.key" \
  -CAcreateserial \
  -out "$SSL_DIR/domain.crt" \
  -extfile "$SSL_DIR/san.ext" 2>/dev/null

rm "$SSL_DIR/domain.csr" "$SSL_DIR/san.ext"
echo "Certificates generated."

echo "Starting Docker containers..."
docker compose up -d --build --force-recreate

echo "Waiting for Pretix to be ready..."
until curl -s -k https://localhost/api/v1/ > /dev/null; do
  sleep 2
done

echo "Setting up test data..."
docker exec -e DJANGO_SUPERUSER_PASSWORD=admin pretix_app pretix createsuperuser \
  --noinput --username admin --email admin@example.com 2>/dev/null || true

TOKEN=$(docker exec -i pretix_app pretix shell < "$PROJECT_ROOT/tests/integrationtest/setup_testdata.py" 2>/dev/null | tail -1)

cd "$PROJECT_ROOT"

echo ""
echo "Integration test environment ready!"
echo "Run integration tests with:"
echo ""
echo "  export PRETIX_HOST=https://localhost"
echo "  export PRETIX_CA_BUNDLE=$PROJECT_ROOT/../pretix-docker-compose/docker/pretix/files/config/ssl/test-ca.crt"
echo "  export PRETIX_TOKEN=$TOKEN"
echo "  pytest tests/integrationtest/ -v"
