# ACTR Lab — Gas Station Game Platform

Flask + Socket.IO web app for live research sessions: team chat, pricing games, admin controls, AI bots and match analysis.

**Production:** [game.xjhuang.com](https://game.xjhuang.com) · **Repo:** [github.com/xjhuang99/game2](https://github.com/xjhuang99/game2)

## Requirements

- Python 3.10+
- **LLM:** [OpenAI API key](https://platform.openai.com/api-keys) and/or [DeepSeek API key](https://platform.deepseek.com/) — OpenAI is tried first; DeepSeek (`deepseek-chat`) is used automatically if OpenAI fails
- **Registration:** Gmail account with [App Password](https://myaccount.google.com/apppasswords) for SMTP

## Setup

```bash
git clone https://github.com/xjhuang99/game2.git
cd game2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — see sections below
python app.py
```

Open **http://localhost:5001** — you will land on the sign-in page (or your `PORT`).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Primary chat API for bots & analysis |
| `DEEPSEEK_API_KEY` | Fallback chat API (`deepseek-chat`) |
| `APP_BASE_URL` | Public URL for email verify links (e.g. `https://game.xjhuang.com`) |
| `SMTP_USER` / `SMTP_PASSWORD` | Gmail SMTP for registration emails |
| `SECRET_KEY` | Flask session secret (required in production) |
| `PORT` | Server port (default `5001`) |

## Admin access

| Method | How |
|--------|-----|
| **Register** | `/register` → Gmail 验证邮件 → 点击链接 → `/login` |
| **Legacy** | `LEGACY_ADMIN_USER` / `LEGACY_ADMIN_PASSWORD` (default `ACTR2026` / `ACTR2026`) |

未验证邮箱的账号无法登录；注册成功后会看到「请查收 Gmail」页面，验证成功页会提示可登录。

## URLs

| Path | Purpose |
|------|---------|
| `/` | Sign in (or dashboard if logged in) |
| `/login` | Admin sign in |
| `/register` | Create account |
| `/admin` | Session management |
| `/game/<session_code>` | Participant join |

## Deploy to game.xjhuang.com

1. Server with Python 3.10+, reverse proxy (Nginx/Caddy) → `127.0.0.1:5001`
2. Set `.env`: `APP_BASE_URL=https://game.xjhuang.com`, strong `SECRET_KEY`, API keys, Gmail SMTP
3. Process manager example (systemd):

```ini
[Service]
WorkingDirectory=/var/www/game2
EnvironmentFile=/var/www/game2/.env
ExecStart=/var/www/game2/.venv/bin/python app.py
Restart=always
```

4. Nginx WebSocket headers for Socket.IO:

```nginx
location / {
    proxy_pass http://127.0.0.1:5001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

5. HTTPS via Let’s Encrypt on the domain.

## LLM behavior

- Bots (`bot_service.py`) and analysis (`analysis_service.py`) use `llm_service.py`
- Model names in `bots_config.json` (e.g. `gpt-4o`) map to `deepseek-chat` when falling back to DeepSeek

## Project layout

```
llm_service.py       # OpenAI → DeepSeek fallback
email_service.py     # Gmail verification mail
bot_service.py       # In-game AI bots
analysis_service.py  # Match analysis & coaching
models.py            # DB models incl. AdminAccount
```

## Troubleshooting

- **No AI responses:** Set at least one of `OPENAI_API_KEY` or `DEEPSEEK_API_KEY`
- **Registration email not received:** Check Gmail App Password, spam folder, and `APP_BASE_URL`
- **Verify link wrong host:** `APP_BASE_URL` must match your public HTTPS URL
