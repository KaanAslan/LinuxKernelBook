# -- Proje bilgileri -----------------------------------------------------
project = 'LinuxKernelBook'
copyright = '2025, Kaan Aslan'
author = 'Kaan Aslan'
release = '1.0.0'

# -- Genel yapılandırma ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Python docstring'lerinden otomatik döküman
    'sphinx.ext.viewcode',     # Kaynak koduna link
    'sphinx.ext.napoleon',     # Google/NumPy stil docstring desteği
    'sphinx.ext.intersphinx',  # Diğer projelere link
]

templates_path = ['_templates']
exclude_patterns = []

language = 'tr'  # veya 'en'

# -- HTML çıktı seçenekleri ----------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Read the Docs teması
html_static_path = ['_static']
html_logo = '_static/logo.png'  # İsteğe bağlı logo
html_favicon = '_static/favicon.ico'  # İsteğe bağlı favicon

# -- Tema seçenekleri ---------------------------------------------------
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}
