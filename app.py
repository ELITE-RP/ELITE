from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = "elite_rp_super_secret_key_change_me"

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
# Получите бесплатный ключ на https://steamcommunity.com/dev/apikey
STEAM_API_KEY = "YOUR_STEAM_WEB_API_KEY"

# Шаблоны встроены прямо в один файл для удобства запуска с телефона
INDEX_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ELITE RP — Игровой проект</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #0d0e12; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: #15171e; padding: 40px; border-radius: 12px; border: 1px solid #252836; text-align: center; max-width: 400px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #f39c12; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; font-size: 28px; }
        p { color: #8a8d9b; font-size: 14px; margin-bottom: 25px; line-height: 1.5; }
        .btn-steam { background: #171a21; color: #fff; padding: 12px 20px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; border: 1px solid #2a475e; width: 100%; transition: 0.2s; }
        .btn-steam:hover { background: #2a475e; border-color: #66c0f4; }
        .user-panel img { border-radius: 50%; width: 90px; height: 90px; border: 2px solid #f39c12; margin-bottom: 15px; }
        .user-panel h2 { font-size: 20px; margin-bottom: 15px; color: #fff; }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        .btn { padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; flex: 1; text-align: center; font-size: 14px; }
        .btn-profile { background: #f39c12; color: #000; }
        .btn-profile:hover { background: #e08e0b; }
        .btn-logout { background: #c0392b; color: #fff; }
        .btn-logout:hover { background: #a93226; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ELITE RP</h1>
        <p>Добро пожаловать на лучший игровой проект. Авторизуйтесь через Steam для входа в личный кабинет.</p>

        {% if user %}
            <div class="user-panel">
                <img src="{{ user.avatarfull }}" alt="Avatar">
                <h2>{{ user.personaname }}</h2>
                <div class="btn-group">
                    <a href="/profile" class="btn btn-profile">Кабинет</a>
                    <a href="/logout" class="btn btn-logout">Выйти</a>
                </div>
            </div>
        {% else %}
            <a href="/login" class="btn-steam">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                Войти через Steam
            </a>
        {% endif %}
    </div>
</body>
</html>
"""

PROFILE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Личный кабинет — ELITE RP</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #0d0e12; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: #15171e; padding: 40px; border-radius: 12px; border: 1px solid #252836; text-align: center; max-width: 400px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        img { border-radius: 50%; width: 100px; height: 100px; border: 2px solid #f39c12; margin-bottom: 15px; }
        h2 { font-size: 22px; margin-bottom: 5px; color: #fff; }
        p { color: #8a8d9b; font-size: 14px; margin-bottom: 20px; }
        .info-box { background: #1c1f2b; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: left; font-size: 13px; }
        .info-box div { margin-bottom: 8px; }
        .info-box span { color: #f39c12; font-weight: bold; }
        .btn { background: #f39c12; color: #000; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; display: block; text-align: center; transition: 0.2s; }
        .btn:hover { background: #e08e0b; }
    </style>
</head>
<body>
    <div class="container">
        <img src="{{ user.avatarfull }}" alt="Avatar">
        <h2>{{ user.personaname }}</h2>
        <p>Личный кабинет игрока</p>
        
        <div class="info-box">
            <div>SteamID: <span>{{ user.steamid }}</span></div>
            <div>Статус аккаунта: <span style="color: #2ecc71;">Авторизован</span></div>
            <div>Баланс: <span>0 ₽</span></div>
        </div>

        <a href="/" class="btn">На главную</a>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML, user=session.get("user"))

@app.route("/login")
def login():
    host = request.host
    return_url = f"http://{host}/authorized"
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_url,
        "openid.realm": f"http://{host}",
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return redirect(f"{STEAM_OPENID_URL}?{urllib.parse.urlencode(params)}")

@app.route("/authorized")
def authorized():
    args = request.args.to_dict()
    args["openid.mode"] = "check_authentication"
    response = requests.post(STEAM_OPENID_URL, data=args)

    if "is_valid:true" in response.text:
        claimed_id = args.get("openid.claimed_id")
        steam_id = claimed_id.split("/")[-1]

        player_data = {
            "steamid": steam_id,
            "personaname": "Elite Player",
            "avatarfull": "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
        }

        try:
            api_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}"
            api_response = requests.get(api_url).json()
            players = api_response.get("response", {}).get("players", [])
            if players:
                player_data["personaname"] = players[0].get("personaname")
                player_data["avatarfull"] = players[0].get("avatarfull")
        except Exception:
            pass

        session["user"] = player_data
        return redirect(url_for("profile"))

    return redirect(url_for("index"))

@app.route("/profile")
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("index"))
    return render_template_string(PROFILE_HTML, user=user)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
