# 12/g — Encrypting fields with Fernet

Some columns are too sensitive to store as plain text, but you still
need to **read them back** (unlike a password). Here a customer's
`phone` and `notes` are encrypted with Fernet before they're saved and
decrypted when they're returned. A learning-only `/raw` route shows what
is actually in the database. No login in this lesson, to keep the focus
on encryption. See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`
and `encryption.py`. Table: `sec_customers`, seeded with two customers.

The app runs with a **dev-only** key hardcoded in `config.py`. For
anything real, generate your own key and put it in `.env` as
`FERNET_KEY=...`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Change the key **after** rows exist and those rows can't be decrypted
any more (see the last curl below).

```bash
cd example/12/g
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /customers` | Every customer, phone/notes decrypted |
| `GET /customers/{customer_id}` | One customer, decrypted; `404` if missing |
| `POST /customers` | Body `{"name", "email", "phone", "notes"?}`; encrypts, saves, `201` |
| `GET /customers/{customer_id}/raw` | **Learning only:** the row exactly as stored (ciphertext); `404` if missing |

Any route that decrypts answers `500 {"detail": "Could not decrypt stored data"}`
if the key doesn't match the data.

```bash
curl -X POST http://127.0.0.1:8000/customers -H "Content-Type: application/json" -d "{\"name\": \"Grace Hopper\", \"email\": \"grace@example.com\", \"phone\": \"555-0100\", \"notes\": \"Call after 5pm\"}"

curl http://127.0.0.1:8000/customers/3

curl http://127.0.0.1:8000/customers/3/raw
```

The second request returns `"phone": "555-0100"`. The third returns
something like:

```json
{"id": 3, "name": "Grace Hopper", "email": "grace@example.com",
 "phone_encrypted": "gAAAAABqw3syjOGnLeGjFcjWqi8JEwLP...", "notes_encrypted": "gAAAAABqw3sy..."}
```

**Try this too:** `POST` the same body again and compare the two `/raw`
results. Same phone, **different** ciphertext. Then stop the server,
set a freshly generated `FERNET_KEY` in `.env`, start it again and
`GET /customers`: `500`, and the terminal logs
`Could not decrypt a stored value ... Is FERNET_KEY the key the data was encrypted with?`.
Remove the line from `.env` and everything is readable again.

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/customers`, Body →
raw → JSON:

```json
{"name": "Grace Hopper", "email": "grace@example.com", "phone": "555-0100", "notes": "Call after 5pm"}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
