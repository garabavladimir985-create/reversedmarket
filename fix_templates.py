from pathlib import Path
import re

templates = Path("backend/templates")

nav_code = """<style>
.bottom-nav,.old-bottom-nav,.navbar{display:none!important}

body{
    padding-bottom:105px!important;
    overflow-x:hidden!important;
    background:#050816!important;
}

.premium-bottom-nav{
    position:fixed!important;
    left:50%!important;
    bottom:0!important;
    transform:translateX(-50%)!important;
    width:100%!important;
    max-width:430px!important;
    height:86px!important;
    background:rgba(17,24,39,.97)!important;
    backdrop-filter:blur(22px)!important;
    border-radius:28px 28px 0 0!important;
    display:flex!important;
    align-items:center!important;
    justify-content:space-around!important;
    padding:6px 8px!important;
    z-index:2147483647!important;
    box-sizing:border-box!important;
    overflow:visible!important;
    box-shadow:0 -10px 38px rgba(0,0,0,.55)!important;
}

.premium-nav-item{
    width:46px!important;
    min-width:46px!important;
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    justify-content:center!important;
    gap:4px!important;
    text-decoration:none!important;
    color:#8f96a8!important;
    font-size:10px!important;
    font-weight:500!important;
    line-height:1!important;
}

.premium-icon{
    font-size:22px!important;
    line-height:1!important;
}

.premium-nav-item.active{
    color:#3ea6ff!important;
}

.premium-shop-btn{
    width:70px!important;
    min-width:70px!important;
    margin-top:-42px!important;
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    justify-content:center!important;
    text-decoration:none!important;
    color:#8f96a8!important;
    font-size:10px!important;
    font-weight:500!important;
    gap:4px!important;
    line-height:1!important;
}

.premium-shop-circle{
    width:70px!important;
    height:70px!important;
    border-radius:50%!important;
    background:#3ea6ff!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    font-size:32px!important;
    border:7px solid #050816!important;
    box-shadow:0 0 32px rgba(62,166,255,.85)!important;
}

.premium-bottom-nav span{
    font-weight:500!important;
    text-decoration:none!important;
    white-space:nowrap!important;
}
</style>

<div class="premium-bottom-nav">
<a href="/" class="premium-nav-item"><div class="premium-icon">🏠</div><span>Главная</span></a>
<a href="/cart" class="premium-nav-item"><div class="premium-icon">🛒</div><span>Корзина</span></a>
<a href="/catalog" class="premium-nav-item"><div class="premium-icon">📁</div><span>Каталог</span></a>
<a href="/my-shop" class="premium-shop-btn"><div class="premium-shop-circle">💎</div><span>Shop</span></a>
<a href="/chat/general" class="premium-nav-item"><div class="premium-icon">💬</div><span>Чат</span></a>
<a href="/vip" class="premium-nav-item"><div class="premium-icon">👑</div><span>Вип</span></a>
<a href="/profile" class="premium-nav-item"><div class="premium-icon">👤</div><span>Профиль</span></a>
</div>
"""

(templates / "_nav.html").write_text(nav_code, encoding="utf-8")

for file in templates.glob("*.html"):
    if file.name == "_nav.html":
        continue

    text = file.read_text(encoding="utf-8")

    text = re.sub(
        r'<div class="premium-bottom-nav">.*?</div>\s*</div>',
        '',
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r'<div class="bottom-nav">.*?</div>',
        '',
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r'<nav class="bottom-nav">.*?</nav>',
        '',
        text,
        flags=re.DOTALL
    )

    text = text.replace('{% include "_nav.html" %}', '')

    if "</body>" in text:
        text = text.replace("</body>", '{% include "_nav.html" %}\n</body>')

    file.write_text(text, encoding="utf-8")

print("DONE: all templates now use _nav.html")