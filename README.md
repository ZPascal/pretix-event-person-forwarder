# Pretix Event Person Forwarder

## Contribution
If you would like to contribute something, have an improvement request, or want to make a change inside the code, please open a pull request.

## Support
If you need support, or you encounter a bug, please don't hesitate to open an issue.

## Donations
If you want to support my work, I ask you to take an unusual action inside the open source community. Donate the money to a non-profit organization like Doctors Without Borders or the Children's Cancer Aid. I will continue to build tools because I like them, and I am passionate about developing and sharing applications.

## License
This product is available under the Apache 2.0 license.

## Integration Tests

Integration tests require a running Pretix instance with HTTPS. The easiest way to set one up locally is via [pretix-docker-compose](https://github.com/ZPascal/pretix-docker-compose), checked out as a sibling directory (`../pretix-docker-compose`).

### Quick Setup

Run the setup script to generate certificates, start Docker, and create test data:

```bash
chmod +x scripts/setup-integration-tests.sh
./scripts/setup-integration-tests.sh
```

The script prints the exact `export` commands to run before executing the tests.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `PRETIX_HOST` | URL of the Pretix API | `https://localhost` |
| `PRETIX_TOKEN` | API token for the test user | required |
| `PRETIX_CA_BUNDLE` | Path to test CA certificate | SSL verification skipped if unset |

### Troubleshooting

**SSL: CERTIFICATE_VERIFY_FAILED** — Verify `PRETIX_CA_BUNDLE` is exported, points to an absolute path, and the file is readable.

**Connection Refused** — Check that containers are running (`docker compose ps`) and port 443 is available. Inspect logs with `docker compose logs -f pretix_app`.

**Organizer not found** — Rerun the setup script or manually execute `docker exec -i pretix_app pretix shell < tests/integrationtest/setup_testdata.py` and check for errors.

**Subject Alternative Name does not match** — Regenerate certificates. Verify SANs with:
```bash
openssl x509 -in ../pretix-docker-compose/docker/pretix/files/config/ssl/domain.crt \
  -text -noout | grep -A1 "Subject Alternative Name"
```

### Cleanup

```bash
cd ../pretix-docker-compose
docker compose down          # stop containers
docker compose down -v       # stop and remove volumes
```
