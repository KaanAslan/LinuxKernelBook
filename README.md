# Linux Kernel — İşletim Sistemlerinin Tasarımı ve Gerçekleştirilmesi

[![Documentation Status](https://readthedocs.org/projects/linuxkernelbook/badge/?version=latest)](https://linuxkernelbook.readthedocs.io/tr/latest/?badge=latest)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

Linux çekirdeğinin iç mimarisini, tasarım kararlarını ve gerçekleştirim ayrıntılarını Türkçe olarak ele alan kapsamlı bir teknik kitap.

📖 **Çevrimiçi okumak için:** [linuxkernelbook.readthedocs.io](https://linuxkernelbook.readthedocs.io)

---

## Kullanılan Araçlar

| Araç | Sürüm / Notlar |
|------|----------------|
| [Sphinx](https://www.sphinx-doc.org/) | Belgeleme motoru |
| [sphinx-rtd-theme](https://sphinx-rtd-theme.readthedocs.io/) | ReadTheDocs teması |
| [ReadTheDocs](https://readthedocs.org/) | Yayın platformu |
| XeLaTeX / TeX Live | PDF üretimi (`xelatex` motoru) |
| Graphviz | Mimari ve veri yapısı diyagramları |
| Python 3 | Sphinx eklentileri ve yardımcı betikler |

## Yerel Derleme

Gereksinimler: Python 3.x, Sphinx, Graphviz

```bash
git clone https://github.com/KaanAslan/LinuxKernelBook.git
cd LinuxKernelBook
pip install -r docs/requirements.txt

# HTML
make -C docs html
open docs/build/html/index.html

# PDF (XeLaTeX gerektirir)
make -C docs latexpdf
```

## Lisans

Bu kitabın içeriği [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) lisansı altında yayımlanmaktadır.
Ticari amaçla kullanılamaz; atıf yapılarak ve aynı lisansla paylaşılabilir.
