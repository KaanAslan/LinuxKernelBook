# -- Proje bilgileri -----------------------------------------------------
project = 'Linux Kernel - İşletim Sistemlerinin Tasarımı ve Gerçekleştirilmesi'
copyright = 'C ve Sistem Programcıları Derneği'
author = 'Kaan KAAN & Sebahat ERSOY'
release = '1.0.0'

# -- Genel yapılandırma ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.graphviz',
]

graphviz_output_format = 'png'

templates_path = ['_templates']
exclude_patterns = []

language = 'tr'

# -- HTML çıktı seçenekleri ----------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/logo.jpeg'
html_favicon = '_static/favicon.ico'
html_css_files = ['custom.css']

# -- Tema seçenekleri ---------------------------------------------------
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}

latex_elements = {
    'papersize': 'a4paper',
    'geometry': r'\usepackage[a4paper, top=2cm, bottom=2cm, left=1.5cm, right=1.5cm]{geometry}',
    'preamble': r'''
        \usepackage{fontspec}
        \usepackage{newunicodechar}
        \newunicodechar{≈}{\ensuremath{\approx}}
        \newunicodechar{×}{\ensuremath{\times}}
        \newunicodechar{→}{\ensuremath{\rightarrow}}
        \newunicodechar{←}{\ensuremath{\leftarrow}}
        \newunicodechar{≥}{\ensuremath{\geq}}
        \newunicodechar{≤}{\ensuremath{\leq}}
        \newfontfamily{\boxfont}[Path=/usr/share/fonts/truetype/dejavu/]{DejaVuSansMono.ttf}
        \newunicodechar{┌}{{\boxfont\char"250C}}
        \newunicodechar{┐}{{\boxfont\char"2510}}
        \newunicodechar{└}{{\boxfont\char"2514}}
        \newunicodechar{┘}{{\boxfont\char"2518}}
        \newunicodechar{├}{{\boxfont\char"251C}}
        \newunicodechar{┤}{{\boxfont\char"2524}}
        \newunicodechar{┬}{{\boxfont\char"252C}}
        \newunicodechar{┴}{{\boxfont\char"2534}}
        \newunicodechar{┼}{{\boxfont\char"253C}}
        \newunicodechar{─}{{\boxfont\char"2500}}
        \newunicodechar{│}{{\boxfont\char"2502}}
    ''',
}

latex_engine = 'xelatex'
latex_additional_files = ['_static/fontawesome7.sty']

html_meta = {
    "description": "Linux Kernel - İşletim Sistemlerinin Tasarımı ve Gerçekleştirilmesi",
    "keywords": (
        "linux kernel, işletim sistemleri, işletim sistemlerinin tasarımı, dosya sistemi, çekirdek senkronizasayonu, " +
        "proses yönetimi, çizelgeleme, bekleme kuyrukları"
    )
}
