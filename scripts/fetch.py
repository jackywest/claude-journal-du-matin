#!/usr/bin/env python3
"""fetch.py : lit sources.txt (RSS, Atom, YouTube, releases GitHub), garde les éléments récents,
dédoublonne, et écrit un JSON. Python 3 bibliothèque standard uniquement.

Usage : python3 scripts/fetch.py [sources.txt] [--hours 24] [--out items.json] [--no-og]
Format de sources.txt : une source par ligne, "URL" ou "Nom | URL", les lignes # sont ignorées.
"""
import argparse, concurrent.futures as cf, difflib, html, json, re, sys, time
import urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

UA = "journal-du-matin/1.0 (+https://github.com/jackywest/claude-journal-du-matin)"
TIMEOUT = 20
SIGNAUX = {
    "pub": r"\b(sponsor\w*|sponsoris\w*|partner content|advertis\w*|publicit\w*|promo code|code promo|affiliate)\b",
    "roundup": r"\b(roundup|round-up|digest|weekly|newsletter|this week|cette semaine|recap|récap\w*|top \d+)\b",
    "mini": r"\b(patch|hotfix|bump|typo|chore|dependabot|minor fixes?|bug ?fixes?)\b|^(v?\d+(\.\d+)+\S*|b\d+)(:|$)",
}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = r.read(3_000_000)
    return data if binary else data.decode("utf-8", "replace")


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def text_of(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def clean(s, n=600):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def kind_of(url):
    if "youtube.com/feeds" in url:
        return "youtube"
    if "github.com" in url and url.endswith(".atom"):
        return "github"
    return "flux"


def parse_feed(xml_text, source, url):
    root = ET.fromstring(xml_text.encode("utf-8"))
    out = []
    feed_title = None
    for el in root.iter():
        if local(el.tag) in ("title",) and feed_title is None:
            feed_title = text_of(el)
            break
    nom = source or feed_title or urllib.parse.urlparse(url).netloc
    for el in root.iter():
        t = local(el.tag)
        if t not in ("item", "entry"):
            continue
        d = {"titre": "", "lien": "", "date": None, "resume": "", "image": ""}
        for c in el:
            k = local(c.tag)
            if k == "title":
                d["titre"] = clean(text_of(c), 300)
            elif k == "link":
                href = c.get("href")
                if href and (c.get("rel") in (None, "alternate")):
                    d["lien"] = d["lien"] or href
                elif not href and text_of(c):
                    d["lien"] = text_of(c)
            elif k in ("pubDate", "published", "updated", "date") and not d["date"]:
                d["date"] = parse_date(text_of(c))
            elif k in ("description", "summary", "content", "encoded") and len(text_of(c)) > len(d["resume"]):
                d["resume"] = clean(text_of(c))
                m = re.search(r'<img[^>]+src=["\']([^"\']+)', text_of(c))
                if m and not d["image"]:
                    d["image"] = m.group(1)
            elif k == "thumbnail" and c.get("url"):
                d["image"] = c.get("url")
            elif k == "content" and c.get("url") and "image" in (c.get("type") or c.get("medium") or ""):
                d["image"] = d["image"] or c.get("url")
            elif k == "enclosure" and (c.get("type") or "").startswith("image"):
                d["image"] = d["image"] or c.get("url")
            elif k == "group":  # YouTube media:group
                for g in c:
                    if local(g.tag) == "thumbnail" and g.get("url"):
                        d["image"] = d["image"] or g.get("url")
                    if local(g.tag) == "description" and not d["resume"]:
                        d["resume"] = clean(text_of(g))
        d["image"] = html.unescape(d["image"])
        if "githubassets.com" in d["image"]:
            d["image"] = ""  # carte générique GitHub, pas une photo d'article
        m = re.search(r"Points: (\d+)\s*# Comments: (\d+)", d["resume"])
        if d["resume"].startswith("Article URL:"):  # gabarit Hacker News : pas de vrai résumé
            d["discussion"] = {"points": int(m.group(1)), "commentaires": int(m.group(2))} if m else {}
            d["resume"] = ""
        if d["titre"] and d["lien"]:
            d["source"] = nom
            d["type"] = kind_of(url)
            if d["type"] == "github":
                d["image"] = ""  # media:thumbnail GitHub = avatar de l'auteur, pas une photo d'article
            out.append(d)
    return out


def og_meta(link, prop):
    try:
        page = get(link)[:200_000]
    except Exception:
        return ""
    m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)' % prop, page, re.I) or \
        re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']' % prop, page, re.I)
    return html.unescape(m.group(1)) if m else ""


def og_image(link):
    img = og_meta(link, "og:image")
    return urllib.parse.urljoin(link, img) if img and "githubassets.com" not in img else ""


def norm_url(u):
    p = urllib.parse.urlsplit(u)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.startswith("utm_") and k not in ("ref", "fbclid")]
    if "youtube.com" in p.netloc:
        return "yt:" + dict(q).get("v", p.path)
    return (p.netloc.lower().replace("www.", "") + p.path.rstrip("/") + ("?" + urllib.parse.urlencode(q) if q else ""))


def tokens(t):
    return set(w for w in re.findall(r"[a-z0-9À-ÿ]{3,}", t.lower()))


def similaires(a, b):
    ta, tb = tokens(a), tokens(b)
    jac = len(ta & tb) / max(1, len(ta | tb))
    return jac >= 0.6 or difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.8


def dedoublonner(items):
    groupes = []
    vus = {}
    for it in sorted(items, key=lambda x: x["date"], reverse=True):
        cle = norm_url(it["lien"])
        g = vus.get(cle)
        if g is None:
            for cand in groupes:
                if cand["source"] != it["source"] and similaires(cand["titre"], it["titre"]):
                    g = cand
                    break
        if g is None:
            it["aussi"] = []
            groupes.append(it)
            vus[cle] = it
        else:
            g["aussi"].append({"source": it["source"], "lien": it["lien"], "titre": it["titre"]})
            if not g["image"] and it["image"]:
                g["image"] = it["image"]
            if len(it["resume"]) > len(g["resume"]):
                g["resume"] = it["resume"]
    return groupes


def lire_sources(path):
    res = []
    for ligne in open(path, encoding="utf-8"):
        ligne = ligne.split(" #")[0].strip()
        if not ligne or ligne.startswith("#"):
            continue
        if "|" in ligne:
            nom, url = [x.strip() for x in ligne.split("|", 1)]
        else:
            nom, url = "", ligne
        if url.startswith("http"):
            res.append((nom, url))
    return res


def lire_flux(nom_url):
    nom, url = nom_url
    try:
        return nom_url, parse_feed(get(url), nom, url), None
    except Exception as e:
        return nom_url, [], "%s: %s" % (type(e).__name__, e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="?", default="sources.txt")
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--out", default="items.json")
    ap.add_argument("--no-og", action="store_true", help="ne pas chercher og:image")
    a = ap.parse_args()
    t0 = time.time()
    srcs = lire_sources(a.sources)
    if not srcs:
        sys.exit("Aucune source dans %s" % a.sources)
    limite = datetime.now(timezone.utc) - timedelta(hours=a.hours)
    bruts, ok, erreurs = [], 0, []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for (nom, url), items, err in ex.map(lire_flux, srcs):
            if err:
                erreurs.append({"source": nom or url, "url": url, "erreur": err})
                continue
            ok += 1
            bruts.extend(items)
    recents = [i for i in bruts if i["date"] and i["date"] >= limite]
    uniques = dedoublonner(recents)
    if not a.no_og:
        besoin = [i for i in uniques if not i["image"] and i["type"] != "youtube"][:25]
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            for it, img in zip(besoin, ex.map(lambda i: og_image(i["lien"]), besoin)):
                it["image"] = img
        sans = [i for i in uniques if not i["resume"]][:25]
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            for it, desc in zip(sans, ex.map(lambda i: og_meta(i["lien"], "og:description"), sans)):
                it["resume"] = clean(desc)
    for it in uniques:
        txt = it["titre"] + " " + it["resume"][:300]
        it["signaux"] = [k for k, rx in SIGNAUX.items() if re.search(rx, txt, re.I)]
        it["date"] = it["date"].isoformat()
    stats = {
        "flux_demandes": len(srcs), "flux_lus": ok, "flux_en_erreur": len(erreurs),
        "elements_total": len(bruts), "elements_moins_de_%dh" % a.hours: len(recents),
        "elements_apres_dedoublonnage": len(uniques),
        "avec_image": sum(1 for i in uniques if i["image"]),
        "duree_s": round(time.time() - t0, 1),
    }
    json.dump({"genere": datetime.now(timezone.utc).isoformat(), "stats": stats, "erreurs": erreurs, "items": uniques},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False))
    for e in erreurs:
        print("  ERREUR", e["source"], e["erreur"], file=sys.stderr)


if __name__ == "__main__":
    main()
