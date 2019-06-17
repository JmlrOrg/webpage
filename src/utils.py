import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

accents = [
   ["'a", "á"], ['"a', "ä"], ["^a", "â"], ["`a", "à"], ["~a", "ã"],
   ["'e", "é"], ["'E", "É"], ['"e', "ë"], ["^e", "ê"], ["`e", "è"],
   ["'i", "í"], ['"i', "ï"], ["^i", "î"], ["`i", "ì"],
   ["'o", "ó"], ['"o', "ö"], ["^o", "ô"], ["`o", "ò"],
   ["'u", "ú"], ['"u', "ü"], ["^u", "û"], ["`u", "ù"],
   ['"U', "Ü"], ['"u', "ü"],
   ['O', "Ø"],
   ['o', "ø"], ['l', 'ł'], ["'n", "ń"],
   ['L', 'Ł'], ['&', '&amp;'], ["'c", "ć"],
   ['~n', 'ñ'], ["'n", "ń"]
]

# this are combinations of the form {\a{b}}
# where a is the first character and b the second one
accents2 = [
    ['vS', 'Š'], ['vs', 'š'], ['vc', 'č'], ["cC", "Ç"], ['ua', 'ă'],  ['Ho', "ő"], ["vZ", "Ž"],["cc", "ç"], ['ug', 'ğ'], ['.z', 'ż']
]

def xml_string(text):
    text = text.replace("``", u"“")
    text = text.replace("''", u"”")

    for tex, utf8 in accents:
        # utf8 = utf8.decode('utf-8')
        text = text.replace('{{\\%s}}' % tex, utf8)          # {{\"a}}
        # text = text.replace('\\%s' % tex, utf8)            # \"a
    for tex, utf8 in accents2:
        text = text.replace('{\\%s{%s}}' % tuple(tex), utf8)
    return text


def authors2string(auth_list):
    auth = ""
    for a in auth_list:
        auth += xml_string(a) + ", "
    return auth[:-2]
    """Return authors list as a string"""
    template = """@article{JMLR:YYY,
  author  = {%s},
  title   = {XXX},
  journal = {Journal of Machine Learning Research},
  year    = {2016}
  }
"""
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    tmp = template % ' and '.join(auth_list)
    bib_database = bibtexparser.loads(tmp, parser=parser)
    return bib_database.entries[0]['author'].replace(' and ', ', ')
