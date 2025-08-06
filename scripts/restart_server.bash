pkill uv
source .venv/bin/activate
export $(cat catbot/.env|xargs)
uv run -m catbot.main &