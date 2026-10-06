"""Check generated routes, metadata, local links, assets and approved identity."""
import argparse, json, re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
parser = argparse.ArgumentParser()
parser.add_argument('--origin', required=True, help='Full public site URL including any hosting path')
args = parser.parse_args()
ORIGIN = args.origin.rstrip('/')
BASE_PATH = urlsplit(ORIGIN).path.rstrip('/')

def local_path(path):
    if BASE_PATH:
        assert path == BASE_PATH or path.startswith(BASE_PATH + '/'), f'URL outside site path: {path}'
        return path[len(BASE_PATH):] or '/'
    return path

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags=[]; self.ids=[]; self.feed(source)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.tags.append((tag,a))
        if 'id' in a: self.ids.append(a['id'])
    def find(self, tag, **attrs):
        return [a for t,a in self.tags if t==tag and all(a.get(k)==v for k,v in attrs.items())]

pages={}
for file in DIST.rglob('*.html'):
    text=file.read_text(encoding='utf-8')
    parsed=Page(text)
    assert not re.search(r'faqeh|faqh|hairul', text, re.I), file
    assert len(parsed.ids)==len(set(parsed.ids)), f'Duplicate ID: {file}'
    assert len(parsed.find('h1'))==1, f'One H1 required: {file}'
    for a in parsed.find('img'):
        assert 'alt' in a, f'Missing image description or decorative alt: {file}'
        assert a.get('width') and a.get('height'), f'Image dimensions missing: {file}'
    if file.name!='404.html':
        assert parsed.find('meta', name='description')[0]['content'], file
        assert len(parsed.find('link',rel='canonical'))==1, file
        assert {a['hreflang'] for a in parsed.find('link', rel='alternate')}=={'ms-MY','en-MY','x-default'}, file
        assert parsed.find('html')[0]['lang'] in ['ms','en'], file
        expected_route = '/' + file.parent.relative_to(DIST).as_posix().strip('.')
        expected_route = expected_route.rstrip('/') + '/'
        if file.parent == DIST:
            expected_route = '/ms/'
        assert parsed.find('link', rel='canonical')[0]['href'] == ORIGIN + expected_route, file
        for a in parsed.find('link', rel='alternate'):
            assert a['href'].startswith(ORIGIN + '/'), f'Wrong alternate origin: {file}'
            route = local_path(urlsplit(a['href']).path)
            assert (DIST / route.lstrip('/') / 'index.html').exists(), f'Missing language route: {file}'
        assert parsed.find('meta', property='og:url')[0]['content'] == ORIGIN + expected_route, file
        assert parsed.find('meta', property='og:image')[0]['content'] == ORIGIN + '/assets/hero.webp', file
    pages[file]=parsed

for file,parsed in pages.items():
    for tag,a in parsed.tags:
        refs=[a.get('href')] if tag in ['a','link','use'] else [a.get('src')] if tag in ['img','script'] else []
        for ref in refs:
            if not ref: continue
            parts=urlsplit(ref)
            if parts.scheme or parts.netloc: continue
            route=unquote(parts.path)
            if route.startswith('/'): route=local_path(route)
            target=(DIST/route.lstrip('/')) if route.startswith('/') else (file.parent/route if route else file)
            if target.is_dir(): target=target/'index.html'
            assert target.exists(), f'Missing local target {ref} in {file}'
            if parts.fragment and target.suffix=='.html':
                assert parts.fragment in pages[target].ids, f'Missing anchor {ref} in {file}'
        for key in ['aria-controls','aria-labelledby','aria-describedby']:
            for identity in a.get(key,'').split():
                assert identity in parsed.ids, f'Invalid {key} {identity} in {file}'
sitemap=ET.fromstring((DIST/'sitemap.xml').read_text(encoding='utf-8'))
assert len(sitemap)==20
for entry in sitemap:
    location=entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
    assert location.startswith(ORIGIN + '/'),location
    path=local_path(urlsplit(location).path)
    assert (DIST/path.lstrip('/')/'index.html').exists(),path
    assert len(entry.findall('{http://www.w3.org/1999/xhtml}link'))==3,path
for sheet in (DIST/'assets').rglob('*.css'):
    for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)', sheet.read_text(encoding='utf-8')):
        if ref.startswith('data:'): continue
        parts=urlsplit(ref)
        if parts.scheme or parts.netloc: continue
        assert not parts.path.startswith('/'), f'Use portable relative CSS asset paths: {ref}'
        assert (sheet.parent / parts.path).exists(), f'Missing CSS asset: {ref}'
assert 'Sitemap: ' + ORIGIN + '/sitemap.xml' in (DIST/'robots.txt').read_text(encoding='utf-8')
assert (DIST/'.nojekyll').exists()
print(json.dumps({'result':'passed','html_pages':len(pages),'sitemap_routes':len(sitemap),'checks':['identity','H1','metadata','local links','image assets and descriptions','ARIA references','sitemap']}))
