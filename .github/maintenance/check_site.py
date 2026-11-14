#!/usr/bin/env python3
"""Dependency-free quality checks for the Movers4Less static website.

Run from the repository root:
    python3 scripts/check_site.py

These checks deliberately protect the current concept-stage behaviour. In
particular, the enquiry preview must remain disabled and the estimator must
not start sending browser selections to a server without an explicit review
of the privacy and backend design.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def error(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


class PageParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.lang = ""
        self.title_parts: list[str] = []
        self.in_title = False
        self.has_viewport = False
        self.has_description = False
        self.canonical_href = ""
        self.has_og_title = False
        self.has_og_description = False
        self.has_main = False
        self.has_skip_link = False
        self.has_concept_banner = False
        self.ids: list[str] = []
        self.links: list[tuple[str, str, set[str]]] = []
        self.assets: list[str] = []
        self.images_without_alt: list[str] = []
        self.forms: list[dict[str, bool]] = []
        self.form_stack: list[dict[str, bool]] = []
        self.inline_handlers: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_list)
        if tag == "html":
            self.lang = attrs.get("lang", "") or ""
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            name = (attrs.get("name", "") or "").lower()
            prop = (attrs.get("property", "") or "").lower()
            if name == "viewport":
                self.has_viewport = True
            elif name == "description" and (attrs.get("content", "") or "").strip():
                self.has_description = True
            if prop == "og:title" and (attrs.get("content", "") or "").strip():
                self.has_og_title = True
            elif prop == "og:description" and (attrs.get("content", "") or "").strip():
                self.has_og_description = True
        if tag == "main":
            self.has_main = True
        if "concept-banner" in (attrs.get("class", "") or "").split():
            self.has_concept_banner = True

        element_id = attrs.get("id")
        if element_id:
            self.ids.append(element_id)

        rel = set((attrs.get("rel", "") or "").lower().split())
        if tag == "a" and attrs.get("href"):
            classes = set((attrs.get("class", "") or "").split())
            self.links.append((
                attrs["href"],
                attrs.get("target", "").lower(),
                set((attrs.get("rel", "") or "").lower().split()),
            ))
            if attrs.get("href", "").strip() == "#main" and "skip-link" in classes:
                self.has_skip_link = True

        if tag == "link" and "canonical" in rel and attrs.get("href"):
            self.canonical_href = attrs["href"]
        if tag == "link" and rel.intersection(
            {"stylesheet", "icon", "manifest", "preload", "apple-touch-icon", "mask-icon"}
        ) and attrs.get("href"):
            self.assets.append(attrs["href"])
        if tag in {"script", "img", "source", "iframe", "audio"} and attrs.get("src"):
            self.assets.append(attrs["src"])
        if tag == "video":
            if attrs.get("src"):
                self.assets.append(attrs["src"])
            if attrs.get("poster"):
                self.assets.append(attrs["poster"])
        if attrs.get("srcset"):
            for candidate in attrs["srcset"].split(","):
                source = candidate.strip().split()
                if source:
                    self.assets.append(source[0])

        if tag == "img" and "alt" not in attrs:
            self.images_without_alt.append(str(attrs))

        for name in attrs:
            if name.lower().startswith("on"):
                self.inline_handlers.append(f"{tag}[{name}]")

        if tag == "form":
            self.form_stack.append({"disabled_fieldset": False, "has_submit": False})
        elif tag == "fieldset" and self.form_stack and "disabled" in attrs:
            self.form_stack[-1]["disabled_fieldset"] = True
        elif tag in {"button", "input"} and self.form_stack:
            input_type = (attrs.get("type", "") or "").lower()
            is_submit = tag == "button" and input_type in {"", "submit"} or (
                tag == "input" and input_type == "submit"
            )
            if is_submit:
                self.form_stack[-1]["has_submit"] = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "form" and self.form_stack:
            self.forms.append(self.form_stack.pop())

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def parse_page(path: Path) -> PageParser:
    parser = PageParser(path)
    try:
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
    except (OSError, UnicodeError) as exc:
        error(f"{path.relative_to(ROOT)}: could not read/parse HTML: {exc}")
    return parser


def resolve_local_path(source: Path, raw_url: str) -> tuple[Path | None, str]:
    """Return the local target path and fragment for a non-external URL."""
    parsed = urlsplit(raw_url)
    if parsed.scheme or parsed.netloc:
        return None, ""
    if parsed.path.startswith("/"):
        target = ROOT / unquote(parsed.path.lstrip("/"))
    elif parsed.path:
        target = source.parent / unquote(parsed.path)
    else:
        target = source
    target = target.resolve()
    fragment = unquote(parsed.fragment)
    return target, fragment


def check_pages() -> dict[Path, PageParser]:
    pages: dict[Path, PageParser] = {}
    html_files = sorted(ROOT.glob("*.html"))
    if not html_files:
        error("No root-level HTML pages found.")
        return pages

    for path in html_files:
        parser = parse_page(path)
        pages[path.resolve()] = parser
        relative = path.relative_to(ROOT)

        if parser.lang != "en-GB":
            error(f"{relative}: expected <html lang=\"en-GB\">, found {parser.lang!r}.")
        if not parser.title:
            error(f"{relative}: missing or empty <title>.")
        if not parser.has_viewport:
            error(f"{relative}: missing responsive viewport metadata.")
        if path.name != "404.html":
            if not parser.has_description:
                error(f"{relative}: missing or empty meta description.")
            if not parser.canonical_href:
                error(f"{relative}: missing canonical URL.")
            if not parser.has_og_title:
                error(f"{relative}: missing or empty Open Graph title.")
            if not parser.has_og_description:
                error(f"{relative}: missing or empty Open Graph description.")
        if not parser.has_main:
            error(f"{relative}: missing <main> landmark.")
        if not parser.has_skip_link:
            error(f"{relative}: missing skip-to-content link to #main.")
        if path.name != "404.html" and not parser.has_concept_banner:
            error(f"{relative}: missing site-wide concept-stage notice.")

        duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        for duplicate in duplicate_ids:
            error(f"{relative}: duplicate id={duplicate!r}.")

        for image in parser.images_without_alt:
            error(f"{relative}: image is missing an alt attribute: {image}.")

        for item in parser.inline_handlers:
            error(f"{relative}: inline JavaScript handler found ({item}); keep behaviour in script.js.")

        for href, target, rel in parser.links:
            if target == "_blank" and not {"noopener", "noreferrer"}.issubset(rel):
                error(f"{relative}: new-tab link must include rel=\"noopener noreferrer\": {href}")

            resolved, fragment = resolve_local_path(path, href)
            if resolved is None:
                continue
            if not resolved.exists():
                error(f"{relative}: local link target does not exist: {href}")
                continue
            if fragment and resolved.suffix.lower() in {".html", ".htm"}:
                target_parser = pages.get(resolved)
                if target_parser is None:
                    target_parser = parse_page(resolved)
                    pages[resolved] = target_parser
                if fragment not in target_parser.ids:
                    error(f"{relative}: fragment #{fragment} does not exist in {href}.")

        for asset in parser.assets:
            try:
                resolved, _ = resolve_local_path(path, asset)
            except ValueError:
                error(f"{relative}: malformed local resource URL: {asset}")
                continue
            if resolved is None:
                if urlsplit(asset).scheme.lower() not in {"data", "blob"}:
                    warn(f"{relative}: external page asset requires review: {asset}")
            elif not resolved.exists():
                error(f"{relative}: local page asset does not exist: {asset}")

        if path.name != "404.html":
            expected_host = (ROOT / "CNAME").read_text(encoding="utf-8").strip().lower()
            canonical = urlsplit(parser.canonical_href)
            expected_path = "/" if path.name == "index.html" else f"/{path.name}"
            if canonical.scheme != "https" or (canonical.hostname or "").lower() != expected_host:
                error(f"{relative}: canonical URL must use https and the configured CNAME host ({expected_host}).")
            elif canonical.path != expected_path or canonical.query or canonical.fragment:
                error(f"{relative}: canonical URL path should be {expected_path!r} without query or fragment.")

    return pages


def check_launch_safeguards(pages: dict[Path, PageParser]) -> None:
    quote = ROOT / "quote.html"
    if quote.exists():
        parser = pages.get(quote.resolve()) or parse_page(quote)
        if not parser.forms:
            error("quote.html: expected the enquiry preview form to remain visible but disabled.")
        elif not all(form["disabled_fieldset"] for form in parser.forms):
            error("quote.html: every enquiry form must remain inside a disabled fieldset.")
        else:
            print("PASS: enquiry preview remains disabled at fieldset level.")

    script = ROOT / "script.js"
    if script.exists():
        source = script.read_text(encoding="utf-8")
        network_apis = re.findall(r"\b(fetch|XMLHttpRequest|sendBeacon|WebSocket)\b", source)
        if network_apis:
            error(
                "script.js: network API detected "
                f"({', '.join(sorted(set(network_apis)))}). Review the data-flow and privacy design before enabling it."
            )
        else:
            print("PASS: current browser script contains no network-submission API.")

        tracker_pattern = re.compile(
            r"google-analytics|googletagmanager|gtag\s*\(|facebook\.net|hotjar|clarity\.ms|mixpanel",
            flags=re.IGNORECASE,
        )
        tracked_files = [script, *sorted(ROOT.glob("*.html"))]
        tracker_hits = [
            str(path.relative_to(ROOT))
            for path in tracked_files
            if tracker_pattern.search(path.read_text(encoding="utf-8"))
        ]
        if tracker_hits:
            error("Known analytics/advertising tracker pattern detected in: " + ", ".join(tracker_hits))
        else:
            print("PASS: no recognised analytics/advertising tracker patterns in page HTML or script.js.")


def check_css_resources() -> None:
    """Check local url(...) references in the shared stylesheet."""
    stylesheet = ROOT / "styles.css"
    if not stylesheet.exists():
        return
    source = stylesheet.read_text(encoding="utf-8")
    pattern = re.compile(r"""url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\s*\)""", re.IGNORECASE)
    for match in pattern.finditer(source):
        raw_url = next((value for value in match.groups() if value is not None), "").strip()
        if not raw_url or raw_url.startswith("#"):
            continue
        try:
            parsed = urlsplit(raw_url)
        except ValueError:
            error(f"styles.css: malformed url(...) value: {raw_url}")
            continue
        if parsed.scheme or parsed.netloc:
            if parsed.scheme.lower() not in {"data", "blob"}:
                warn(f"styles.css: external CSS asset requires review: {raw_url}")
            continue
        target = (stylesheet.parent / unquote(parsed.path)).resolve()
        if not target.exists():
            error(f"styles.css: local CSS asset does not exist: {raw_url}")
    print("PASS: local CSS url(...) references checked.")


def check_sitemap_and_robots() -> None:
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        try:
            tree = ET.parse(sitemap)
            namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [node.text or "" for node in tree.findall(".//sm:loc", namespace)]
            if not locs:
                error("sitemap.xml: no <loc> entries found.")
            if len(locs) != len(set(locs)):
                error("sitemap.xml: duplicate URL entries found.")
            expected_host = (ROOT / "CNAME").read_text(encoding="utf-8").strip().lower()
            for loc in locs:
                parsed = urlsplit(loc)
                if parsed.scheme != "https" or (parsed.hostname or "").lower() != expected_host:
                    error(f"sitemap.xml: URL must use https and configured host {expected_host}: {loc}")
                    continue
                if parsed.query or parsed.fragment:
                    error(f"sitemap.xml: URL must not include a query or fragment: {loc}")
                local = (ROOT / unquote(parsed.path.lstrip("/"))).resolve()
                if parsed.path in {"", "/"}:
                    local = (ROOT / "index.html").resolve()
                if not local.is_file():
                    error(f"sitemap.xml: URL does not map to a file in the site: {loc}")
            print(f"PASS: sitemap XML parsed; checked {len(locs)} URLs.")
        except (ET.ParseError, OSError) as exc:
            error(f"sitemap.xml: invalid or unreadable XML: {exc}")
    else:
        error("sitemap.xml is missing.")

    robots = ROOT / "robots.txt"
    if not robots.exists():
        error("robots.txt is missing.")
    elif "sitemap:" not in robots.read_text(encoding="utf-8").lower():
        error("robots.txt: sitemap declaration is missing.")
    else:
        print("PASS: robots.txt points crawlers to the sitemap.")


def main() -> int:
    pages = check_pages()
    check_launch_safeguards(pages)
    check_css_resources()
    check_sitemap_and_robots()

    print(f"\nChecked {len([p for p in ROOT.glob('*.html')])} HTML pages.")
    for message in WARNINGS:
        print(f"WARNING: {message}")
    for message in ERRORS:
        print(f"FAIL: {message}")

    if ERRORS:
        print(f"\nResult: FAILED ({len(ERRORS)} error(s), {len(WARNINGS)} warning(s)).")
        return 1

    print(f"\nResult: PASSED (0 errors, {len(WARNINGS)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
