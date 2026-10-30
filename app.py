# ============================================================
# Account Name Maker (single file)
# ランダムなアカウント名の候補を提案する小さな Web ツール。
# テーマ・キーワード・数字／区切りの有無を選ぶと、候補をまとめて出す。
# 各サービスで実際に使えるか（空き状況）は確認しない。
# ============================================================

# =========================
# [S1] WORD LISTS
# =========================
# テーマごとの単語リスト（すべて小文字ローマ字／英単語）。
THEMES = {
    "cute": [
        "mochi", "pudding", "sakura", "honey", "milky", "peach",
        "cocoa", "mimi", "lulu", "maru", "fuwa", "poko",
        "chibi", "usagi", "neko", "panda", "ringo", "ichigo",
    ],
    "cool": [
        "shadow", "blade", "nova", "vortex", "onyx", "raven",
        "zero", "storm", "wolf", "phantom", "eclipse", "drift",
        "falcon", "onyx2", "venom", "axis", "rogue", "night",
    ],
    "nature": [
        "sora", "umi", "hoshi", "tsuki", "kaze", "hana",
        "mori", "kawa", "ame", "yuki", "taiyo", "kumo",
        "leaf", "river", "ocean", "forest", "meadow", "stone",
    ],
    "stylish": [
        "lumi", "astra", "velo", "noir", "ciel", "aura",
        "bijou", "eclat", "muse", "opal", "serene", "vivid",
        "gloss", "prism", "silk", "azure", "ivory", "pearl",
    ],
    "game": [
        "quest", "pixel", "mana", "loot", "boss", "combo",
        "level", "sword", "shield", "magic", "dragon", "hero",
        "respawn", "guild", "arcade", "dungeon", "potion", "critical",
    ],
    "food": [
        "cocoa", "mocha", "chai", "latte", "soda", "ramen",
        "sushi", "curry", "pasta", "waffle", "donut", "cookie",
        "melon", "lemon", "mint", "butter", "cream", "miso",
    ],
    "space": [
        "astro", "cosmo", "luna", "solar", "orbit", "comet",
        "nebula", "galaxy", "meteor", "star", "moon", "planet",
        "rocket", "saturn", "vega", "altair", "polaris", "zenith",
    ],
}

# "onyx2" のような数字入り単語は数字オフ時に困るので除く
THEMES["cool"] = [w for w in THEMES["cool"] if w.isalpha()]

THEME_LABELS = {
    "random": "おまかせ（ランダム）",
    "cute": "かわいい",
    "cool": "かっこいい",
    "nature": "自然・和風ローマ字",
    "stylish": "おしゃれ",
    "game": "ゲーム風",
    "food": "食べ物・カフェ",
    "space": "宇宙・星",
}

SEPARATORS = {"auto": None, "underscore": "_", "dot": ".", "none": ""}
PREFIXES = ["the", "its", "hello", "just", "mr", "ms"]

# =========================
# [S2] GENERATION LOGIC
# =========================
import random
import re


def sanitize_keyword(raw: str) -> str:
    """キーワードをアカウント名に使える形（小文字英数と _ .）へ整える。"""
    word = (raw or "").strip().lower()
    word = re.sub(r"[^a-z0-9_.]", "", word)
    return word.strip("._")


def _sep_for(separator: str, rng: random.Random) -> str:
    if separator == "auto":
        return rng.choice(["", "_", "."])
    return SEPARATORS[separator]


def _one_name(theme: str, keyword: str, use_numbers: bool,
              separator: str, rng: random.Random) -> str:
    theme_name = theme
    if theme_name == "random":
        theme_name = rng.choice(sorted(THEMES))
    words = THEMES[theme_name]
    sep = _sep_for(separator, rng)

    if keyword:
        # キーワードあり: 半分はキーワード＋単語、残りはキーワード単体寄り
        pattern = rng.choice(["kw_word", "word_kw", "kw_only", "kw_word"])
        if pattern == "kw_word":
            base = keyword + sep + rng.choice(words)
        elif pattern == "word_kw":
            base = rng.choice(words) + sep + keyword
        else:
            base = keyword
    else:
        pattern = rng.choice(["two", "two", "one", "prefix_one"])
        if pattern == "two":
            a, b = rng.sample(words, 2)
            base = a + sep + b if sep else a + b
        elif pattern == "prefix_one":
            base = rng.choice(PREFIXES) + sep + rng.choice(words)
        else:
            base = rng.choice(words)

    if use_numbers and rng.random() < 0.4:
        base = base + str(rng.choice([rng.randint(2, 99),
                                       rng.randint(100, 999),
                                       rng.randint(2000, 2026)]))
    return base


def generate_names(theme: str = "random", keyword: str = "", count: int = 10,
                   use_numbers: bool = True, separator: str = "auto",
                   max_length: int = 30, seed=None) -> list:
    """候補を count 件、重複なしで生成する。"""
    if theme != "random" and theme not in THEMES:
        raise ValueError(f"unknown theme: {theme}")
    if separator not in SEPARATORS:
        raise ValueError(f"unknown separator: {separator}")
    if not isinstance(count, int) or count < 1 or count > 50:
        raise ValueError("count must be 1..50")
    if max_length < 4 or max_length > 64:
        raise ValueError("max_length must be 4..64")

    kw = sanitize_keyword(keyword)
    if keyword and keyword.strip() and not kw:
        raise ValueError("keyword has no usable characters")

    rng = random.Random(seed)
    names, seen = [], set()
    for _ in range(count * 60):
        if len(names) >= count:
            break
        name = _one_name(theme, kw, use_numbers, separator, rng)
        if len(name) > max_length or name in seen:
            continue
        if not use_numbers and any(c.isdigit() for c in name):
            continue
        seen.add(name)
        names.append(name)
    return names


# =========================
# [S3] WEB APP
# =========================
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Account Name Maker</title>
<style>
body{margin:0;background:#eef4fb;color:#16324f;font-family:sans-serif;}
main{max-width:720px;margin:0 auto;padding:24px 16px 48px;}
.card{background:#fff;border-radius:12px;padding:20px;margin:16px 0;
box-shadow:0 2px 8px rgba(22,50,79,.12);}
label{display:block;margin:12px 0 4px;font-weight:bold;}
input,select{padding:10px;font-size:1rem;width:100%;box-sizing:border-box;}
button{padding:12px 20px;font-size:1.05rem;background:#16324f;color:#fff;
border:0;border-radius:8px;cursor:pointer;width:100%;margin-top:16px;}
.name{font-size:1.2rem;padding:10px 8px;border-bottom:1px solid #dde6f0;
cursor:pointer;word-break:break-all;}
.name:last-child{border-bottom:0;}
.hint{color:#5a7186;font-size:.9rem;}
</style>
</head>
<body>
<main>
<h1>Account Name Maker</h1>
<p>ランダムなアカウント名の候補を提案するツールです。テーマや好きな言葉を選んで「候補を出す」を押してください。候補をタップするとコピーできます。</p>
<p class="hint">※ 候補が各サービスで実際に使えるか（空き状況）は確認していません。登録前にサービス側で確認してください。</p>

<div class="card">
<form method="post" action="/">
<label for="theme">テーマ</label>
<select id="theme" name="theme">
{% for key, label in theme_labels.items() %}
<option value="{{ key }}" {% if key == theme %}selected{% endif %}>{{ label }}</option>
{% endfor %}
</select>

<label for="keyword">好きな言葉（任意・英数字）</label>
<input id="keyword" name="keyword" value="{{ keyword }}" placeholder="例: cocoa">

<label for="count">候補の数</label>
<select id="count" name="count">
{% for n in [5, 10, 20, 30] %}
<option value="{{ n }}" {% if n == count %}selected{% endif %}>{{ n }}件</option>
{% endfor %}
</select>

<label for="separator">区切り</label>
<select id="separator" name="separator">
<option value="auto" {% if separator == 'auto' %}selected{% endif %}>おまかせ</option>
<option value="underscore" {% if separator == 'underscore' %}selected{% endif %}>アンダースコア _</option>
<option value="dot" {% if separator == 'dot' %}selected{% endif %}>ドット .</option>
<option value="none" {% if separator == 'none' %}selected{% endif %}>なし</option>
</select>

<label><input type="checkbox" name="use_numbers" value="1"
{% if use_numbers %}checked{% endif %} style="width:auto"> 数字をつける</label>

<button type="submit">候補を出す</button>
</form>
</div>

{% if names %}
<div class="card">
<h2>候補（タップでコピー）</h2>
{% for name in names %}
<div class="name" onclick="copyName(this)">{{ name }}</div>
{% endfor %}
<p class="hint" id="copied"></p>
</div>
{% endif %}
</main>
<script>
function copyName(el){
  const text = el.textContent.trim();
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(()=>{
      document.getElementById("copied").textContent = "コピーしました: " + text;
    }).catch(()=>{});
  }
}
</script>
</body>
</html>
"""


def _form_options():
    theme = request.form.get("theme", "random")
    keyword = request.form.get("keyword", "")
    separator = request.form.get("separator", "auto")
    use_numbers = request.form.get("use_numbers") == "1"
    try:
        count = int(request.form.get("count", "10"))
    except ValueError:
        count = 10
    if theme not in THEME_LABELS:
        theme = "random"
    if separator not in SEPARATORS:
        separator = "auto"
    if count not in (5, 10, 20, 30):
        count = 10
    return theme, keyword, count, use_numbers, separator


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        theme, keyword, count, use_numbers, separator = _form_options()
    else:
        theme, keyword, count, use_numbers, separator = "random", "", 10, True, "auto"
    try:
        names = generate_names(theme=theme, keyword=keyword, count=count,
                               use_numbers=use_numbers, separator=separator)
    except ValueError:
        names = generate_names(count=count)
    return render_template_string(
        HTML, names=names, theme=theme, keyword=keyword, count=count,
        use_numbers=use_numbers, separator=separator,
        theme_labels=THEME_LABELS)


@app.route("/api/generate")
def api_generate():
    theme = request.args.get("theme", "random")
    keyword = request.args.get("keyword", "")
    separator = request.args.get("separator", "auto")
    use_numbers = request.args.get("numbers", "1") not in ("0", "false", "no")
    seed = request.args.get("seed")
    try:
        count = int(request.args.get("count", "10"))
        max_length = int(request.args.get("max_length", "30"))
    except ValueError:
        return jsonify({"error": "count and max_length must be integers"}), 400
    try:
        names = generate_names(theme=theme, keyword=keyword, count=count,
                               use_numbers=use_numbers, separator=separator,
                               max_length=max_length,
                               seed=int(seed) if seed is not None else None)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"names": names, "count": len(names), "theme": theme})


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    import os
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
