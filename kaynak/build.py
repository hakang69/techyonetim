#!/usr/bin/env python3
"""techyonetim.com statik sayfa üreticisi.

kaynak/rehber/*.md dosyalarından public/rehber/ altındaki yazı sayfalarını,
rehber dizinini ve public/sitemap.xml dosyasını üretir. Dış bağımlılığı yoktur.

Kullanım:  python3 kaynak/build.py
"""
import datetime
import html
import json
import os
import re

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, "kaynak")
YAYIN = os.path.join(KOK, "public")
SITE = "https://techyonetim.com"
MARKA = "Tech Consultancy"
UNVAN = "Tech Yönetim ve Finansal Danışmanlık Ltd. Şti."
ADRES = "Cevizli Mah. Zuhal Cad. No: 46E, Ritim İstanbul A5 Blok D:4 Kat:2, 34846 Maltepe / İstanbul"
TELEFON = "+90 535 573 02 69"
EPOSTA = "info@techyonetim.com"
PAYLASIM_GORSELI = SITE + "/og-image.png"


def e(metin):
    return html.escape(metin, quote=True)


def tarih_tr(iso):
    return datetime.date.fromisoformat(iso).strftime("%d.%m.%Y")


def md_oku(yol):
    """Basit ön bilgi (--- anahtar: değer ---) ve gövde ayrıştırıcı."""
    metin = open(yol, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", metin, re.S)
    if not m:
        raise ValueError(f"Ön bilgi bulunamadı: {yol}")
    meta = {}
    for satir in m.group(1).splitlines():
        if satir.strip():
            anahtar, _, deger = satir.partition(":")
            meta[anahtar.strip()] = deger.strip()
    return meta, m.group(2)


def md_html(govde):
    """Desteklenen biçimler: paragraf, '## ara başlık', '- madde', '> dayanak notu'."""
    parcalar, liste = [], []

    def liste_kapat():
        if liste:
            parcalar.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in liste) + "</ul>")
            liste.clear()

    for blok in re.split(r"\n\s*\n", govde.strip()):
        satirlar = [s for s in blok.splitlines() if s.strip()]
        if all(s.startswith("- ") for s in satirlar):
            liste.extend(s[2:].strip() for s in satirlar)
            continue
        liste_kapat()
        ilk = satirlar[0]
        if ilk.startswith("## "):
            parcalar.append(f"<h2>{e(ilk[3:].strip())}</h2>")
        elif ilk.startswith("> "):
            parcalar.append(f'<p class="dayanak">{e(" ".join(s[2:].strip() for s in satirlar))}</p>')
        else:
            parcalar.append(f"<p>{e(' '.join(s.strip() for s in satirlar))}</p>")
    liste_kapat()
    return "\n".join(parcalar)


def json_ld(veri):
    return '<script type="application/ld+json">' + json.dumps(veri, ensure_ascii=False) + "</script>"


def sayfa(baslik, aciklama, yol, govde, ek_head="", og_turu="website", aktif=""):
    adres = SITE + yol

    def nav_link(href, ad):
        cur = ' aria-current="page"' if aktif == ad else ""
        return f'<a href="{href}"{cur}>{ad}</a>'

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(baslik)}</title>
<meta name="description" content="{e(aciklama)}">
<link rel="canonical" href="{adres}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<meta property="og:type" content="{og_turu}">
<meta property="og:locale" content="tr_TR">
<meta property="og:site_name" content="{MARKA}">
<meta property="og:title" content="{e(baslik)}">
<meta property="og:description" content="{e(aciklama)}">
<meta property="og:url" content="{adres}">
<meta property="og:image" content="{PAYLASIM_GORSELI}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(baslik)}">
<meta name="twitter:description" content="{e(aciklama)}">
<meta name="twitter:image" content="{PAYLASIM_GORSELI}">
<meta name="robots" content="index,follow">
{ek_head}
</head>
<body>
<header class="hdr">
  <div class="wrap">
    <a class="logo" href="/">TECH CONSULTANCY</a>
    <nav class="nav" aria-label="Ana menü">
      {nav_link("/#hizmetler", "Hizmetler")}
      {nav_link("/#surec", "Süreç")}
      {nav_link("/#uygunluk", "Uygunluk")}
      {nav_link("/#mevzuat", "Mevzuat")}
      {nav_link("/rehber/", "Rehber")}
      <a class="btn btn-p" href="/#iletisim">Durum analizi talep et</a>
    </nav>
  </div>
</header>
<main>
{govde}
</main>
<footer class="ftr">
  <div class="wrap">
    <div class="firma"><strong>{MARKA}</strong>{UNVAN}<br>{ADRES}<br>{TELEFON} · <a href="mailto:{EPOSTA}">{EPOSTA}</a></div>
    <nav aria-label="Alt menü">
      <a href="/#hizmetler">Hizmetler</a>
      <a href="/rehber/">Rehber</a>
      <a href="/#uygunluk">Uygunluk kontrolü</a>
      <a href="/#iletisim">İletişim</a>
      <a href="/#kvkk">KVKK Aydınlatma Metni</a>
      <a href="/#gizlilik">Gizlilik Politikası</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def yol_izi(ogeler):
    li = "".join(
        f'<li><a href="{href}">{e(ad)}</a></li>' if href else f'<li aria-current="page">{e(ad)}</li>'
        for ad, href in ogeler
    )
    return f'<nav class="crumbs" aria-label="Yol izi"><ol>{li}</ol></nav>'


def yol_izi_ld(ogeler):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": ad, "item": SITE + yol}
            for i, (ad, yol) in enumerate(ogeler)
        ],
    }


def yazi_sayfasi(meta, govde_md, ilgili):
    yol = f"/rehber/{meta['slug']}/"
    baslik = f"{meta['baslik']} | {MARKA}"
    makale_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta["baslik"],
        "description": meta["aciklama"],
        "inLanguage": "tr-TR",
        "datePublished": meta["yayin"],
        "dateModified": meta["guncelleme"],
        "author": {"@type": "Person", "name": meta["yazar"], "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": MARKA, "logo": {"@type": "ImageObject", "url": SITE + "/logo.png"}},
        "image": PAYLASIM_GORSELI,
        "mainEntityOfPage": SITE + yol,
    }
    izi = [("Ana sayfa", "/"), ("Rehber", "/rehber/"), (meta["kart_basligi"], yol)]
    ek_head = json_ld(makale_ld) + "\n" + json_ld(yol_izi_ld(izi))
    ilgili_html = ""
    if ilgili:
        linkler = "".join(
            f'<a href="/rehber/{m["slug"]}/"><strong>{e(m["kart_basligi"])}</strong><span>{e(m["aciklama"])}</span></a>'
            for m in ilgili
        )
        ilgili_html = f'<section class="ilgili" aria-label="İlgili yazılar"><h2>Aynı gruptan</h2>{linkler}</section>'
    cagri = meta.get("cagri") or "Şirketinize özel değerlendirme için bize ulaşın."
    govde = f"""<div class="wrap narrow">
{yol_izi([("Ana sayfa", "/"), ("Rehber", "/rehber/"), (meta["kart_basligi"], None)])}
<article class="art">
  <header class="art-head">
    <span class="pill">{e(meta["grup"])}</span>
    <h1>{e(meta["baslik"])}</h1>
    <p class="ozet">{e(meta["ozet"])}</p>
    <p class="art-meta">{e(meta["yazar"])} · Yayın: {tarih_tr(meta["yayin"])} · Güncelleme: {tarih_tr(meta["guncelleme"])}</p>
  </header>
  <div class="art-body">
{md_html(govde_md)}
  </div>
  <aside class="cagri">
    <p>{e(cagri)}</p>
    <a class="btn btn-p" href="/#iletisim">Durum analizi talep et</a>
  </aside>
  {ilgili_html}
</article>
</div>"""
    return yol, sayfa(baslik, meta["aciklama"], yol, govde, ek_head, og_turu="article", aktif="Rehber")


def rehber_dizini(gruplar, yazilar):
    yol = "/rehber/"
    bloklar = []
    for g in gruplar:
        linkler = "".join(
            f'<a class="grup-yazi" href="/rehber/{s}/"><strong>{e(yazilar[s]["kart_basligi"])}</strong>'
            f'<span>{e(yazilar[s]["aciklama"])}</span><em>Yazıyı oku →</em></a>'
            for s in g["yazilar"]
        )
        bloklar.append(
            f'<section class="grup"><div class="grup-bas"><span class="no">{e(g["no"])}</span>'
            f'<h2>{e(g["baslik"])}</h2><p>{e(g["aciklama"])}</p>'
            f'<a href="/#hizmetler">İlgili hizmet: {e(g["ilgili_hizmet"])} →</a></div>'
            f"<div>{linkler}</div></section>"
        )
    aciklama = "Teknopark, Ar-Ge Merkezi ve teşvik mevzuatını açıklayan, eşikleri gösteren ve riski adlandıran yazılar."
    izi = [("Ana sayfa", "/"), ("Rehber", yol)]
    liste_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Rehber",
        "url": SITE + yol,
        "inLanguage": "tr-TR",
        "hasPart": [{"@type": "Article", "headline": m["baslik"], "url": f"{SITE}/rehber/{s}/"} for s, m in yazilar.items()],
    }
    govde = f"""<div class="wrap">
{yol_izi([("Ana sayfa", "/"), ("Rehber", None)])}
<div class="sayfa-bas">
  <span class="eyebrow">Rehber</span>
  <h1>Karar vermeden önce okunacaklar</h1>
  <p class="lede">Mevzuatı açıklayan, eşikleri gösteren ve riski adlandıran içerikler. Üç grup, hizmet hatlarıyla aynı sırada ilerliyor.</p>
</div>
<div class="gruplar">
{"".join(bloklar)}
</div>
</div>"""
    ek_head = json_ld(liste_ld) + "\n" + json_ld(yol_izi_ld(izi))
    return yol, sayfa(f"Rehber: Teknopark ve Ar-Ge Teşvik Yazıları | {MARKA}", aciklama, yol, govde, ek_head, aktif="Rehber")


def site_haritasi(kayitlar):
    satirlar = "".join(
        f"  <url><loc>{SITE}{yol}</loc><lastmod>{tarih}</lastmod></url>\n" for yol, tarih in kayitlar
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{satirlar}</urlset>\n'


def yaz(yol, icerik):
    hedef = os.path.join(YAYIN, yol.strip("/"), "index.html") if yol.endswith("/") else os.path.join(YAYIN, yol.strip("/"))
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    with open(hedef, "w", encoding="utf-8") as f:
        f.write(icerik)
    return hedef


def main():
    rehber_dir = os.path.join(KAYNAK, "rehber")
    gruplar = json.load(open(os.path.join(rehber_dir, "gruplar.json"), encoding="utf-8"))
    yazilar = {}
    for ad in sorted(os.listdir(rehber_dir)):
        if ad.endswith(".md"):
            meta, govde = md_oku(os.path.join(rehber_dir, ad))
            yazilar[meta["slug"]] = dict(meta, _govde=govde)
    sirali = [s for g in gruplar for s in g["yazilar"]]
    eksik = set(yazilar) - set(sirali)
    if eksik:
        raise ValueError(f"gruplar.json içinde olmayan yazılar: {sorted(eksik)}")

    harita = [("/", max(m["guncelleme"] for m in yazilar.values()))]
    yol, icerik = rehber_dizini(gruplar, yazilar)
    print("yazıldı:", yaz(yol, icerik))
    harita.append((yol, max(m["guncelleme"] for m in yazilar.values())))
    for g in gruplar:
        for s in g["yazilar"]:
            ilgili = [yazilar[x] for x in g["yazilar"] if x != s]
            yol, icerik = yazi_sayfasi(yazilar[s], yazilar[s]["_govde"], ilgili)
            print("yazıldı:", yaz(yol, icerik))
            harita.append((yol, yazilar[s]["guncelleme"]))
    print("yazıldı:", yaz("/sitemap.xml", site_haritasi(harita)))


if __name__ == "__main__":
    main()
