"""Build a bilingual static CPE website from reusable, semantic section templates."""
import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urlsplit
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
LANG = 'ms'
ORIGIN = ''
BASE_PATH = ''
PHONE = '60143362622'
EMAIL = 'emidflyzone@gmail.com'
ROUTES = {
    'home': {'ms': '', 'en': ''},
    'about': {'ms': 'kenali-cpe', 'en': 'about'},
    'suitability': {'ms': 'kesesuaian', 'en': 'suitability'},
    'measurement': {'ms': 'pengukuran', 'en': 'measurement'},
    'plans': {'ms': 'pelan', 'en': 'plans'},
    'guides': {'ms': 'panduan', 'en': 'guides'},
    'contact': {'ms': 'hubungi', 'en': 'contact'},
    'privacy': {'ms': 'privasi', 'en': 'privacy'},
    'savings-guide': {'ms': 'panduan/fahami-penjimatan', 'en': 'guides/understanding-savings'},
    'preparation-guide': {'ms': 'panduan/persediaan-semakan', 'en': 'guides/site-check-preparation'},
}
PAGE_NAMES = {
    'home': ('CPE Patch untuk Aircond & Chiller di Malaysia', 'CPE Patch for Air-Conditioning & Chillers in Malaysia'),
    'about': ('Kenali CPE Patch', 'About CPE Patch'),
    'suitability': ('Kesesuaian & Pemasangan CPE Patch', 'CPE Patch Suitability & Installation'),
    'measurement': ('Pengukuran & Maklumat Penjimatan', 'Measurement & Savings Information'),
    'plans': ('Pelan Sewa Milik & Pemilikan', 'Rent-to-Own Plans & Ownership'),
    'guides': ('Panduan untuk Pemilik Premis', 'Guides for Premises Owners'),
    'contact': ('Hubungi Pasukan CPE', 'Contact the CPE Team'),
    'privacy': ('Privasi & Pertanyaan Anda', 'Privacy & Your Enquiry'),
    'savings-guide': ('Fahami Penjimatan Compressor dan Jumlah Bil', 'Understanding Compressor Savings and Total Bills'),
    'preparation-guide': ('Persediaan untuk Semakan Premis', 'Preparing for a Premises Check'),
}
INTRO = {
    'home': ('Kenali CPE Patch untuk aircond dan chiller. Semak kesesuaian premis, fahami contoh penjimatan dan bincang pelan dengan Pasukan CPE.',
             'Explore CPE Patch for air-conditioning and chillers. Check premises suitability, understand the savings example and discuss plans with the CPE team.'),
    'about': ('Fahami aplikasi produk, proses penilaian dan perkara yang perlu diketahui sebelum membuat keputusan.',
              'Understand the product application, assessment process and what to review before making a decision.'),
    'suitability': ('Jenis unit, keadaan sistem dan waktu operasi membantu menentukan sama ada CPE Patch sesuai untuk premis anda.',
                    'Equipment type, system condition and operating hours help determine whether CPE Patch is suitable for your premises.'),
    'measurement': ('Bezakan pengukuran pada compressor dengan perubahan keseluruhan bil. Semak data bersama keadaan operasi.',
                    'Distinguish compressor measurements from changes in the total bill. Review the data alongside operating conditions.'),
    'plans': ('Fahami konfigurasi, bayaran dan syarat pemilikan melalui cadangan yang khusus untuk premis anda.',
              'Understand configuration, payments and ownership conditions through a proposal specific to your premises.'),
    'guides': ('Penerangan praktikal untuk membantu anda bersedia dan bertanya soalan yang tepat.',
               'Practical explanations to help you prepare and ask useful questions.'),
    'contact': ('Mulakan dengan maklumat asas premis. Semak mesej anda sebelum menghantarnya kepada Pasukan CPE.',
                'Start with basic premises information. Review your message before sending it to the CPE team.'),
    'privacy': ('Cara borang pertanyaan dan pautan hubungan di laman ini digunakan.',
                'How the enquiry form and contact links on this website work.'),
    'savings-guide': ('Dua angka ini menerangkan perkara yang berbeza. Berikut cara membaca contoh dalam brosur CPE.',
                      'These two figures describe different things. Here is how to read the example in the CPE brochure.'),
    'preparation-guide': ('Sediakan maklumat yang membantu Pasukan CPE memahami peralatan dan keadaan operasi premis anda.',
                          'Prepare information that helps the CPE team understand your equipment and operating conditions.'),
}
def e(value):
    return html.escape(str(value), quote=True)

def raw(ms, en):
    return ms if LANG == 'ms' else en

def t(ms, en):
    return e(raw(ms, en))

def url(page='home', lang=None):
    code = lang or LANG
    slug = ROUTES[page][code]
    return '/' + code + '/' + (slug + '/' if slug else '')

def absolute(path):
    return ORIGIN + path

def site_html(source):
    """Mount local URLs below the hosting path without changing physical routes."""
    return re.sub(r'((?:href|src|action)=")/(?!/)',
                  lambda match: match.group(1) + BASE_PATH + '/', source)

def asset(name):
    version = hashlib.sha256((DIST / 'assets' / name).read_bytes()).hexdigest()[:12]
    return '/assets/' + name + '?v=' + version

def contact_anchor():
    return '#contact'

def wa(message=None):
    message = message or raw('Salam Pasukan CPE. Saya ingin semak kesesuaian premis saya.', 'Hello CPE team. I would like to check the suitability of my premises.')
    return 'https://wa.me/' + PHONE + '?text=' + quote(message)

ICONS = {
    'arrow': '<path d="M4 12h16M14 6l6 6-6 6"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
    'ac': '<rect x="2" y="5" width="20" height="10" rx="2"/><path d="M5 11h14M7 18v3M12 18v3M17 18v3"/>',
    'bill': '<path d="M6 2h9l4 4v16H6zM14 2v5h5M9 11h7M9 15h7M9 19h4"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    'compressor': '<rect x="4" y="7" width="16" height="12" rx="4"/><path d="M8 7V3h8v4M2 11h2M20 11h2M7 19v3M17 19v3M8 11h8M8 15h6"/>',
    'search': '<circle cx="10" cy="10" r="7"/><path d="m16 16 6 6"/>',
    'gear': '<path d="m9 3 1-2h4l1 2 3 1 2-1 2 4-2 2v4l2 2-2 4-3-1-3 2h-4l-1-2-3-1-2 1-2-4 2-2V9L2 7l2-4 2 1z"/><circle cx="12" cy="11" r="3"/>',
    'chat': '<path d="M5 3h14a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H9l-6 3v-5a3 3 0 0 1-1-2V6a3 3 0 0 1 3-3z"/><path d="M7 11h.01M12 11h.01M17 11h.01"/>',
    'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'minus': '<path d="M5 12h14"/>',
    'whatsapp': '<path d="M21 11.5a9 9 0 0 1-13.6 7.7L2 21l1.8-5.3A9 9 0 1 1 21 11.5z"/><path d="m8 7 2 3-1 1c1 2 2 3 4 4l1-1 3 2c-1 2-3 2-5 1-3-1-6-4-6-7 0-2 1-3 2-3z"/>',
}
def sprite():
    return '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">' + ''.join('<symbol id="i-' + name + '" viewBox="0 0 24 24">' + path + '</symbol>' for name, path in ICONS.items()) + '</svg>'

def icon(name):
    return '<svg class="icon" aria-hidden="true" focusable="false"><use href="#i-' + name + '"></use></svg>'

def button(label, href='#contact', style='', external=False, symbol='arrow'):
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return f'<a class="btn arrow {style}" href="{e(href)}"{attrs}><span>{label}</span>{icon(symbol)}</a>'

def link(label, href, external=False):
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return f'<a class="text-link" href="{e(href)}"{attrs}>{label}{icon("arrow")}</a>'

def photo(name, alt, cls='', reveal=False):
    effect = 'image' if reveal is True else reveal
    return f'<figure class="photo {cls}"' + (f' data-reveal="{e(effect)}"' if effect else '') + f'><img src="/assets/{name}.webp" alt="{e(alt)}" width="1536" height="1024" loading="lazy" decoding="async"><figcaption>{t("Imej ilustrasi", "Illustrative image")}</figcaption></figure>'

def wordmark():
    return f'<a class="wordmark" href="{url()}" aria-label="CPE Patch Energy Solutions"><strong>CPE PATCH</strong><small>ENERGY SOLUTIONS</small></a>'

def header(page):
    labels = {
        'about': ('Kenali CPE', 'About CPE'), 'suitability': ('Kesesuaian', 'Suitability'),
        'measurement': ('Pengukuran', 'Measurement'), 'plans': ('Pelan', 'Plans'),
        'guides': ('Panduan', 'Guides'),
    }
    anchors = {'about': '#about', 'suitability': '#suitability', 'measurement': '#measurement', 'plans': '#plans'}
    nav = ''
    for key, label in labels.items():
        dest = anchors[key] if page == 'home' and key in anchors else url(key)
        current = ' aria-current="page"' if page == key else ''
        nav += f'<a href="{dest}"{current}>{t(*label)}</a>'
    language = '<div class="language" aria-label="' + t('Bahasa', 'Language') + '">' + f'<a href="{url(page, "ms")}" lang="ms" hreflang="ms-MY"' + (' aria-current="page"' if LANG == 'ms' else '') + '>BM</a><span>/</span>' + f'<a href="{url(page, "en")}" lang="en" hreflang="en-MY"' + (' aria-current="page"' if LANG == 'en' else '') + '>EN</a></div>'
    return f'''<a href="#main" class="skip-link">{t("Langkau ke kandungan", "Skip to content")}</a>
<header class="site-header {"inner-header" if page != "home" else ""}"><div class="header-row">{wordmark()}<nav class="desktop-nav" aria-label="{t("Navigasi utama", "Main navigation")}">{nav}</nav>{language}<a class="header-cta" href="#contact">{t("Semakan Premis", "Premises Check")}</a><button type="button" class="menu-toggle" aria-expanded="false" aria-controls="mobile-nav" aria-label="{t("Buka menu", "Open menu")}">{icon("menu")}</button></div>
<nav id="mobile-nav" class="mobile-nav" aria-label="{t("Navigasi mudah alih", "Mobile navigation")}" hidden>{nav}<a href="#contact">{t("Hubungi Pasukan CPE", "Contact the CPE Team")}</a></nav></header>'''

def hero():
    return f'''<section class="hero" aria-labelledby="hero-title"><div class="hero-media"><img src="/assets/hero.webp" width="1536" height="1024" alt="{t("Ilustrasi kedai serbaneka dengan unit aircond luaran pada waktu senja", "Illustration of a convenience store with an outdoor air-conditioning unit at dusk")}" fetchpriority="high"></div>
<div class="wrap hero-content"><h1 id="hero-title">{t("Kenali potensi penjimatan tenaga premis anda.", "Explore your premises’ potential energy savings.")}</h1><p>{t("Terokai CPE Patch untuk aircond dan chiller. Mulakan dengan semakan kesesuaian premis anda.", "Explore CPE Patch for air-conditioning and chillers. Start with a suitability check for your premises.")}</p><div class="actions">{button(t("Semak Kesesuaian Premis Saya", "Check My Premises’ Suitability"))}{link(t("Kenali CPE Patch", "Explore CPE Patch"), "#about")}</div><div class="hero-note"><span>{t("Untuk kedai dan premis komersial di Malaysia.", "For shops and commercial premises in Malaysia.")}</span><span>{t("Imej ilustrasi", "Illustrative image")}</span></div></div></section>'''

def situation():
    items = [
        ('clock', ('Operasi panjang', 'Long operating hours'), ('Aircond atau chiller digunakan untuk tempoh yang lama.', 'Air-conditioning or chillers run for extended periods.')),
        ('ac', ('Beberapa unit', 'Multiple units'), ('Premis menggunakan lebih daripada satu unit peralatan.', 'Your premises use more than one equipment unit.')),
        ('bill', ('Bil mahu disemak', 'Bills to review'), ('Anda ingin memahami peluang penjimatan berdasarkan penggunaan sebenar.', 'You want to understand potential savings based on actual usage.')),
    ]
    grid = ''.join(f'<div class="context-item" data-reveal style="--delay:{i*80}ms">{icon(sym)}<h3>{t(*heading)}</h3><p>{t(*body)}</p></div>' for i, (sym, heading, body) in enumerate(items))
    return f'''<section class="section" id="situation" aria-labelledby="situation-title"><div class="wrap"><div class="section-heading"><h2 id="situation-title">{t("Kenali corak penggunaan premis anda.", "Understand how your premises use energy.")}</h2><p>{t("Waktu operasi dan penggunaan peralatan membantu kami menilai kesesuaian CPE Patch.", "Operating hours and equipment usage help us assess CPE Patch suitability.")}</p></div><div class="context-grid">{grid}</div>{photo("interior", raw("Ilustrasi ruang kedai dengan aircond dan kabinet penyejuk", "Illustration of a shop interior with air-conditioning and refrigerated cabinets"), "wide-photo")}<div class="context-footer"><span class="small muted">{t("Mulakan dengan maklumat penggunaan yang sedia ada.", "Start with the usage information you already have.")}</span>{link(t("Lihat faktor kesesuaian", "Explore suitability factors"), "#suitability")}</div></div></section>'''

def product():
    return f'''<section class="section dark" id="about" aria-labelledby="about-title"><div class="wrap split">{photo("equipment", raw("Ilustrasi unit aircond dan compressor, bukan foto produk CPE sebenar", "Illustration of an air-conditioning unit and compressor, not an actual CPE product photograph"), "product-photo", True)}<div class="product-copy" data-reveal><h2 id="about-title">{t("Fahami produk sebelum membuat keputusan.", "Understand the product before deciding.")}</h2><p>{t("CPE Patch ditawarkan untuk aplikasi pada compressor aircond dan chiller yang sesuai. Pasukan CPE akan menerangkan kesesuaian, pemasangan dan kaedah pengukuran.", "CPE Patch is offered for application on suitable air-conditioning and chiller compressors. The CPE team will explain suitability, installation and measurement.")}</p>
<div class="product-tabs" role="tablist" aria-label="{t("Maklumat produk", "Product information")}"><button type="button" id="tab-application" role="tab" aria-selected="true" aria-controls="panel-application" tabindex="0">{t("Aplikasi", "Application")}</button><button type="button" id="tab-assessment" role="tab" aria-selected="false" aria-controls="panel-assessment" tabindex="-1">{t("Semakan awal", "Initial check")}</button></div>
<div class="tab-panel" role="tabpanel" id="panel-application" aria-labelledby="tab-application" tabindex="0"><p>{t("Aircond dan chiller, tertakluk kepada penilaian teknikal. Semakan dibuat sebelum konfigurasi pemasangan dicadangkan.", "Air-conditioning and chillers, subject to technical assessment. A check takes place before an installation configuration is proposed.")}</p></div>
<div class="tab-panel" role="tabpanel" id="panel-assessment" aria-labelledby="tab-assessment" tabindex="0" hidden><p>{t("Jenis unit, kapasiti, keadaan sistem dan waktu operasi membantu Pasukan CPE memahami keperluan premis anda.", "Equipment type, capacity, system condition and operating hours help the CPE team understand your premises’ needs.")}</p></div>
<div class="actions">{button(t("Bincang Tentang Peralatan Saya", "Discuss My Equipment"), style="outline")}{link(t("Maklumat produk", "Product details"), url("about"))}</div></div></div></section>'''

def suitability():
    categories = [
        ('interior', 'store', ('Kedai serbaneka', 'Convenience store'), ('Untuk kedai, sediakan bilangan unit serta waktu operasi harian.', 'For a shop, prepare the unit count and daily operating hours.')),
        ('restaurant', 'restaurant', ('Restoran', 'Restaurant'), ('Untuk restoran, maklumkan peralatan penyejukan dan waktu perniagaan.', 'For a restaurant, describe the cooling equipment and business hours.')),
        ('office', 'office', ('Pejabat', 'Office'), ('Untuk pejabat, maklumkan jenis aircond dan jadual penggunaannya.', 'For an office, describe the air-conditioning type and operating schedule.')),
    ]
    choices = ''.join(f'<button type="button" class="premise-option" aria-pressed="{"true" if i == 0 else "false"}" data-value="{value}" data-note="{t(*note)}"><img src="/assets/{asset}.webp" width="1536" height="1024" alt="" loading="lazy" decoding="async"><span>{t(*label)}</span></button>' for i, (asset, value, label, note) in enumerate(categories))
    factors = [('Jenis dan kapasiti unit', 'Equipment type and capacity'), ('Bilangan aircond dan chiller', 'Number of air-conditioning and chiller units'), ('Waktu penggunaan', 'Operating hours'), ('Keadaan sistem sedia ada', 'Existing system condition')]
    checks = ''.join(f'<li data-reveal style="--delay:{i*70}ms">{icon("check")}<span>{t(*factor)}</span></li>' for i, factor in enumerate(factors))
    return f'''<section class="section" id="suitability" aria-labelledby="suitability-title"><div class="wrap"><div class="section-heading center suitability-heading"><h2 id="suitability-title">{t("Adakah CPE sesuai untuk premis anda?", "Could CPE suit your premises?")}</h2><p>{t("Kesesuaian dinilai berdasarkan peralatan dan corak operasi.", "Suitability is assessed against equipment and operating patterns.")}</p></div><div class="suitability-layout"><div><div class="premises-picker" data-reveal="fade">{choices}</div><p class="small muted" style="margin-top:12px">{t("Imej ilustrasi • Pilih kategori untuk panduan awal.", "Illustrative images • Select a category for initial guidance.")}</p></div><div class="assessment"><h3>{t("Perkara yang kami semak", "What we review")}</h3><ul class="check-list">{checks}</ul><p class="premise-result" aria-live="polite">{t(*categories[0][3])}</p></div></div><div class="suitability-bottom center"><p>{t("Setiap premis mempunyai keperluan berbeza. Mulakan dengan semakan awal.", "Every premises has different needs. Start with an initial check.")}</p>{button(t("Semak Premis Saya", "Check My Premises"))}</div></div></section>'''

def measurement():
    steps = [
        (('Data asas penggunaan', 'Baseline usage data'), ('Kenal pasti peralatan, waktu operasi dan data penggunaan sebelum perbandingan dibuat.', 'Identify the equipment, operating hours and usage data before making a comparison.')),
        (('Tempoh dan keadaan pengukuran', 'Measurement period and conditions'), ('Semak tempoh pengukuran serta perubahan pada beban, waktu operasi dan keadaan premis.', 'Review the measurement period and changes in load, operating hours and premises conditions.')),
        (('Perbandingan serta penjelasan hasil', 'Comparison and explanation'), ('Bezakan perubahan pada peralatan yang diukur daripada perubahan pada seluruh bil premis.', 'Distinguish changes in measured equipment from changes in the whole premises bill.')),
    ]
    buttons = ''.join(f'<button type="button" class="measurement-step" aria-expanded="{"true" if i == 0 else "false"}" aria-controls="measure-detail-{i}" data-reveal style="--delay:{i*70}ms"><span class="step-number">{i+1:02d}</span><span><strong>{t(*heading)}</strong><span class="step-description" id="measure-detail-{i}"{"" if i == 0 else " hidden"}>{t(*body)}</span></span></button>' for i, (heading, body) in enumerate(steps))
    return f'''<section class="section pale" id="measurement" aria-labelledby="measurement-title"><div class="wrap"><div class="section-heading"><h2 id="measurement-title">{t("Lihat bagaimana penjimatan dinilai.", "See how savings are assessed.")}</h2><p>{t("Fahami apa yang diukur, tempoh semakan dan keadaan operasi.", "Understand what is measured, the review period and operating conditions.")}</p></div><div class="scope-comparison"><div class="scope-panel">{icon("compressor")}<div><h3>{t("Penggunaan compressor", "Compressor consumption")}</h3><p>{t("Pengukuran pada peralatan yang dinilai.", "Measurement of the equipment being assessed.")}</p></div></div><div class="scope-panel">{icon("bill")}<div><h3>{t("Jumlah bil premis", "Total premises bill")}</h3><p>{t("Turut dipengaruhi oleh peralatan lain dan corak operasi.", "Also affected by other equipment and operating patterns.")}</p></div></div></div><div class="measure-bottom">{photo("service", raw("Ilustrasi semakan peralatan di premis komersial", "Illustration of an equipment check at commercial premises"), "measure-photo", "fade")}<div><div class="measurement-list">{buttons}</div><p class="measurement-note">{t("Keputusan khusus perlu dirujuk bersama laporan pengukuran.", "Specific results should be reviewed alongside the measurement report.")}</p>{link(t("Maklumat pengukuran", "Measurement information"), url("measurement"))}</div></div></div></section>'''

def example():
    return f'''<section class="section example" id="example" aria-labelledby="example-title"><div class="wrap"><div class="section-heading example-head"><h2 id="example-title">{t("Fahami angka untuk satu konfigurasi kedai.", "Understand the figures for one store configuration.")}</h2><p>{t("Contoh kiraan dalam brosur • Operasi 24 jam • 4 × 3HP aircond + 1 × 3HP chiller", "Brochure calculation example • 24-hour operation • 4 × 3HP air-conditioning units + 1 × 3HP chiller")}</p></div><div class="example-layout">{photo("interior", raw("Ilustrasi kedai, bukan foto premis bagi contoh kiraan", "Illustrative shop, not a photograph of the premises used for the calculation"), "example-photo")}<div class="bill-bars"><div><div class="bar-label"><span>{t("Bil sebelum", "Bill before")}</span><span>RM4,500.00</span></div><div class="bar-track" aria-hidden="true"><div class="bar-fill"></div></div></div><div><div class="bar-label"><span>{t("Bil selepas", "Bill after")}</span><span>RM4,236.75</span></div><div class="bar-track" aria-hidden="true"><div class="bar-fill after"></div></div></div><p class="bar-note">{t("Pengurangan bil dalam contoh:", "Bill reduction in this example:")} <strong>5.85%</strong></p></div></div><div class="equation" aria-label="{t("Penjimatan RM263.25 ditolak bayaran pelan RM235.00 bersamaan baki bulanan RM28.25", "Savings of RM263.25 minus a plan payment of RM235.00 leave a monthly balance of RM28.25")}"><div><small>{t("Penjimatan bulanan", "Monthly savings")}</small><strong>RM263.25</strong></div><span class="equation-symbol" aria-hidden="true">−</span><div><small>{t("Bayaran pelan dalam contoh", "Plan payment in the example")}</small><strong>RM235.00</strong></div><span class="equation-symbol" aria-hidden="true">=</span><div><small>{t("Baki bulanan", "Monthly balance")}</small><strong>RM28.25</strong></div></div><div class="example-bottom"><p>{t("Kiraan ini tidak termasuk bayaran awal. Angka dalam brosur ialah contoh, bukan jaminan hasil untuk setiap premis. Harga dan hasil sebenar perlu dinilai melalui cadangan khusus.", "This calculation excludes the initial payment. Brochure figures are an example, not a guarantee for every premises. Actual pricing and results require a specific proposal.")}</p>{link(t("Semak Angka Premis Saya", "Review My Premises’ Figures"), "#contact")}</div></div></section>'''

def plans():
    rows = [
        (('Kecil', 'Small'), '2 × 2HP', '1'),
        (('Sederhana', 'Medium'), '4 × 3HP', '1'),
        (('Besar', 'Large'), '6 × 3HP', '2'),
        (('Lebih besar', 'Larger'), '8 × 3HP', '3'),
    ]
    table = ''.join(f'<tr tabindex="0"><td>{t(*name)}</td><td>{ac} {t("aircond", "air-conditioning units")} + {chillers} {t("chiller", "chiller" if chillers == "1" else "chillers")}</td></tr>' for name, ac, chillers in rows)
    factors = [('bill', ('Bayaran awal', 'Initial payment'), ('Fahami jumlah dan syarat.', 'Understand the amount and conditions.')), ('bill', ('Bayaran bulanan', 'Monthly payment'), ('Bandingkan dengan anggaran penjimatan.', 'Compare it with estimated savings.')), ('check', ('Pemilikan', 'Ownership'), ('Semak tempoh dan terma perjanjian.', 'Review the duration and agreement terms.'))]
    items = ''.join(f'<div data-reveal style="--delay:{i*70}ms">{icon(sym)}<div><h3>{t(*heading)}</h3><p>{t(*body)}</p></div></div>' for i, (sym, heading, body) in enumerate(factors))
    return f'''<section class="section dark" id="plans" aria-labelledby="plans-title"><div class="wrap"><div class="section-heading"><h2 id="plans-title">{t("Fahami pelan yang sesuai untuk premis anda.", "Understand the plan for your premises.")}</h2><p>{t("Cadangan disediakan mengikut konfigurasi dan penilaian premis.", "Proposals are prepared around the configuration and assessment of your premises.")}</p></div><table class="plans-table" data-reveal="fade"><caption class="small" style="caption-side:bottom;text-align:left;padding-top:14px;color:#d4e3e7">{t("Konfigurasi ini ialah contoh daripada brosur, bukan pengesahan kelayakan.", "These are brochure configuration examples, not confirmation of eligibility.")}</caption><thead><tr><th scope="col">{t("Kategori", "Category")}</th><th scope="col">{t("Contoh konfigurasi dalam brosur", "Brochure configuration example")}</th></tr></thead><tbody>{table}</tbody></table><div class="plan-considerations">{items}</div><div class="plan-foot center">{button(t("Minta Penerangan Pelan", "Discuss a Plan"), style="amber")}<p>{t("Jumlah bayaran dan tempoh pemilikan perlu disahkan dalam cadangan rasmi.", "Payment amounts and ownership duration must be confirmed in the formal proposal.")}</p></div></div></section>'''

def process():
    steps = [
        ('bill', ('Kongsi maklumat', 'Share information'), ('Jenis premis, lokasi dan peralatan.', 'Premises type, location and equipment.'), ('Sediakan maklumat asas tentang premis dan peralatan. Ini membantu perbincangan awal.', 'Prepare basic premises and equipment information to support the initial discussion.')),
        ('search', ('Semakan awal', 'Initial review'), ('Bil dan keadaan premis disemak.', 'Bills and premises conditions are reviewed.'), ('Bincang skop semakan, liputan lokasi dan maklumat yang diperlukan sebelum lawatan.', 'Discuss the review scope, location coverage and required information before a visit.')),
        ('bill', ('Fahami cadangan', 'Understand the proposal'), ('Kesesuaian, kos dan kaedah pengukuran.', 'Suitability, costs and measurement.'), ('Semak konfigurasi yang dicadangkan, semua bayaran dan kaedah menilai hasil.', 'Review the proposed configuration, all payments and the method for assessing results.')),
        ('gear', ('Tentukan langkah', 'Choose the next step'), ('Bincang percubaan atau pemasangan.', 'Discuss a trial or installation.'), ('Pilihan percubaan dan pemasangan tertakluk kepada kelayakan, skop serta syarat yang dipersetujui.', 'Trial and installation options depend on eligibility, scope and agreed conditions.')),
    ]
    buttons = ''.join(f'<button type="button" class="process-step" aria-pressed="{"true" if i == 0 else "false"}" aria-controls="process-detail" data-detail="{t(*detail)}"><span class="process-marker">{i+1:02d}</span><h3>{t(*heading)}</h3><p>{t(*body)}</p></button>' for i, (sym, heading, body, detail) in enumerate(steps))
    return f'''<section class="section" id="process" aria-labelledby="process-title"><div class="wrap"><div class="section-heading"><h2 id="process-title">{t("Mulakan dengan semakan. Fahami sebelum membuat keputusan.", "Start with a check. Understand before deciding.")}</h2><p>{t("Pasukan CPE menerangkan kesesuaian, cadangan dan pilihan yang tersedia.", "The CPE team explains suitability, proposals and available options.")}</p></div>{photo("process", raw("Ilustrasi juruteknik menilai unit aircond di luar kedai", "Illustration of a technician assessing an outdoor air-conditioning unit"), "process-photo", "fade")}<div class="process"><div class="process-progress" aria-hidden="true"></div>{buttons}</div><p class="process-explanation" id="process-detail">{t(*steps[0][3])}</p><div class="process-bottom"><p>{t("Pilihan percubaan: kelayakan dan syarat diterangkan terlebih dahulu. Bincang juga skop semakan percuma yang dinyatakan dalam brosur.", "Trial eligibility and conditions are explained in advance. Also discuss the scope of the free check described in the brochure.")}</p>{button(t("Atur Semakan Awal", "Arrange an Initial Check"))}</div></div></section>'''

def team():
    return f'''<section id="team" aria-labelledby="team-title"><div class="team-section"><div class="team-media"><img src="/assets/service.webp" width="1536" height="1024" loading="lazy" decoding="async" alt="{t("Ilustrasi semakan peralatan, bukan foto ahli pasukan sebenar", "Illustration of an equipment check, not a photograph of an actual team member")}"></div><div class="wrap team-content"><div class="team-copy"><h2 id="team-title">{t("Bincang dengan pasukan yang mengendalikan CPE.", "Speak with the team handling CPE.")}</h2><p>{t("Dapatkan penjelasan tentang kesesuaian peralatan, cadangan pemasangan dan kaedah pengukuran.", "Get explanations about equipment suitability, proposed installation and measurement methods.")}</p>{button(t("Hubungi Pasukan CPE", "Contact the CPE Team"), style="outline")}</div></div><span class="team-caption">{t("Imej ilustrasi", "Illustrative image")}</span></div><div class="wrap references-strip"><h3>{t("Mahukan rujukan pemasangan?", "Looking for installation references?")}</h3><p>{t("Minta maklumat contoh premis dan bahan sokongan yang tersedia.", "Ask about premises examples and available supporting material.")}</p>{button(t("Tanya Tentang Rujukan", "Ask About References"), wa(raw("Salam Pasukan CPE. Saya ingin mendapatkan maklumat rujukan pemasangan dan bahan pengukuran yang tersedia.", "Hello CPE team. I would like information about installation references and available measurement material.")), external=True)}</div></section>'''

FAQ = [
    (('Adakah semua aircond dan chiller sesuai?', 'Are all air-conditioning units and chillers suitable?'), ('Kesesuaian bergantung pada jenis unit, keadaan sistem dan corak operasi. Pasukan CPE akan menilai maklumat premis anda terlebih dahulu.', 'Suitability depends on equipment type, system condition and operating patterns. The CPE team will first assess your premises information.')),
    (('Bagaimana penjimatan diukur?', 'How are savings measured?'), ('Bincang peralatan yang akan diukur, data asas, tempoh pengukuran dan keadaan operasi. Hasil pengukuran compressor perlu dibezakan daripada perubahan seluruh bil elektrik.', 'Discuss the equipment being measured, baseline data, measurement period and operating conditions. Compressor measurement results must be distinguished from changes in the whole electricity bill.')),
    (('Apakah proses pemasangan?', 'What is the installation process?'), ('Selepas penilaian, Pasukan CPE menerangkan konfigurasi dan langkah pemasangan yang sesuai. Masa dan keperluan operasi perlu disahkan untuk peralatan serta premis anda.', 'After assessment, the CPE team explains the suitable configuration and installation steps. Timing and operating requirements need to be confirmed for your equipment and premises.')),
    (('Bagaimana kesan terhadap warranty disemak?', 'How is the warranty impact reviewed?'), ('Minta penjelasan bertulis tentang kaedah pemasangan dan kesesuaiannya dengan syarat warranty pengeluar peralatan anda sebelum bersetuju.', 'Request a written explanation of the installation method and its compatibility with your equipment manufacturer’s warranty conditions before agreeing.')),
    (('Apakah syarat percubaan dan pelan sewa milik?', 'What are the trial and rent-to-own conditions?'), ('Semak kelayakan, tempoh, bayaran awal, bayaran bulanan, pengukuran serta syarat pemilikan dan penamatan melalui cadangan rasmi. Angka contoh dalam brosur bukan sebut harga khusus untuk premis anda.', 'Review eligibility, duration, initial and monthly payments, measurement, ownership and termination conditions in the formal proposal. Brochure examples are not a quotation for your premises.')),
]
def faq():
    items = ''
    for i, (question, answer) in enumerate(FAQ):
        items += f'<div class="faq-item {"open" if i == 0 else ""}"><h3><button type="button" class="faq-question" id="faq-question-{i}" aria-expanded="{"true" if i == 0 else "false"}" aria-controls="faq-answer-{i}"><span>{t(*question)}</span>{icon("minus" if i == 0 else "plus")}</button></h3><div class="faq-answer" id="faq-answer-{i}" role="region" aria-labelledby="faq-question-{i}"{"" if i == 0 else " hidden"}><p>{t(*answer)}</p></div></div>'
    return f'''<section class="section" id="faq" aria-labelledby="faq-title"><div class="wrap"><div class="faq-layout"><div class="faq-intro">{icon("chat")}<h2 id="faq-title">{t("Soalan sebelum anda bermula.", "Questions before you start.")}</h2><p>{t("Dapatkan penjelasan yang jelas tentang peralatan, pemasangan dan pelan.", "Get clear explanations about equipment, installation and plans.")}</p>{button(t("Tanya Pasukan CPE", "Ask the CPE Team"), style="outline")}</div><div class="accordion" data-reveal="fade">{items}</div></div><p class="faq-note">{t("Setiap cadangan perlu difahami bersama skop dan syaratnya.", "Every proposal should be understood alongside its scope and conditions.")}</p></div></section>'''

def contact():
    fields = [
        ('name', ('Nama', 'Name'), 'text', 'name'),
        ('phone', ('Nombor telefon', 'Telephone number'), 'tel', 'tel'),
        ('location', ('Lokasi premis', 'Premises location'), 'text', 'address-level2'),
    ]
    inputs = ''.join(f'<div class="field"><label for="enquiry-{name}">{t(*label)}</label><input id="enquiry-{name}" name="{name}" type="{typ}" autocomplete="{autocomplete}" required maxlength="{"25" if name == "phone" else "100"}" aria-describedby="enquiry-{name}-error"><span class="field-error" id="enquiry-{name}-error"></span></div>' for name, label, typ, autocomplete in fields)
    types = [('store', ('Kedai serbaneka / runcit', 'Convenience / retail store')), ('restaurant', ('Restoran / kafe', 'Restaurant / café')), ('office', ('Pejabat', 'Office')), ('hotel', ('Hotel / hospitaliti', 'Hotel / hospitality')), ('hall', ('Dewan / ruang acara', 'Hall / event venue')), ('factory', ('Kilang / industri', 'Factory / industrial')), ('other', ('Lain-lain', 'Other'))]
    options = ''.join(f'<option value="{value}">{t(*label)}</option>' for value, label in types)
    return f'''<section class="section dark contact-section" id="contact" aria-labelledby="contact-title"><div class="wrap contact-layout"><div class="contact-copy"><h2 id="contact-title">{t("Semak kesesuaian premis anda.", "Check your premises’ suitability.")}</h2><p>{t("Kongsi maklumat asas. Pasukan CPE akan membantu menerangkan langkah seterusnya.", "Share basic information. The CPE team will help explain the next steps.")}</p><div class="actions">{button(t("WhatsApp Pasukan CPE", "WhatsApp the CPE Team"), wa(), external=True, symbol="whatsapp")}</div><p class="small">{t("Sediakan jenis premis, lokasi dan maklumat peralatan.", "Prepare your premises type, location and equipment information.")}</p><p class="small"><a href="tel:+{PHONE}">+60 14-336 2622</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<form class="contact-form" data-reveal data-phone="{PHONE}" novalidate action="{e(wa())}" method="get"><h3>{t("Pertanyaan awal", "Initial enquiry")}</h3><p>{t("Borang ini menyediakan mesej WhatsApp. Anda boleh menyemak mesej sebelum menghantarnya.", "This form prepares a WhatsApp message. You can review it before sending.")}</p><div class="form-grid">{inputs}<div class="field"><label for="enquiry-premises">{t("Jenis premis", "Premises type")}</label><select id="enquiry-premises" name="premises" required aria-describedby="enquiry-premises-error"><option value="">{t("Pilih jenis premis", "Choose premises type")}</option>{options}</select><span class="field-error" id="enquiry-premises-error"></span></div><div class="field full"><label for="enquiry-equipment">{t("Peralatan / nota (pilihan)", "Equipment / notes (optional)")}</label><textarea id="enquiry-equipment" name="equipment" rows="2" maxlength="700"></textarea></div></div><button class="btn" type="submit" disabled><span>{t("Sediakan Mesej WhatsApp", "Prepare WhatsApp Message")}</span>{icon("arrow")}</button><p class="form-note">{t("Maklumat borang tidak disimpan oleh laman ini. Ia dimasukkan ke dalam mesej WhatsApp apabila anda memilih untuk meneruskan.", "Form information is not stored by this website. It is included in a WhatsApp message when you choose to continue.")} <a href="{url("privacy")}">{t("Privasi", "Privacy")}</a></p><p class="form-status" role="status" aria-live="polite"></p><noscript><p class="small">{t("Untuk pertanyaan tanpa JavaScript, gunakan butang WhatsApp atau nombor telefon di sebelah.", "For an enquiry without JavaScript, use the WhatsApp button or telephone number alongside.")}</p></noscript></form></div></section>'''

def footer():
    labels = [('about', ('Kenali CPE', 'About CPE')), ('suitability', ('Kesesuaian', 'Suitability')), ('measurement', ('Pengukuran', 'Measurement')), ('plans', ('Pelan', 'Plans')), ('guides', ('Panduan', 'Guides'))]
    links = ''.join(f'<a href="{url(page)}">{t(*label)}</a>' for page, label in labels)
    return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top">{wordmark()}<nav class="footer-links" aria-label="{t("Navigasi footer", "Footer navigation")}">{links}</nav><div class="footer-contact"><a href="{url("contact")}">{t("Hubungi Pasukan CPE", "Contact the CPE Team")}</a><a href="tel:+{PHONE}">+60 14-336 2622</a></div></div><div class="footer-bottom"><span>© 2026 CPE Patch Energy Solutions</span><span>{t("Fotografi ilustrasi digunakan di laman ini.", "Illustrative photography is used on this website.")}</span><a href="{url("privacy")}">{t("Polisi Privasi", "Privacy Policy")}</a></div></div></footer><a class="floating-contact" href="{e(wa())}" target="_blank" rel="noopener noreferrer" aria-label="{t("WhatsApp Pasukan CPE", "WhatsApp the CPE Team")}">{icon("whatsapp")}<span>{t("Pasukan CPE", "CPE Team")}</span></a>'''

def paragraph(ms, en):
    return '<p>' + t(ms, en) + '</p>'

def article_section(heading, paragraphs, bullets=None):
    result = '<h2>' + t(*heading) + '</h2>'
    for ms, en in paragraphs:
        result += paragraph(ms, en)
    if bullets:
        result += '<ul>' + ''.join('<li>' + t(*item) + '</li>' for item in bullets) + '</ul>'
    return result

def article_shell(content, page, image=None):
    aside = '<aside class="article-aside"><h3>' + t('Teruskan penerokaan', 'Keep exploring') + '</h3>'
    for related in ['about', 'suitability', 'measurement', 'plans', 'guides']:
        if related != page:
            aside += '<a href="' + url(related) + '">' + t(*PAGE_NAMES[related]) + '</a>'
    aside += button(t('Bincang dengan Pasukan CPE', 'Speak with the CPE Team')) + '</aside>'
    if image:
        content = photo(image, raw('Imej ilustrasi untuk penerangan, bukan produk atau pemasangan sebenar', 'Illustrative explanatory image, not an actual product or installation'), 'article-photo') + content
    return '<section class="section"><div class="wrap article-layout"><article class="article-content">' + content + '</article>' + aside + '</div></section>'

def details(page):
    if page == 'about':
        content = article_section(('Aplikasi pada peralatan yang sesuai', 'Application on suitable equipment'), [
            ('CPE Patch Energy Solutions memberi tumpuan kepada aplikasi CPE Patch pada compressor aircond dan chiller. Langkah pertama ialah memahami keadaan peralatan dan corak penggunaan premis.',
             'CPE Patch Energy Solutions focuses on CPE Patch applications on air-conditioning and chiller compressors. The first step is understanding equipment conditions and premises usage.'),
            ('Penilaian awal membantu menentukan konfigurasi, langkah pemasangan dan maklumat pengukuran yang perlu dibincangkan. Foto di laman ini ialah ilustrasi peralatan dan premis, bukan foto produk atau hasil pelanggan sebenar.',
             'An initial assessment helps determine the configuration, installation steps and measurement information to discuss. Website photographs illustrate equipment and premises; they are not actual product or customer-result photographs.'),
        ])
        content += article_section(('Perkara yang boleh anda minta', 'Information you can request'), [], [
            ('Maklumat teknikal produk dan peralatan yang serasi.', 'Technical product information and compatible equipment.'),
            ('Cadangan pemasangan serta keperluan operasi.', 'An installation proposal and operating requirements.'),
            ('Laporan pengukuran dan rujukan pemasangan yang tersedia.', 'Available measurement reports and installation references.'),
            ('Penerangan semua bayaran serta terma pelan.', 'An explanation of all payments and plan terms.'),
        ])
        return article_shell(content, page, 'equipment') + product()
    if page == 'suitability':
        content = article_section(('Semakan bermula dengan keadaan premis', 'A check starts with your premises conditions'), [
            ('Kategori premis sahaja belum menentukan kesesuaian. Sediakan jenis unit, kapasiti, bilangan peralatan, keadaan sistem dan waktu operasi untuk perbincangan awal.',
             'Premises category alone does not determine suitability. Prepare equipment types, capacities, unit counts, system conditions and operating hours for the initial discussion.'),
        ])
        content += article_section(('Sebelum pemasangan', 'Before installation'), [], [
            ('Semak konfigurasi pemasangan yang dicadangkan.', 'Review the proposed installation configuration.'),
            ('Sahkan tempoh pemasangan dan keperluan akses.', 'Confirm installation duration and access requirements.'),
            ('Bincang sebarang kesan kepada operasi.', 'Discuss any impact on operations.'),
            ('Minta penjelasan keserasian dengan syarat warranty pengeluar.', 'Request an explanation of compatibility with the manufacturer’s warranty conditions.'),
        ])
        return article_shell(content, page, 'process') + suitability() + process()
    if page == 'measurement':
        content = article_section(('Apa yang dinyatakan dalam brosur', 'What the brochure states'), [
            ('Brosur CPE menyatakan 9% penjimatan pada compressor. Angka ini perlu dibaca bersama laporan pengukuran, jenis peralatan, tempoh dan keadaan ujian yang berkaitan.',
             'The CPE brochure states 9% savings on compressors. This figure should be read alongside the relevant measurement report, equipment type, period and test conditions.'),
            ('Angka penjimatan pada compressor tidak bersamaan secara automatik dengan peratus pengurangan seluruh bil. Peralatan lain dan corak operasi juga menyumbang kepada penggunaan premis.',
             'A compressor savings percentage does not automatically equal the percentage reduction in the whole bill. Other equipment and operating patterns also contribute to premises consumption.'),
        ])
        content += article_section(('Maklumat yang membantu anda menilai hasil', 'Information that helps you assess results'), [], [
            ('Data penggunaan sebelum dan selepas, pada skop yang sama.', 'Before-and-after usage data within the same scope.'),
            ('Tempoh pengukuran dan perubahan waktu operasi.', 'Measurement period and changes in operating hours.'),
            ('Perubahan pada beban peralatan dan keadaan premis.', 'Changes in equipment load and premises conditions.'),
            ('Sumber laporan dan pihak yang menjalankan pengukuran.', 'Report source and the party conducting the measurement.'),
        ])
        return article_shell(content, page, 'service') + measurement() + example()
    if page == 'plans':
        content = article_section(('Semak keseluruhan kos dan terma', 'Review the full costs and terms'), [
            ('Pelan sewa milik perlu dinilai berdasarkan cadangan rasmi untuk premis anda. Jumlah bayaran awal dan tempoh pemilikan perlu disahkan sebelum persetujuan.',
             'A rent-to-own plan should be assessed against the formal proposal for your premises. The initial payment amount and ownership duration must be confirmed before agreement.'),
            ('Contoh bayaran RM235 sebulan dalam brosur ialah sebahagian daripada satu konfigurasi contoh. Ia bukan harga tetap untuk setiap unit atau setiap premis.',
             'The brochure’s RM235 monthly payment is part of one example configuration. It is not a fixed price for every unit or premises.'),
        ])
        content += article_section(('Soalan sebelum bersetuju', 'Questions before agreeing'), [], [
            ('Apakah bayaran awal, dan adakah ia deposit atau bayaran sekali sahaja?', 'What is the initial payment, and is it a deposit or a one-off payment?'),
            ('Apakah jumlah bayaran bulanan dan semua bayaran sepanjang perjanjian?', 'What are the monthly payments and all charges over the agreement?'),
            ('Bilakah pemilikan dipindahkan dan apakah syaratnya?', 'When is ownership transferred, and under what conditions?'),
            ('Apakah skop sokongan, percubaan dan penamatan?', 'What are the support, trial and termination conditions?'),
        ])
        return article_shell(content, page) + plans() + example()
    if page == 'guides':
        guides = ''
        for key in ['savings-guide', 'preparation-guide']:
            guides += '<a class="guide-card" href="' + url(key) + '"><h2>' + t(*PAGE_NAMES[key]) + '</h2><p>' + t(*INTRO[key]) + '</p><span class="text-link">' + t('Baca panduan', 'Read the guide') + icon('arrow') + '</span></a>'
        return '<section class="section"><div class="wrap"><div class="guides-list">' + guides + '</div></div></section>'
    if page == 'savings-guide':
        content = article_section(('Bezakan skop pengukuran', 'Distinguish measurement scopes'), [
            ('Jika pengukuran dibuat pada compressor, hasilnya menerangkan penggunaan compressor itu. Jumlah bil premis merangkumi penggunaan peralatan lain yang turut beroperasi.',
             'If a measurement is made on a compressor, the result describes that compressor’s usage. The total premises bill includes other equipment operating at the premises.'),
            ('Dalam brosur, 9% penjimatan compressor dan 5.85% pengurangan bil ialah dua angka berbeza. Maklumat asas penggunaan diperlukan untuk menerangkan hubungannya.',
             'In the brochure, 9% compressor savings and a 5.85% bill reduction are two different figures. Baseline usage information is needed to explain their relationship.'),
        ])
        content += article_section(('Baca contoh bulanan secara lengkap', 'Read the complete monthly example'), [
            ('Contoh bil RM4,500.00 berkurang kepada RM4,236.75 memberikan perbezaan RM263.25. Selepas bayaran contoh RM235.00, baki ialah RM28.25 sebulan.',
             'The example bill falls from RM4,500.00 to RM4,236.75, a difference of RM263.25. After the example RM235.00 payment, the balance is RM28.25 per month.'),
            ('Kiraan ini belum memasukkan bayaran awal. Untuk menilai cadangan anda, semak semua bayaran, tempoh perjanjian dan andaian hasil. Angka brosur bukan jaminan bagi setiap premis.',
             'This calculation has not included the initial payment. To assess your proposal, review all payments, the agreement period and result assumptions. Brochure figures are not a guarantee for every premises.'),
        ])
        content += article_section(('Minta konteks bersama angka', 'Ask for context alongside figures'), [], [
            ('Peralatan apa yang diukur?', 'Which equipment was measured?'),
            ('Berapa lama pengukuran dijalankan?', 'How long did measurement take?'),
            ('Adakah waktu operasi dan beban berubah?', 'Did operating hours and load change?'),
            ('Adakah data asal dan laporan boleh disemak?', 'Can the original data and report be reviewed?'),
        ])
        return article_shell(content, page, 'interior')
    if page == 'preparation-guide':
        content = article_section(('Maklumat asas untuk perbincangan', 'Basic information for the discussion'), [], [
            ('Jenis premis dan lokasinya.', 'Premises type and location.'),
            ('Jenis, kapasiti dan bilangan aircond atau chiller.', 'Type, capacity and number of air-conditioning or chiller units.'),
            ('Waktu operasi harian dan jadual penggunaan.', 'Daily operating hours and usage schedule.'),
            ('Keadaan peralatan dan isu yang diketahui.', 'Equipment condition and known issues.'),
        ])
        content += article_section(('Bahan sokongan jika diminta', 'Supporting material if requested'), [
            ('Bil elektrik dan gambar label peralatan boleh membantu perbincangan lanjut. Pasukan CPE akan menerangkan maklumat yang diperlukan mengikut skop semakan.',
             'Electricity bills and photographs of equipment labels can support a further discussion. The CPE team will explain what information is needed for the review scope.'),
            ('Gunakan saluran yang dipersetujui dengan pasukan. Elakkan menghantar maklumat peribadi atau akaun yang tidak diperlukan untuk penilaian.',
             'Use a channel agreed with the team. Avoid sending personal or account information that is unnecessary for the assessment.'),
        ])
        content += article_section(('Perkara untuk dipersetujui', 'What to agree on'), [], [
            ('Skop semakan dan sama ada lawatan diperlukan.', 'The review scope and whether a visit is needed.'),
            ('Liputan lokasi dan jadual yang sesuai.', 'Location coverage and a suitable schedule.'),
            ('Kelayakan serta syarat semakan atau percubaan percuma.', 'Eligibility and conditions for a free check or trial.'),
            ('Cara cadangan dan hasil pengukuran akan diterangkan.', 'How the proposal and measurement results will be explained.'),
        ])
        return article_shell(content, page, 'process')
    if page == 'privacy':
        content = article_section(('Borang menyediakan mesej WhatsApp', 'The form prepares a WhatsApp message'), [
            ('Maklumat yang ditaip dalam borang diproses dalam pelayar anda untuk menyediakan mesej. Laman ini tidak mempunyai pangkalan data pertanyaan dan tidak menyimpan input borang.',
             'Information entered in the form is processed in your browser to prepare a message. This website has no enquiry database and does not store form input.'),
            ('Apabila anda memilih untuk meneruskan, nama, nombor telefon, lokasi, jenis premis dan nota pilihan dimasukkan ke pautan mesej WhatsApp. Anda boleh menyemak mesej sebelum menghantar.',
             'When you choose to continue, your name, telephone number, location, premises type and optional notes are included in a WhatsApp message link. You can review the message before sending.'),
        ])
        content += article_section(('Saluran pihak ketiga', 'Third-party channels'), [
            ('WhatsApp dan penyedia e-mel mempunyai syarat serta amalan privasi masing-masing. Maklumat yang anda hantar melalui saluran tersebut diterima oleh penerima pertanyaan anda.',
             'WhatsApp and email providers have their own terms and privacy practices. Information you send through those channels is received by your enquiry recipient.'),
            ('Laman ini tidak menggunakan kuki analitik atau penjejakan pengiklanan sendiri. Perkhidmatan hos mungkin memproses log teknikal dan maklumat akses mengikut polisinya.',
             'This website does not use its own analytics cookies or advertising tracking. The hosting service may process technical logs and access information under its policies.'),
        ])
        content += article_section(('Pertanyaan tentang maklumat anda', 'Questions about your information'), [
            ('Hubungi Pasukan CPE melalui saluran hubungan yang dipaparkan untuk pertanyaan mengenai maklumat yang anda telah hantar kepada pasukan.',
             'Contact the CPE team using the displayed contact channels with questions about information you have sent to the team.'),
        ])
        return article_shell(content, page)
    if page == 'contact':
        return ''

def lead(page):
    breadcrumbs = f'<nav class="breadcrumbs" aria-label="{t("Jejak halaman", "Breadcrumb")}"><a href="{url()}">{t("Utama", "Home")}</a><span aria-hidden="true">/</span>'
    if page.endswith('-guide'):
        breadcrumbs += f'<a href="{url("guides")}">{t("Panduan", "Guides")}</a><span aria-hidden="true">/</span>'
    breadcrumbs += '<span>' + t(*PAGE_NAMES[page]) + '</span></nav>'
    return '<section class="page-lead"><div class="wrap">' + breadcrumbs + '<h1>' + t(*PAGE_NAMES[page]) + '</h1><p>' + t(*INTRO[page]) + '</p></div></section>'

def head(page):
    title = raw(*PAGE_NAMES[page]) + ' | CPE Patch'
    description = raw(*INTRO[page])
    address = absolute(url(page))
    schema = [
        {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'CPE Patch Energy Solutions', 'url': absolute(url()), 'inLanguage': 'ms-MY' if LANG == 'ms' else 'en-MY'},
        {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'CPE Patch Energy Solutions', 'url': ORIGIN, 'contactPoint': {'@type': 'ContactPoint', 'telephone': '+' + PHONE, 'email': EMAIL, 'contactType': 'customer enquiries', 'availableLanguage': ['Malay', 'English']}},
    ]
    return f'''<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#0b2638"><link rel="canonical" href="{e(address)}"><link rel="alternate" hreflang="ms-MY" href="{e(absolute(url(page, "ms")))}"><link rel="alternate" hreflang="en-MY" href="{e(absolute(url(page, "en")))}"><link rel="alternate" hreflang="x-default" href="{e(absolute(url(page, "ms")))}"><meta property="og:type" content="website"><meta property="og:locale" content="{"ms_MY" if LANG == "ms" else "en_MY"}"><meta property="og:site_name" content="CPE Patch Energy Solutions"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(address)}"><meta property="og:image" content="{e(absolute("/assets/hero.webp"))}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="preload" href="/assets/fonts/manrope.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="{asset('site.css')}"><script src="{asset('vendor/gsap.min.js')}" defer></script><script src="{asset('vendor/ScrollTrigger.min.js')}" defer></script><script src="{asset('site.js')}" defer></script><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")}</script></head>'''

def render(page):
    if page == 'home':
        body = hero() + situation() + product() + suitability() + measurement() + example() + plans() + process() + team() + faq() + contact()
    else:
        body = lead(page) + details(page) + (faq() if page in ['about', 'suitability', 'contact'] else '') + contact()
    return '<!doctype html><html lang="' + LANG + '">' + head(page) + '<body><noscript><style>.faq-answer[hidden],.tab-panel[hidden],.step-description[hidden]{display:block!important}</style></noscript>' + sprite() + header(page) + '<main id="main"' + (' class="subpage"' if page != 'home' else '') + '>' + body + '</main>' + footer() + '</body></html>'

def build(origin):
    global LANG, ORIGIN, BASE_PATH
    ORIGIN = origin.rstrip('/')
    parsed_origin = urlsplit(ORIGIN)
    if parsed_origin.scheme not in ['http', 'https'] or not parsed_origin.netloc or parsed_origin.query or parsed_origin.fragment:
        raise ValueError('Origin must be an HTTP(S) site URL without a query or fragment.')
    BASE_PATH = parsed_origin.path.rstrip('/')
    shutil.copytree(ROOT / 'src' / 'assets', DIST / 'assets', dirs_exist_ok=True)
    for language in ['ms', 'en']:
        LANG = language
        for page in ROUTES:
            target = DIST / url(page).strip('/') / 'index.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(site_html(render(page)), encoding='utf-8')
    LANG = 'ms'
    root_page = site_html(render('home'))
    (DIST / 'index.html').write_text(root_page, encoding='utf-8')
    urls = [(page, language) for language in ['ms', 'en'] for page in ROUTES]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    for page, language in urls:
        sitemap += '<url><loc>' + xml_escape(absolute(url(page, language))) + '</loc>'
        for alternate, code in [('ms', 'ms-MY'), ('en', 'en-MY'), ('ms', 'x-default')]:
            sitemap += '<xhtml:link rel="alternate" hreflang="' + code + '" href="' + xml_escape(absolute(url(page, alternate)), {'"': '&quot;'}) + '"/>'
        sitemap += '</url>'
    sitemap += '</urlset>'
    (DIST / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (DIST / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + ORIGIN + '/sitemap.xml\n', encoding='utf-8')
    (DIST / '404.html').write_text('<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Halaman tidak ditemui | CPE Patch</title><meta name="robots" content="noindex"><link rel="stylesheet" href="/assets/site.css"></head><body><main class="section wrap"><h1>Halaman tidak ditemui.</h1><p style="margin-top:24px">Page not found.</p><a class="btn" style="margin-top:30px" href="/ms/">Kembali ke utama / Return home</a></main></body></html>', encoding='utf-8')
    (DIST / 'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#0b2638"/><path d="M45 17a21 21 0 1 0 0 30" stroke="#00b6aa" stroke-width="8" fill="none" stroke-linecap="round"/></svg>', encoding='utf-8')
    (DIST / '_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n  Content-Security-Policy: default-src \'self\'; script-src \'self\' \'unsafe-inline\'; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\'; connect-src \'self\'; base-uri \'self\'; form-action https://wa.me\n/assets/*\n  Cache-Control: public, max-age=86400\n', encoding='utf-8')
    not_found = DIST / '404.html'
    not_found_markup = not_found.read_text(encoding='utf-8').replace('</head>', '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"></head>')
    not_found.write_text(site_html(not_found_markup), encoding='utf-8')
    (DIST / '.nojekyll').touch()
    print(json.dumps({'pages': len(urls) + 2, 'origin': ORIGIN, 'languages': ['ms', 'en']}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', required=True)
    build(parser.parse_args().origin)
