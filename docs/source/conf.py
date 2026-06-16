# -- Proje bilgileri -----------------------------------------------------
project = 'Linux Kernel - İşletim Sistemlerinin Tasarımı ve Gerçekleştirilmesi'
copyright = '2025, Kaan Aslan'
author = 'Kaan Aslan'
release = '1.0.0'

# -- Genel yapılandırma ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Python docstring'lerinden otomatik döküman
    'sphinx.ext.viewcode',     # Kaynak koduna link
    'sphinx.ext.napoleon',     # Google/NumPy stil docstring desteği
    'sphinx.ext.intersphinx',  # Diğer projelere link
    'sphinx.ext.graphviz',
]

graphviz_output_format = 'svg'

templates_path = ['_templates']
exclude_patterns = []

language = 'tr'  # veya 'en'

# -- HTML çıktı seçenekleri ----------------------------------------------
html_theme = 'sphinx_rtd_theme'         # Read the Docs teması
html_static_path = ['_static']
html_logo = '_static/logo.jpeg'         # İsteğe bağlı logo
html_favicon = '_static/favicon.ico'    # İsteğe bağlı favicon
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
        \newfontfamily{\boxfont}{[DejaVuSansMono.ttf]}[Path=/usr/local/texlive/2026/texmf-dist/fonts/truetype/public/dejavu/]
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
templates_path = ['_templates']
