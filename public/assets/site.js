/* techyonetim.com — ortak betik: eski çapa yönlendirmesi, uygunluk aracı, iletişim formu. */

/* Eski tek sayfa çapaları yeni sayfalara gider */
(function () {
  var yeni = { "#kvkk": "/kvkk/", "#gizlilik": "/gizlilik/", "#uygunluk": "/uygunluk-kontrolu/" };
  if (location.pathname === "/" && yeni[location.hash]) location.replace(yeni[location.hash]);
})();

/* UYGUNLUK KONTROLÜ — cevaplar tarayıcıdan çıkmaz */
(function () {
  var kutu = document.getElementById("uyg-sonuc");
  if (!kutu) return;
  var base = "font-family: inherit; font-size: 13.5px; font-weight: 500; padding: 9px 16px; border-radius: 999px; cursor: pointer; transition: all .2s cubic-bezier(.22,.61,.36,1); ";
  var SECILI = base + "border: 1px solid #e2d3c4; background: #f4ece4; color: #8a5a3c; font-weight: 700; box-shadow: 0 6px 14px -8px rgba(138,90,60,0.35);";
  var BOS = base + "border: 1px solid var(--hair); background: var(--surface); color: var(--text);";
  var S = {};

  function buildResult(S) {
      if (!S.toplam || !S.arge || !S.faaliyet) {
        return { show: false, verdict: '', title: '', body: [], flags: [], hasFlags: false };
      }
  
      const argeYeterli = (S.arge === 'c' || S.arge === 'd');
      const tasarimYeterli = (S.arge === 'b' || argeYeterli);
      let verdict, title, body = [];
  
      if (S.toplam === 'mikro' && S.arge === 'a') {
        verdict = 'Şu an uygun görünmüyor';
        title = 'Bu ölçekte önce başka bir yol daha mantıklı olabilir';
        body = [
          { t: 'On kişinin altındaki bir yapıda teknopark süreci kurulabilir, ancak sürecin sabit iş yükü ölçeğe bölünemediği için maliyeti çoğu zaman faydasını karşılamaz.' },
          { t: 'Bizim çalışma modelimiz tek seferlik başvurular değil, sürekli yürütülen programlar üzerine kurulu — bu aşamada size uygun olmayabilir. Ekibiniz büyüdüğünde ya da bir TÜBİTAK veya KOSGEB programına başvurmayı düşündüğünüzde konuşalım.' }
        ];
      } else if (S.faaliyet === 'tasarim' && tasarimYeterli) {
        verdict = 'Tasarım Merkezi eşiğini karşılıyorsunuz';
        title = 'Tasarım Merkezi ve Teknopark, ikisi de değerlendirilebilir';
        body = [{ t: 'Tasarım Merkezi için asgari 10 tasarım personeli şartını karşılıyorsunuz. Tasarım Merkezi kendi tesisinizde kurulur; Teknopark ise bölge içinde faaliyet gerektirir. Hangisinin daha uygun olduğu tesis yapınıza ve çalışma düzeninize bağlı.' }];
      } else if (argeYeterli && (S.faaliyet === 'yazilim' || S.faaliyet === 'urun')) {
        verdict = 'Ar-Ge Merkezi eşiğini karşılıyorsunuz';
        title = 'Ar-Ge Merkezi ve Teknopark, ikisi de değerlendirilebilir';
        body = [
          { t: 'Ar-Ge Merkezi için asgari 15 tam zaman eşdeğer Ar-Ge personeli şartını karşılıyorsunuz. Belirli sektörlerde bu eşik 30 olarak uygulanır — faaliyet konunuzun hangi grupta olduğunu görüşmede netleştiriyoruz.' },
          { t: 'Ar-Ge Merkezi kendi tesisinizde kurulur ve coğrafi kısıt getirmez; Teknopark bölge içinde faaliyet gerektirir ama kurulum eşiği daha düşüktür. İkisi birlikte de yürütülebilir.' }
        ];
      } else if (S.faaliyet === 'belirsiz') {
        verdict = 'Önce faaliyet tanımı';
        title = 'Model seçiminden önce faaliyetin tanımlanması gerekiyor';
        body = [
          { t: 'Hangi modele uygun olduğunuz, faaliyetinizin Ar-Ge, yazılım geliştirme veya tasarım olarak nasıl tanımlanacağına bağlı. Bu tanım hem başvurunun kabulünü hem sonraki denetimleri doğrudan etkiler.' },
          { t: 'Durum analizinde faaliyetinizi Oslo ve Frascati kılavuzları çerçevesinde değerlendirip hangi kapının açık olduğunu netleştiriyoruz.' }
        ];
      } else {
        verdict = 'Teknopark yolu uygun';
        title = 'Ar-Ge Merkezi eşiğinin altındasınız — Teknopark tarafına bakalım';
        body = [
          { t: 'Ar-Ge, yazılım veya tasarım personeli sayınız Ar-Ge Merkezi için gereken 15 kişilik eşiğin altında. Bu bir engel değil: Teknopark statüsünde böyle bir asgari personel şartı yok, teşvik seti ise büyük ölçüde benzer.' },
          { t: "Ekibiniz büyüdükçe Ar-Ge Merkezi'ne geçiş de gündeme gelebilir; yapıyı baştan buna uygun kurmak, sonradan taşımaktan kolaydır." }
        ];
      }
  
      const flags = [];
      if (S.istisna === 'orta') {
        flags.push({ head: 'Tasdik zorunluluğu kapsamında olabilirsiniz.', rest: 'Tek kalemde 500.000 TL, toplamda 1.000.000 TL eşiği aşıldığında tasdik raporu zorunlu; beyanname süresini takip eden iki ay içinde ibraz edilmezse hak kaybı doğuyor.' });
      }
      if (S.istisna === 'yuksek') {
        flags.push({ head: 'Tasdik zorunluluğu kapsamındasınız.', rest: 'Eşik aşıldığında rapor, beyanname süresini takip eden iki ay içinde ibraz edilmelidir.' });
        flags.push({ head: 'Girişim sermayesi fonu yükümlülüğünüz var.', rest: "Alt sınır 10803 sayılı Karar ile 5.000.000 TL'ye yükseldi. Yararlanılan tutarın %3'ü fon olarak ayrılıp süresinde yatırıma yönlendirilmezse, tutarın %20'si istisna dışına çıkıyor." });
      }
      if (S.toplam === 'buyuk' && !argeYeterli) {
        flags.push({ head: 'Ar-Ge kadronuz eşiğin altında görünüyor.', rest: 'Mevcut kadronun ne kadarının Ar-Ge personeli olarak tanımlanabileceği çoğu firmada beklenenden fazla çıkıyor — bu ayrım başvuru öncesinde yapılmalı.' });
      }
  
      return { show: true, verdict, title, body, flags, hasFlags: flags.length > 0 };
    }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function ciz() {
    document.querySelectorAll("button[data-q]").forEach(function (b) {
      var secili = S[b.getAttribute("data-q")] === b.getAttribute("data-v");
      b.setAttribute("style", secili ? SECILI : BOS);
      b.setAttribute("aria-pressed", secili ? "true" : "false");
    });
    var r = buildResult(S);
    if (!r.show) { kutu.innerHTML = ""; return; }
    var html = '<div style="padding: 24px 26px; background: var(--wash); border-top: 1px solid var(--hair);">' +
      '<span style="display: inline-block; font-size: 11.5px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; padding: 4px 10px; margin-bottom: 12px; border: 1.5px solid var(--accent); color: var(--accent);">' + esc(r.verdict) + "</span>" +
      '<h4 style="font-size: 19px; font-weight: 600; margin: 0 0 10px;">' + esc(r.title) + "</h4>" +
      '<div style="display: flex; flex-direction: column; gap: 10px;">' +
      r.body.map(function (b) { return '<p style="font-size: 14.5px; line-height: 1.6; margin: 0;">' + esc(b.t) + "</p>"; }).join("") + "</div>";
    if (r.hasFlags) {
      html += '<div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--accent); display: flex; flex-direction: column; gap: 8px;">' +
        r.flags.map(function (f) { return '<p style="font-size: 13.5px; line-height: 1.55; margin: 0;"><strong>' + esc(f.head) + "</strong> " + esc(f.rest) + "</p>"; }).join("") + "</div>";
    }
    kutu.innerHTML = html + '<p style="margin: 18px 0 0;"><a class="btn btn-p" href="/iletisim/">Durum analizi talep et →</a></p></div>';
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button[data-q]") : null;
    if (!b) return;
    S[b.getAttribute("data-q")] = b.getAttribute("data-v");
    ciz();
  });
  ciz();
})();


/* =================================================================
   İLETİŞİM FORMU — Tech Consultancy
   Web3Forms erişim anahtarınızı tırnakların arasına yapıştırın.
   Anahtar girilmezse form, e-posta uygulamasını açan yedeğe düşer;
   hiçbir talep sessizce kaybolmaz.
   ================================================================= */
window.__W3F_KEY = "e81f0fe0-5545-4715-a674-ab74153f4ccb";
(function () {
  var ALICI = "info@techyonetim.com", TEL = "+90 535 573 02 69";
  var busy = false;

  function box(btn) {
    var el = document.getElementById("__form_msg");
    if (!el || !el.isConnected) {
      el = document.createElement("p");
      el.id = "__form_msg";
      el.style.cssText = "margin:14px 0 0;font-size:13.5px;line-height:1.5;display:none";
    }
    if (el.parentNode !== btn.parentNode) btn.parentNode.insertBefore(el, btn.nextSibling);
    return el;
  }
  function say(btn, t, c) { var e = box(btn); e.textContent = t; e.style.color = c; e.style.display = "block"; }
  function val(id) { var e = document.getElementById(id); return e ? (e.value || "").trim() : ""; }

  /* Olay delegasyonu: tasarım motoru DOM'u yeniden çizse de bağlantı kopmaz */
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest ? ev.target.closest("button") : null;
    if (!btn || !/Talebi g[oö]nder/i.test(btn.textContent) || busy) return;
    ev.preventDefault();

    var kvkk = document.getElementById("f-kvkk");
    var d = {
      "Şirket": val("f-sirket"), "Ad soyad": val("f-ad"), "E-posta": val("f-mail"),
      "Telefon": val("f-tel"), "Personel sayısı": val("f-per"),
      "Hizmet konusu": val("f-konu"), "Mesaj": val("f-mesaj")
    };
    if (!d["Ad soyad"] || !d["E-posta"]) return say(btn, "Lütfen ad soyad ve e-posta alanlarını doldurun.", "#b4232a");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(d["E-posta"])) return say(btn, "E-posta adresi geçerli görünmüyor.", "#b4232a");
    if (kvkk && !kvkk.checked) return say(btn, "Devam etmek için KVKK onayını işaretleyin.", "#b4232a");

    var konu = "Durum analizi talebi — " + (d["Şirket"] || d["Ad soyad"]);
    var key = window.__W3F_KEY;

    if (!key || key.indexOf("BURAYA") === 0) {
      var govde = Object.keys(d).map(function (k) { return k + ": " + d[k]; }).join("\n");
      say(btn, "E-posta uygulamanız açılıyor — mesajı göndermeniz yeterli.", "#48566d");
      window.location.href = "mailto:" + ALICI + "?subject=" + encodeURIComponent(konu) +
                             "&body=" + encodeURIComponent(govde);
      return;
    }

    busy = true; say(btn, "Gönderiliyor…", "#48566d");
    var payload = { access_key: key, subject: konu, from_name: "Tech Consultancy web sitesi", replyto: d["E-posta"] };
    for (var k in d) payload[k] = d[k];

    fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json(); })
      .then(function (r) {
        busy = false;
        if (!r || !r.success) throw new Error("hata");
        say(btn, "Talebiniz alındı. İki iş günü içinde dönüş yapacağız.", "#1e7a4a");
        ["f-sirket","f-ad","f-mail","f-tel","f-mesaj"].forEach(function (id) {
          var e = document.getElementById(id); if (e) e.value = "";
        });
        if (kvkk) kvkk.checked = false;
      })
      .catch(function () {
        busy = false;
        say(btn, "Gönderilemedi. Lütfen " + ALICI + " adresine yazın veya " + TEL + " numarasını arayın.", "#b4232a");
      });
  }, true);
})();
