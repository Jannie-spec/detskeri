/* Cookie-samtykke + Google Analytics. GA indlæses først, når den besøgende har sagt ja.
   Brug: <script src="/samtykke.js" data-ga="G-XXXX" defer></script>  ·  link med class="cookie-valg" åbner valget igen */
(function () {
  var me = document.currentScript, GA = me && me.getAttribute("data-ga"), KEY = "samtykke";
  if (!GA) return;
  var T = {
    da: ["Vi vil gerne tælle besøg med Google Analytics, så vi kan gøre siden bedre. Det sætter cookies.", "Ja tak", "Nej tak", "Cookie-valg"],
    en: ["We'd like to count visits with Google Analytics to improve the site. This sets cookies.", "Accept", "No thanks", "Cookie settings"],
    de: ["Wir möchten Besuche mit Google Analytics zählen, um die Seite zu verbessern. Dabei werden Cookies gesetzt.", "Akzeptieren", "Nein danke", "Cookie-Einstellungen"],
    sv: ["Vi vill räkna besök med Google Analytics för att förbättra sidan. Det sätter cookies.", "Ja tack", "Nej tack", "Cookieval"]
  };
  var t = T[(document.documentElement.lang || "da").slice(0, 2)] || T.da;
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag("consent", "default", { analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
  var loaded = false;
  function load() {
    gtag("consent", "update", { analytics_storage: "granted" });
    if (loaded) return; loaded = true;
    var s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA;
    document.head.appendChild(s);
    gtag("js", new Date()); gtag("config", GA, { anonymize_ip: true });
  }
  function bar() {
    if (document.getElementById("samtykke")) return;
    var css = document.createElement("style");
    css.textContent = "#samtykke{position:fixed;left:12px;right:12px;bottom:12px;z-index:50;max-width:560px;margin:0 auto;background:#302f2f;color:#fff;border-radius:16px;padding:14px 16px;display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;font:500 15px/1.4 Figtree,system-ui,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.18)}#samtykke p{margin:0;flex:1 1 260px}#samtykke button{font:inherit;font-weight:700;border:0;border-radius:999px;padding:8px 16px;cursor:pointer}#samtykke .ja{background:#e37b5b;color:#fff}#samtykke .nej{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.5)}";
    document.head.appendChild(css);
    var d = document.createElement("div"); d.id = "samtykke"; d.setAttribute("role", "dialog"); d.setAttribute("aria-label", t[3]);
    d.innerHTML = "<p></p><button type='button' class='nej'></button><button type='button' class='ja'></button>";
    d.querySelector("p").textContent = t[0]; d.querySelector(".ja").textContent = t[1]; d.querySelector(".nej").textContent = t[2];
    d.querySelector(".ja").onclick = function () { set("ja"); d.remove(); load(); };
    d.querySelector(".nej").onclick = function () { set("nej"); d.remove(); gtag("consent", "update", { analytics_storage: "denied" }); };
    document.body.appendChild(d);
  }
  var v = get();
  if (v === "ja") load();
  else if (v !== "nej") (document.body ? bar() : document.addEventListener("DOMContentLoaded", bar));
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest(".cookie-valg");
    if (a) { e.preventDefault(); bar(); }
  });
})();
