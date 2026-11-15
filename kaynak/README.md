# techyonetim.com — kaynak

Yayınlanan dosyalar `public/` klasöründedir (DigitalOcean App Platform `output_dir: public`).
`kaynak/` yayınlanmaz.

## Rehber yazısı eklemek veya düzeltmek

1. `kaynak/rehber/<adres>.md` dosyasını düzenleyin (ön bilgi + gövde).
   Gövde biçimleri: paragraf, `## ara başlık`, `- madde`, `> dayanak notu`.
2. Yeni yazıysa adresini `kaynak/rehber/gruplar.json` içinde bir gruba ekleyin.
3. `python3 kaynak/build.py` — `public/rehber/` ve `public/sitemap.xml` yeniden üretilir.
4. Değişikliği gönderin (`git push`) ve App Platform'da dağıtımı tetikleyin.

## Notlar

- Ana sayfa (`public/index.html`) hâlâ Claude Design paketidir; içindeki şablon değiştirilirken
  hem dış `<head>` hem `__bundler/template` içindeki kaçışlı şablon güncellenmelidir.
- Sitede meslek unvanı (SMMM, bağımsız denetçi) ve müşteri adı kullanılmaz.
