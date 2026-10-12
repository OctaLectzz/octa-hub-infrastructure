# 12 — Hermes Agent Operations and Troubleshooting

**Status:** Initial operational guide; security closeout pending
**Last updated:** 2026-10-12

## 1. Official References

- Repository: https://github.com/NousResearch/hermes-agent
- Docker installation: https://hermes-agent.nousresearch.com/docs/user-guide/docker
- Web dashboard: https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard

Check the official documentation for the deployed release before changing configuration, updating the image, or troubleshooting version-specific behavior.

## 2. Deployment Locations

| Item | Location |
|---|---|
| Infrastructure repository | `/opt/octa` |
| Compose directory | `/opt/octa/stacks/hermes/` |
| Compose file | `/opt/octa/stacks/hermes/compose.yaml` |
| Environment file | `/opt/octa/stacks/hermes/.env` |
| Persistent data | `/opt/octa/data/hermes/` |
| Container name | `hermes` |
| Dashboard | `https://hermes.octalectzz.my.id` |

Keep real credentials and runtime data out of Git.

## 3. Check Container Status

```bash
cd /opt/octa/stacks/hermes
sudo docker compose ps
sudo docker inspect --format '{{.State.Status}}' hermes
```

Confirm that the container is running before investigating application-level problems.

## 4. Read Logs

Read the most recent logs:

```bash
cd /opt/octa/stacks/hermes
sudo docker compose logs --tail=100 hermes
```

Follow logs while reproducing an issue:

```bash
sudo docker compose logs --tail=100 --follow hermes
```

Stop following the logs with `Ctrl+C`. This does not stop the container.

Review log output before sharing it. Remove API keys, bot tokens, OAuth credentials, passwords, personal data, and other sensitive values.

## 5. Validate Compose Configuration

```bash
cd /opt/octa/stacks/hermes
sudo docker compose config --quiet
```

If validation fails, read the error carefully and inspect the relevant configuration. Do not print the rendered Compose configuration into public logs or messages because interpolated environment values may contain secrets.

## 6. Start, Stop, and Restart

Start the service:

```bash
cd /opt/octa/stacks/hermes
sudo docker compose up -d
```

Stop the service:

```bash
sudo docker compose stop
```

Restart the service:

```bash
sudo docker compose restart hermes
```

These operations can interrupt active agent sessions or integrations. Use them only when needed and after considering the impact.

Do not use `docker compose down -v` for routine troubleshooting. Never remove persistent data to solve a problem without a verified recovery plan.

## 7. Dashboard Troubleshooting

Dashboard URL:

`https://hermes.octalectzz.my.id`

If the dashboard is unavailable:

1. Check container status.
2. Inspect recent Hermes logs.
3. Validate the Compose configuration.
4. Confirm the Dahono Web Ingress route and HTTPS configuration.
5. Test the dashboard from the VPS without exposing credentials.

A local HTTP header check can help verify whether the dashboard responds on its published port:

```bash
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' \
  http://127.0.0.1:9119/
```

An HTTP redirect to the login page can be normal. Do not treat an HTTP status code alone as proof that authentication and all dashboard features work.

## 8. API and Network Troubleshooting

The Hermes API server uses port `8642` inside the container network. The current Compose file does not publish that port on the VPS host.

Before diagnosing API connectivity:

- Confirm that the intended client is attached to a network that can reach Hermes.
- Verify the API endpoint and authentication requirements against the deployed release's official documentation.
- Distinguish connectivity failures from authentication failures.
- Never share the API key in a command transcript or support message.

Do not publish the API port publicly or attach additional services to `octa-hub` solely to bypass an unexplained connection failure.

## 9. Telegram Troubleshooting

Telegram connectivity was previously confirmed in gateway logs.

If Telegram stops responding:

1. Check whether the Hermes container is running.
2. Inspect recent logs for Telegram connection or polling errors.
3. Verify that the integration remains configured in the protected runtime data.
4. Check the official Hermes documentation for the current Telegram integration requirements.

Never display or paste the bot token. Do not recreate the integration or overwrite its configuration until the existing state has been inspected.

## 10. Updates and Image Changes

The Compose file references `nousresearch/hermes-agent:stable`.

Before updating:

1. Review the official repository and Docker documentation.
2. Check the current stable release and relevant release notes.
3. Review compatibility and configuration changes.
4. Establish a recovery plan for persistent data.
5. Pull and deploy the selected image deliberately.
6. Verify the container, logs, dashboard authentication, API behavior, and required integrations.

Do not assume that the `stable` tag always refers to the same image. Record the deployed image version or digest after verification.

## 11. Security Reminders

- Do not mount the host Docker socket as a quick troubleshooting fix.
- Do not assume that containers on `octa-hub` are isolated from one another.
- Keep actual `.env` files and runtime data out of Git.
- Do not change public authentication or trusted-proxy settings without reviewing the official guidance.
- Review the terminal backend and sandbox configuration before exposing additional integrations or services.
- Complete `docs/11-hermes-security.md` before declaring the security review closed.
