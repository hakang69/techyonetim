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


def satir_ici(metin):
    """Satır içi biçimler: **kalın** ve [metin](/site-ici-adres/). Dış adrese bağlantı kabul edilmez."""
    s = e(metin)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\((/[^)\s]*)\)", r'<a href="\2">\1</a>', s)
    return s


def md_html(govde):
    """Desteklenen biçimler: paragraf, '## ara başlık', '- madde', '> dayanak notu', satır içi **kalın** ve [bağlantı](/adres/)."""
    parcalar, liste = [], []

    def liste_kapat():
        if liste:
            parcalar.append("<ul>" + "".join(f"<li>{satir_ici(x)}</li>" for x in liste) + "</ul>")
            liste.clear()

    for blok in re.split(r"\n\s*\n", govde.strip()):
        satirlar = [s for s in blok.splitlines() if s.strip()]
        if all(s.startswith("|") for s in satirlar):
            liste_kapat()
            satirlar = [s for s in satirlar if not re.match(r"^\|\s*:?-{3,}", s)]
            hucreler = [[c.strip() for c in s.strip().strip("|").split("|")] for s in satirlar]
            bas = "".join(f"<th>{satir_ici(c)}</th>" for c in hucreler[0])
            gov = "".join("<tr>" + "".join(f"<td>{satir_ici(c)}</td>" for c in r) + "</tr>" for r in hucreler[1:])
            parcalar.append(f'<div class="tablo"><table><thead><tr>{bas}</tr></thead><tbody>{gov}</tbody></table></div>')
            continue
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
            parcalar.append(f"<p>{satir_ici(' '.join(s.strip() for s in satirlar))}</p>")
    liste_kapat()
    return "\n".join(parcalar)


def json_ld(veri):
    return '<script type="application/ld+json">' + json.dumps(veri, ensure_ascii=False) + "</script>"


def sayfa(baslik, aciklama, yol, govde, ek_head="", og_turu="website", aktif="", robots="index,follow"):
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
<meta name="robots" content="{robots}">
{ek_head}
</head>
<body>
<header class="hdr">
  <div class="wrap">
    <a class="logo" href="/">TECH CONSULTANCY</a>
    <nav class="nav" aria-label="Ana menü">
      {nav_link("/hizmetler/", "Hizmetler")}
      {nav_link("/#surec", "Süreç")}
      {nav_link("/uygunluk-kontrolu/", "Uygunluk")}
      {nav_link("/mevzuat-gundemi/", "Mevzuat")}
      {nav_link("/rehber/", "Rehber")}
      {nav_link("/hakkimizda/", "Hakkımızda")}
      <a class="btn btn-p" href="/iletisim/">Durum analizi talep et</a>
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
      <a href="/teknoparka-gecis/">Teknoparka geçiş</a>
      <a href="/geleneksel-sirketler-icin-teknopark/">Geleneksel şirketler için teknopark</a>
      <a href="/teknoparktaki-sirketler/">Teknoparktaki şirketler</a>
      <a href="/hizmetler/">Hizmetler</a>
      <a href="/uygunluk-kontrolu/">Uygunluk kontrolü</a>
      <a href="/teknopark-tesvikleri/">Teknopark teşvikleri</a>
      <a href="/mevzuat-gundemi/">Mevzuat gündemi</a>
      <a href="/rehber/">Rehber</a>
      <a href="/hakkimizda/">Hakkımızda</a>
      <a href="/iletisim/">İletişim</a>
      <a href="/kvkk/">KVKK Aydınlatma Metni</a>
      <a href="/gizlilik/">Gizlilik Politikası</a>
    </nav>
    <div class="telif">© {datetime.date.today().year} {UNVAN} Tüm hakları saklıdır.</div>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
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
    <a class="btn btn-p" href="/iletisim/">Durum analizi talep et</a>
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
            f'<a href="{e(g.get("ilgili_hizmet_yol", "/hizmetler/"))}">İlgili hizmet: {e(g["ilgili_hizmet"])} →</a></div>'
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


def parca(ad):
    return open(os.path.join(KAYNAK, "sayfalar", ad), encoding="utf-8").read()


FIRMA_LD = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": MARKA,
    "legalName": UNVAN,
    "description": "Teknopark başvurusu, Ar-Ge ve Tasarım Merkezi kurulumu, portal raporlama ve istisna uyumu. 20 yıllık teknopark ekosistemi deneyimiyle uçtan uca teşvik yönetimi.",
    "url": SITE + "/",
    "logo": SITE + "/logo.png",
    "image": PAYLASIM_GORSELI,
    "telephone": TELEFON,
    "email": EPOSTA,
    "areaServed": "TR",
    "address": {"@type": "PostalAddress", "streetAddress": "Cevizli Mah. Zuhal Cad. No: 46E, Ritim İstanbul A5 Blok D:4 Kat:2",
                "addressLocality": "Maltepe", "addressRegion": "İstanbul", "postalCode": "34846", "addressCountry": "TR"},
    "knowsAbout": ["Teknopark danışmanlığı", "Ar-Ge Merkezi", "Tasarım Merkezi", "4691 sayılı Kanun", "5746 sayılı Kanun",
                   "Ar-Ge teşvikleri", "Portal raporlama"],
}
SITE_LD = {"@context": "https://schema.org", "@type": "WebSite", "name": MARKA,
           "alternateName": ["Tech Yönetim", "techyonetim.com"], "url": SITE + "/", "inLanguage": "tr-TR"}

ANA_SAYFA_PARCALARI = ["01-giris.html", "02-hizmetler.html", "03-surec.html", "04-kim-icin.html", "05-uygunluk-ozet.html",
                       "06-tesvikler.html", "07-mevzuat.html", "08-rehber.html", "09-danismanlar.html",
                       "09b-gizlilik-ilkemiz.html", "10-iletisim.html"]


def segment_sayfasi(meta, govde_md, yazilar):
    """Hedef kitle (segment) sayfası: koyu giriş, gövde metni, başlangıç çalışması kutusu, ilgili yazılar."""
    yol = f"/{meta['slug']}/"
    izi = [("Ana sayfa", "/"), (meta["kirinti"], yol)]
    kapsam = "".join(f"<li>{e(x.strip())}</li>" for x in meta["urun_kapsam"].split("|"))
    ilgili = [yazilar[s.strip()] for s in meta.get("ilgili", "").split(",") if s.strip()]
    ilgili_html = ""
    if ilgili:
        linkler = "".join(
            f'<a href="/rehber/{m["slug"]}/"><strong>{e(m["kart_basligi"])}</strong><span>{e(m["aciklama"])}</span></a>'
            for m in ilgili
        )
        ilgili_html = f'<section class="ilgili" aria-label="İlgili yazılar"><h2>Konuyla ilgili yazılar</h2>{linkler}</section>'
    hizmet_ld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": meta["urun_adi"],
        "serviceType": meta["kirinti"],
        "description": meta["aciklama"],
        "url": SITE + yol,
        "areaServed": "TR",
        "inLanguage": "tr-TR",
        "provider": {"@type": "ProfessionalService", "name": MARKA, "url": SITE + "/"},
    }
    govde = f"""<div class="wrap narrow">
{yol_izi([("Ana sayfa", "/"), (meta["kirinti"], None)])}
<article class="art seg">
  <header class="art-head">
    <span class="pill">{e(meta["eyebrow"])}</span>
    <h1>{e(meta["baslik"])}</h1>
    <p class="ozet">{e(meta["lede"])}</p>
    <div class="seg-cta">
      <a class="btn btn-a" href="/iletisim/">Durum analizi talep et</a>
      <a class="btn btn-g" href="/uygunluk-kontrolu/">Uygunluğunuzu kontrol edin</a>
    </div>
  </header>
  <div class="art-body">
{md_html(govde_md)}
  </div>
  <section class="urun" aria-label="Başlangıç çalışması">
    <span class="urun-etiket">Başlangıç çalışması</span>
    <h2>{e(meta["urun_adi"])}</h2>
    <p>{e(meta["urun_ozet"])}</p>
    <h3>Kapsam</h3>
    <ul>{kapsam}</ul>
    <dl>
      <div><dt>Çıktı</dt><dd>{e(meta["urun_cikti"])}</dd></div>
      <div><dt>Süre</dt><dd>{e(meta["urun_sure"])}</dd></div>
    </dl>
  </section>
  <aside class="cagri">
    <p>{e(meta["cagri"])}</p>
    <a class="btn btn-p" href="/iletisim/">Durum analizi talep et</a>
  </aside>
  <p class="gizlilik-not"><strong>Gizlilik ilkemiz:</strong> Çalıştığımız şirketlerin adını ve projelerini hiçbir yerde paylaşmayız. <a href="/#gizlilik-ilkemiz">Neden?</a></p>
  {ilgili_html}
</article>
</div>"""
    ek_head = json_ld(hizmet_ld) + "\n" + json_ld(yol_izi_ld(izi))
    return yol, sayfa(f"{meta['seo_basligi']} | {MARKA}", meta["aciklama"], yol, govde, ek_head)


KART_STIL = ("border-radius: 22px; background: var(--surface); padding: 32px 32px 30px; display: flex; flex-direction: column; "
             "box-shadow: rgba(22, 35, 58, 0.04) 0px 1px 2px, rgba(22, 35, 58, 0.16) 0px 14px 34px -16px; "
             "transition: transform 0.28s cubic-bezier(0.22, 0.61, 0.36, 1), box-shadow 0.28s cubic-bezier(0.22, 0.61, 0.36, 1), background 0.28s;")
HARF_STIL = ("display: flex; width: 42px; height: 42px; border-radius: 999px; background: rgb(244, 236, 228); color: rgb(138, 90, 60); "
             "align-items: center; justify-content: center; font-family: &quot;Source Serif 4&quot;, Georgia, serif; font-size: 20px; "
             "line-height: 1; margin-bottom: 18px;")


def hizmetleri_oku():
    """kaynak/hizmetler/: dizin.md (hizmetler sayfasının metni) ve 'sira' alanına göre dizilen hizmet dosyaları."""
    d = os.path.join(KAYNAK, "hizmetler")
    dizin = md_oku(os.path.join(d, "dizin.md"))
    hizmetler = []
    for ad in os.listdir(d):
        if ad.endswith(".md") and ad != "dizin.md":
            meta, govde = md_oku(os.path.join(d, ad))
            hizmetler.append(dict(meta, _govde=govde))
    return dizin, sorted(hizmetler, key=lambda m: int(m["sira"]))


def hizmet_karti(m):
    aciklama = satir_ici(m["kart_aciklama"]).replace("<strong>", '<strong style="color: var(--accent); font-weight: 700;">')
    maddeler = "".join(
        '<div style="display: flex; gap: 12px; font-size: 14.5px; line-height: 1.5; padding: 5px 0px; color: var(--text);">'
        '<span aria-hidden="true" style="flex: 0 0 auto; width: 11px; height: 1.5px; background: var(--accent); margin-top: 10px;"></span>'
        f"<span>{e(x.strip())}</span></div>"
        for x in m["kart_maddeler"].split("|")
    )
    not_ = ""
    if m.get("kart_not"):
        not_ = ('<p style="margin: 16px 0px 0px; font-size: 13px; line-height: 1.6; color: rgb(138, 90, 60); '
                f'background: rgb(244, 236, 228); border-radius: 14px; padding: 14px 16px;">{e(m["kart_not"])}</p>')
    return (
        f'<div data-c="svccard" class="scp0" style="{KART_STIL}">'
        f'<span style="{HARF_STIL}">{e(m["harf"])}</span>'
        '<h3 data-c="svctitle" style="font-size: 23px; font-weight: 600; line-height: 1.24; margin: 0px 0px 10px; '
        f'letter-spacing: -0.012em; min-height: 2.48em;">{e(m["kart_basligi"])}</h3>'
        '<p data-c="svcdesc" style="font-size: 14.5px; color: var(--muted); line-height: 1.62; margin: 0px 0px 18px; '
        f'min-height: 8.2em;">{aciklama}</p>'
        '<div data-c="svclist" style="display: flex; flex-direction: column; gap: 1px; border-top: 1px solid var(--hair); '
        f'padding-top: 16px;">{maddeler}</div>{not_}'
        f'<a class="kart-link" style="margin-top: auto; padding-top: 18px;" href="/hizmetler/{m["slug"]}/" '
        f'aria-label="{e(m["kart_basligi"])}: ayrıntılar">Ayrıntılar →</a></div>'
    )


def hizmet_kartlari(hizmetler):
    return ('<div data-r="svcgrid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 40px;">'
            + "".join(hizmet_karti(m) for m in hizmetler) + "</div>")


def hizmet_sayfasi(m, yazilar, hizmetler):
    yol = f"/hizmetler/{m['slug']}/"
    izi = [("Ana sayfa", "/"), ("Hizmetler", "/hizmetler/"), (m["kart_basligi"], yol)]
    kapsam = "".join(f"<li>{e(x.strip())}</li>" for x in m["kart_maddeler"].split("|"))
    kart_not = f'<p>{e(m["kart_not"])}</p>' if m.get("kart_not") else ""
    ilgili = [yazilar[s.strip()] for s in m.get("ilgili", "").split(",") if s.strip()]
    ilgili_html = ""
    if ilgili:
        linkler = "".join(
            f'<a href="/rehber/{y["slug"]}/"><strong>{e(y["kart_basligi"])}</strong><span>{e(y["aciklama"])}</span></a>'
            for y in ilgili
        )
        ilgili_html = f'<section class="ilgili" aria-label="İlgili yazılar"><h2>Konuyla ilgili yazılar</h2>{linkler}</section>'
    diger = "".join(
        f'<a href="/hizmetler/{h["slug"]}/"><strong>{e(h["harf"])} · {e(h["kart_basligi"])}</strong><span>{e(h["aciklama"])}</span></a>'
        for h in hizmetler if h["slug"] != m["slug"]
    )
    hizmet_ld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": m["kart_basligi"],
        "serviceType": m["kart_basligi"],
        "description": m["aciklama"],
        "url": SITE + yol,
        "areaServed": "TR",
        "inLanguage": "tr-TR",
        "provider": {"@type": "ProfessionalService", "name": MARKA, "url": SITE + "/"},
    }
    govde = f"""<div class="wrap narrow">
{yol_izi([("Ana sayfa", "/"), ("Hizmetler", "/hizmetler/"), (m["kart_basligi"], None)])}
<article class="art seg">
  <header class="art-head">
    <span class="pill">Hizmet {e(m["harf"])}</span>
    <h1>{e(m["baslik"])}</h1>
    <p class="ozet">{e(m["lede"])}</p>
    <div class="seg-cta">
      <a class="btn btn-a" href="/iletisim/">Durum analizi talep et</a>
      <a class="btn btn-g" href="/uygunluk-kontrolu/">Uygunluğunuzu kontrol edin</a>
    </div>
  </header>
  <section class="urun" aria-label="Kapsam">
    <span class="urun-etiket">Kapsam</span>
    <ul style="margin-top: 16px;">{kapsam}</ul>
    {kart_not}
  </section>
  <div class="art-body">
{md_html(m["_govde"])}
  </div>
  <aside class="cagri">
    <p>{e(m["cagri"])}</p>
    <a class="btn btn-p" href="/iletisim/">Durum analizi talep et</a>
  </aside>
  <p class="gizlilik-not"><strong>Gizlilik ilkemiz:</strong> Çalıştığımız şirketlerin adını ve projelerini hiçbir yerde paylaşmayız. <a href="/#gizlilik-ilkemiz">Neden?</a></p>
  {ilgili_html}
  <section class="ilgili" aria-label="Diğer hizmetler"><h2>Diğer hizmetler</h2>{diger}</section>
</article>
</div>"""
    ek_head = json_ld(hizmet_ld) + "\n" + json_ld(yol_izi_ld(izi))
    return yol, sayfa(f"{m['seo_basligi']} | {MARKA}", m["aciklama"], yol, govde, ek_head, aktif="Hizmetler")


def hizmet_dizini(dizin, hizmetler):
    meta, govde_md = dizin
    yol = "/hizmetler/"
    izi = [("Ana sayfa", "/"), ("Hizmetler", yol)]
    liste_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Hizmetler",
        "url": SITE + yol,
        "inLanguage": "tr-TR",
        "hasPart": [{"@type": "Service", "name": h["kart_basligi"], "url": f"{SITE}/hizmetler/{h['slug']}/"} for h in hizmetler],
    }
    govde = f"""<div class="wrap">
{yol_izi([("Ana sayfa", "/"), ("Hizmetler", None)])}
<div class="sayfa-bas">
  <span class="eyebrow">Hizmetler</span>
  <h1>{e(meta["baslik"])}</h1>
  <p class="lede">{e(meta["lede"])}</p>
</div>
{hizmet_kartlari(hizmetler)}
</div>
<div class="wrap narrow" style="padding-bottom: 72px;">
<article class="art">
  <div class="art-body" style="padding-top: 24px;">
{md_html(govde_md)}
  </div>
  <aside class="cagri">
    <p>Hangi hattan başlamanız gerektiğini ilk görüşmede birlikte belirleyelim.</p>
    <a class="btn btn-p" href="/iletisim/">Durum analizi talep et</a>
  </aside>
</article>
</div>"""
    ek_head = json_ld(liste_ld) + "\n" + json_ld(yol_izi_ld(izi))
    return yol, sayfa(f"{meta['seo_basligi']} | {MARKA}", meta["aciklama"], yol, govde, ek_head, aktif="Hizmetler")


def icerik_sayfasi(m, yazilar):
    """Bilgi sayfası (teşvikler, mevzuat gündemi): yol izi, başlık, güncelleme tarihi, gövde, çağrı, ilgili yazılar."""
    yol = f"/{m['slug']}/"
    izi = [("Ana sayfa", "/"), (m["kirinti"], yol)]
    ilgili = [yazilar[s.strip()] for s in m.get("ilgili", "").split(",") if s.strip()]
    ilgili_html = ""
    if ilgili:
        linkler = "".join(
            f'<a href="/rehber/{y["slug"]}/"><strong>{e(y["kart_basligi"])}</strong><span>{e(y["aciklama"])}</span></a>'
            for y in ilgili
        )
        ilgili_html = f'<section class="ilgili" aria-label="İlgili yazılar"><h2>Konuyla ilgili yazılar</h2>{linkler}</section>'
    sayfa_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": m["baslik"],
        "description": m["aciklama"],
        "url": SITE + yol,
        "inLanguage": "tr-TR",
        "dateModified": m["guncelleme"],
        "publisher": {"@type": "Organization", "name": MARKA, "logo": {"@type": "ImageObject", "url": SITE + "/logo.png"}},
    }
    govde = f"""<div class="wrap narrow">
{yol_izi([("Ana sayfa", "/"), (m["kirinti"], None)])}
<article class="art">
  <header class="art-head">
    <span class="pill">{e(m["eyebrow"])}</span>
    <h1>{e(m["baslik"])}</h1>
    <p class="ozet">{e(m["lede"])}</p>
    <p class="art-meta">Güncelleme: {tarih_tr(m["guncelleme"])}</p>
  </header>
  <div class="art-body">
{md_html(m["_govde"])}
  </div>
  <aside class="cagri">
    <p>{e(m["cagri"])}</p>
    <a class="btn btn-p" href="/iletisim/">Durum analizi talep et</a>
  </aside>
  {ilgili_html}
</article>
</div>"""
    ek_head = json_ld(sayfa_ld) + "\n" + json_ld(yol_izi_ld(izi))
    return yol, sayfa(f"{m['seo_basligi']} | {MARKA}", m["aciklama"], yol, govde, ek_head, aktif=m.get("aktif", ""))


def ana_sayfa(hizmetler):
    baslik = f"Teknopark Danışmanlığı ve Ar-Ge Teşvik Yönetimi | {MARKA}"
    govde = "\n".join(parca(p) for p in ANA_SAYFA_PARCALARI)
    if "{{HIZMET_KARTLARI}}" not in govde:
        raise ValueError("02-hizmetler.html içinde {{HIZMET_KARTLARI}} yer tutucusu yok")
    govde = govde.replace("{{HIZMET_KARTLARI}}", hizmet_kartlari(hizmetler))
    return "/", sayfa(baslik, FIRMA_LD["description"], "/", govde, json_ld(FIRMA_LD) + "\n" + json_ld(SITE_LD))


def bolum_sayfasi(yol, baslik, aciklama, kirinti, parca_adi, aktif="", robots="index,follow", ek=""):
    izi = [("Ana sayfa", "/"), (kirinti, yol)]
    govde = (f'<div class="wrap sayfa-izi">{yol_izi([("Ana sayfa", "/"), (kirinti, None)])}</div>\n'
             + parca(parca_adi) + ek)
    ek_head = json_ld(yol_izi_ld(izi))
    return yol, sayfa(f"{baslik} | {MARKA}", aciklama, yol, govde, ek_head, aktif=aktif, robots=robots)


def ozgecmis_html(anahtar, cv, foto):
    def liste(ogeler):
        return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in ogeler) + "</ul>" if ogeler else ""

    isler = "".join(
        f'<div class="cv-is"><strong>{e(x["role"])}</strong><span class="yer">{e(x["place"])}</span>'
        f'<span class="tarih">{e(x.get("period", ""))}</span>' + (f'<p>{e(x["desc"])}</p>' if x.get("desc") else "") + "</div>"
        for x in cv.get("experience", [])
    )
    egitim = "".join(
        f'<div class="cv-is"><strong>{e(x["role"])}</strong><span class="yer">{e(x["place"])}</span>'
        f'<span class="tarih">{e(x.get("period", ""))}</span></div>'
        for x in cv.get("education", [])
    )
    iletisim = " · ".join(
        f'<a href="tel:{re.sub(r"[^0-9+]", "", c)}">{e(c)}</a>' if re.match(r"^\+?[\d\s()-]+$", c) else e(c)
        for c in cv.get("contact", [])
    )
    cipler = "".join(f"<span>{e(x)}</span>" for x in cv.get("skills", []))
    sag = ""
    if cv.get("licenses"):
        sag += f"<h3>Lisanslar ve belgeler</h3>{liste(cv['licenses'])}"
    if cv.get("orgs"):
        sag += f"<h3>Kuruluşlar ve kurullar</h3>{liste(cv['orgs'])}"
    if cipler:
        sag += f'<h3>Yetkinlikler</h3><div class="cipler">{cipler}</div>'
    if egitim:
        sag += f"<h3>Eğitim</h3>{egitim}"
    return f"""<article class="cv" id="ozgecmis-{anahtar}">
  <div class="cv-bas">
    <span class="rol">{e(cv.get("role", ""))}</span>
    <h2>{e(cv["name"])}</h2>
    <p class="unvan">{e(cv.get("title", ""))}</p>
    {f'<p class="ozet">{e(cv["summary"])}</p>' if cv.get("summary") else ""}
    {f'<p class="ozet">{iletisim}</p>' if iletisim else ""}
  </div>
  <div class="cv-govde">
    <div><h3>Deneyim</h3>{isler}</div>
    <div>{sag}</div>
  </div>
</article>"""


def hakkimizda():
    yol = "/hakkimizda/"
    cvler = json.load(open(os.path.join(KAYNAK, "ozgecmis.json"), encoding="utf-8"))
    fotolar = {"hakan": "/assets/img/hakan-gumus.jpg", "sule": "/assets/img/sule-tunc-gumus.jpg"}
    ozgecmisler = "".join(ozgecmis_html(k, v, fotolar.get(k)) for k, v in cvler.items())
    ek = f'<div class="sec"><div class="wrap" style="padding-top: 0;">{ozgecmisler}</div></div>\n' + parca("09b-gizlilik-ilkemiz.html")
    kisiler = [{"@type": "Person", "name": v["name"], "jobTitle": v.get("title", ""), "image": SITE + fotolar[k],
                "worksFor": {"@type": "Organization", "name": MARKA, "url": SITE + "/"}} for k, v in cvler.items()]
    yol, html_ = bolum_sayfasi(yol, "Hakkımızda: Danışmanlarımız",
                               "Teknopark mevzuatı, teşvik yönetimi ve kurumsal gelişim deneyimini bir arada taşıyan kurucu ortaklar: Hakan Gümüş ve Şule Tunç Gümüş, PhD.",
                               "Hakkımızda", "hakkimizda-ust.html", aktif="Hakkımızda", ek=ek)
    ld = json_ld({"@context": "https://schema.org", "@type": "AboutPage", "url": SITE + yol, "inLanguage": "tr-TR",
                  "about": {"@type": "Organization", "name": MARKA, "url": SITE + "/", "member": kisiler}})
    return yol, html_.replace("</head>", ld + "\n</head>", 1)


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

    dizin, hizmetler = hizmetleri_oku()
    bugun = datetime.date.today().isoformat()
    harita = []
    sayfalar = [
        ana_sayfa(hizmetler),
        bolum_sayfasi("/uygunluk-kontrolu/", "Teknopark ve Ar-Ge Merkezi Uygunluk Kontrolü",
                      "Dört soruda Teknopark, Ar-Ge Merkezi ve Tasarım Merkezi eşiklerini kontrol edin. Cevaplarınız hiçbir yere gönderilmez, tarayıcınızdan çıkmaz.",
                      "Uygunluk kontrolü", "uygunluk.html", aktif="Uygunluk"),
        hakkimizda(),
        bolum_sayfasi("/iletisim/", "İletişim: Durum Analizi Talep Edin",
                      "Teknopark, Ar-Ge ve Tasarım Merkezi ile teşvik mevzuatı konusunda durum analizi talep edin. Ritim İstanbul, Maltepe. İki iş günü içinde dönüş.",
                      "İletişim", "iletisim.html"),
    ]
    for yol, icerik in sayfalar:
        print("yazıldı:", yaz(yol, icerik))
        harita.append((yol, bugun))
    for yol, baslik, aciklama, kirinti, ad in [
        ("/kvkk/", "KVKK Aydınlatma Metni", "Tech Yönetim ve Finansal Danışmanlık Ltd. Şti. kişisel verilerin korunması aydınlatma metni.", "KVKK Aydınlatma Metni", "kvkk.html"),
        ("/gizlilik/", "Gizlilik Politikası", "techyonetim.com gizlilik politikası: çerez, izleme aracı ve dış kaynak kullanımı.", "Gizlilik Politikası", "gizlilik.html"),
    ]:
        yol, icerik = bolum_sayfasi(yol, baslik, aciklama, kirinti, ad, robots="noindex,follow")
        print("yazıldı:", yaz(yol, icerik))
    segment_dir = os.path.join(KAYNAK, "segmentler")
    segmentler = sorted((md_oku(os.path.join(segment_dir, ad)) for ad in os.listdir(segment_dir) if ad.endswith(".md")),
                        key=lambda x: int(x[0]["sira"]))
    for meta, govde in segmentler:
        yol, icerik = segment_sayfasi(meta, govde, yazilar)
        print("yazıldı:", yaz(yol, icerik))
        harita.append((yol, meta["guncelleme"]))
    icerik_dir = os.path.join(KAYNAK, "icerik")
    for ad in sorted(os.listdir(icerik_dir)):
        if ad.endswith(".md"):
            meta, govde = md_oku(os.path.join(icerik_dir, ad))
            yol, icerik = icerik_sayfasi(dict(meta, _govde=govde), yazilar)
            print("yazıldı:", yaz(yol, icerik))
            harita.append((yol, meta["guncelleme"]))
    yol, icerik = hizmet_dizini(dizin, hizmetler)
    print("yazıldı:", yaz(yol, icerik))
    harita.append((yol, max([dizin[0]["guncelleme"]] + [h["guncelleme"] for h in hizmetler])))
    for h in hizmetler:
        yol, icerik = hizmet_sayfasi(h, yazilar, hizmetler)
        print("yazıldı:", yaz(yol, icerik))
        harita.append((yol, h["guncelleme"]))
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
