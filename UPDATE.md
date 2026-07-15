# Maintenance Update — 15 July 2026

A health check of the project turned up three bugs that made a fresh deploy fail,
a set of leaked credentials, and a readme describing a system that no longer
existed. This is what changed and what is still outstanding.

Commits: `6ed87ae`, `a065271`, `3cbeeec`, `4e0532b`, `a2898a9`, plus a history
rewrite (see [Leaked credentials](#leaked-credentials)).

---

## 1. A fresh deploy created no database tables

**`6ed87ae`**

`alembic.ini` set `script_location = alembic`, but the migration files lived in a
root-level `versions/` directory. Alembic therefore found **zero** migrations:
`alembic heads` returned nothing, and the Dockerfile's `alembic upgrade head`
succeeded silently while doing nothing. A fresh deploy came up against an empty
database and every query failed.

Moving the files into `alembic/versions/` exposed two more problems underneath:

- **Two independent heads.** The three revisions formed two unconnected
  branches, and `alembic upgrade head` fails outright when there is more than one
  head. (This is why the Dockerfile had been changed to `upgrade heads`, plural —
  that was a workaround for the symptom, not a fix.)
- **`test_results.tokens_used` was never created by any migration**, even though
  `models.py` defines it and `main.py` writes to it on *every report upload*. The
  two revisions named `add_tokens_used` did not add the column. They were
  misnamed CockroachDB-era autogenerate output (`postgresql_using="prefix"`) that
  only altered indexes and column types, and both declared `down_revision = None`
  while running pure `ALTER TABLE`, so neither could run against an empty
  database at all.

**Fix:** dropped the two dead revisions, kept `5a1b15c7d385` (*Fresh_Start*) as
the baseline, and added `c1d2e3f4a5b6` to create the missing column. History is
now a single linear head.

**Verified:** the stack was run end to end against a real Postgres. Migrations
applied cleanly on startup, and the database now has all three tables plus
`tokens_used`.

> **Keep the history to a single head.** If `alembic heads` ever prints more than
> one revision, `upgrade` will break again.

## 2. Every signup and login was broken

**`6ed87ae`**

`requirements.txt` had `passlib[bcrypt]` commented out in favour of a bare
`passlib`, and nothing else pulled in `bcrypt`. But `main.py` uses
`CryptContext(schemes=["bcrypt"])`, so on any clean build the backend was absent
and every signup and login raised `MissingBackendError: bcrypt: no backends
available`.

**Fix:** pinned `passlib[bcrypt]==1.7.4` with `bcrypt==4.0.1` (passlib 1.7.4
cannot read the version of bcrypt >= 4.1).

**Verified:** signup and login both succeed against the running stack, the stored
hash is a genuine `$2b$12$` bcrypt digest, and a wrong password is rejected.

## 3. Secrets were being baked into the Docker image

**`a065271`**

The Dockerfile ran `COPY . .` with no exclusions, which copied `.env`,
`keys.txt`, the Google `client_secret` JSON, the `.git` history, and ~650KB of
generated codebase dumps into the image layers.

**Fix:** added `.dockerignore`. The app already receives its secrets at runtime
via Compose's `env_file`, so none of this ever needed to be in the image.

## 4. The session key had an unsafe default

**`a065271`**

`main.py` fell back to `secret_key="unsafe-secret"` when `SECRET_KEY` was unset,
which would let anyone forge session cookies if the variable ever went missing in
production.

**Fix:** the app now raises at startup instead. The check rejects an empty string
as well as an unset variable.

## 5. The database password was hardcoded

**`6ed87ae`, `a065271`**

The password appeared in plaintext in two tracked files:

- `alembic.ini` — dead config. `alembic/env.py` imports `DATABASE_URL` from the
  environment for both its offline and online paths and never reads this value.
  Removed.
- `docker-compose.yml` — now `${POSTGRES_PASSWORD:?...}`, read from `.env`.
  Compose **refuses to start** if it is unset rather than falling back to a known
  value.

## 6. The port migration was only half-applied

**`3cbeeec`, `4e0532b`**

FastAPI moved from **8080 to 8502** in `6244a59`, but four call sites still
assumed 8080: the `PUBLIC_API_URL` defaults in both `app.py` and `main.py`,
`main.py`'s `uvicorn.run`, and `check_users.py`'s documented debug URL. All now
agree on 8502. Streamlit is unchanged on 8501.

`deploy.sh` was stale in the same way — it ran `docker run` against a single
image with **no database container attached** and published the retired 8080, so
it could not deploy the current stack. It now runs `docker compose up -d --build`.

Also fixed a variable-name mismatch: `main.py` reads `FRONTEND_URL` to decide
where to send the browser after a Google login, but nothing defined it, so it
silently fell back to `http://localhost:8501` and stranded remote users. (`.env`
defined `STREAMLIT_PUBLIC_URL`, which nothing reads.)

## 7. The readme described a system that no longer exists

**`3cbeeec`**

It still documented the pre-migration CockroachDB architecture: the retired
`root.crt` / `sslmode=verify-full` setup, a `get_cert.py` that does not exist in
the repo, a `docker run` invocation that starts the app with **no database**, a
container name (`health-server`) that Compose never creates, and port 8080
throughout — including the Cloudflare Tunnel routing rules. It also omitted
`POSTGRES_PASSWORD`, which Compose now requires, and its markdown had lost its
newlines and rendered as a single paragraph.

Rewritten to describe the actual stack: Compose, local Postgres, ports 8501/8502,
single-head migrations, and a complete `.env` template.

---

## Leaked credentials

The Gemini API key was committed to the repository in the initial commit, inside
a file called `New Text Document.txt` (which was really a copy of `.env`). The
CockroachDB password was in `postgresql_cockroachdb.txt` in the same commit. Both
were harvested, and the Google project was suspended for *"abusive activity
consistent with hijacking"* (since reinstated).

| Credential | Where it leaked | Status |
| --- | --- | --- |
| Gemini API key | `New Text Document.txt`, initial commit | Leaked key **deleted**; new key issued under the reinstated project. |
| CockroachDB password | `postgresql_cockroachdb.txt` | Cluster is dead — no action needed. |
| GitHub PAT | `deploy.sh` | Dead — GitHub auto-revoked it (verified: HTTP 401). |
| Postgres password | `alembic.ini`, `docker-compose.yml` | LAN-only, low risk. Rotate at leisure. |
| Google OAuth secret | — | **Never committed.** |

**History was rewritten** with `git filter-repo`: the five credential-dump text
files (`New Text Document.txt`, `postgresql_cockroachdb.txt`, `howTo.txt`,
`checkpoint1.txt`, `plan.txt`) were removed outright, and the GitHub token and
Postgres password embedded in `deploy.sh` and `alembic.ini` were replaced across
every commit on `main` and `development`.

> **The first rewrite did not persist — corrected 15 Jul 2026.** A stale clone
> still holding the original history had pushed it back, so `4f06af0` and the
> leaked files resurfaced on `origin` (the earlier "verified absent / 404" claim
> here was wrong). The rewrite was redone from a fresh clone of `origin`; the new
> root commit is `85878ad`, `4f06af0` no longer resolves on the remote, and the
> dump files are gone from all history. **Every clone must be hard-reset (below),
> or the next push from a stale one resurrects the leak again.**

> **Note:** every commit hash cited elsewhere in this document predates the
> rewrite and no longer resolves. The changes they describe are intact under new
> hashes.

`.gitignore` was also rewritten — it had been corrupted with UTF-16 NUL bytes by a
PowerShell `Out-File`, and its secret patterns now glob properly.

> **This closes the door; it does not un-copy what was taken.** Scrubbing history
> is not a substitute for rotating the keys — and the repo was public during the
> leak window, so treat every value above as harvested regardless.

### Because history was rewritten

Every commit hash changed. On the Pi, do **not** `git pull`:

```bash
git fetch origin
git reset --hard origin/main   # .env is untracked, so it survives
```

---

## Still outstanding

1. **Expose the OAuth backend publicly.** Google login runs on FastAPI
   (port 8502), but the public hostname currently reaches only Streamlit
   (port 8501), so `/auth/login` and `/auth/callback` never hit the backend and
   login bounces back to the home page. Route `/auth/*` to 8502 — either a second
   hostname pointing at the backend, or a path rule on the reverse proxy — then
   set `PUBLIC_API_URL` to that backend URL and add its `/auth/callback` to the
   Google OAuth **Authorized redirect URIs**. (Email/password login is unaffected;
   the frontend reaches the backend internally over `localhost:8502`.)
2. **Restrict the published ports to the tunnel.** Compose publishes 8501/8502 on
   `0.0.0.0`, so the services can be reached directly rather than only through the
   tunnel. Bind them to loopback in `docker-compose.yml`:
   ```yaml
   ports:
     - "127.0.0.1:8501:8501"
     - "127.0.0.1:8502:8502"
   ```
   If the tunnel runs on a separate host and reaches this machine over the
   network, loopback binding would cut it off — in that case firewall 8501–8502 to
   the tunnel's source address instead. Confirm where the tunnel originates first.
3. **Rotate the local Postgres password at leisure** (LAN-only). Editing `.env`
   alone does nothing — Postgres applies `POSTGRES_PASSWORD` only when initializing
   an *empty* volume. Change it in the database and in `.env` together:
   ```bash
   docker exec -it health-db psql -U healthuser -d healthdb \
     -c "ALTER USER healthuser WITH PASSWORD 'new-password';"
   ```
4. **Consider upgrading the Gemini models.** `extractor.py` starts on
   `gemini-2.5-flash-lite` and escalates to `gemini-2.5-pro-lite` — a model that
   may not exist, in which case that fallback branch has been failing. Confirm the
   current model IDs against the API before changing anything.

## Known drift

The Pi's `test_results.tokens_used` column already existed even though no
migration ever created it, so the live schema had drifted from the migration
history. It has been reconciled (the database is stamped at `c1d2e3f4a5b6`), but
if an upload throws an error about some *other* column, that is drift resurfacing.
