import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

accents = [
   ["'a", "á"], ['"a', "ä"], ["^a", "â"], ["`a", "à"],
   ["'e", "é"], ['"e', "ë"], ["^e", "ê"], ["`e", "è"],
   ["'i", "í"], ['"i', "ï"], ["^i", "î"], ["`i", "ì"],
   ["'o", "ó"], ['"o', "ö"], ["^o", "ô"], ["`o", "ò"],
   ["'u", "ú"], ['"u', "ü"], ["^u", "û"], ["`u", "ù"],
   ["cc", "ç"], ['ug', 'ğ'], ['"U', "Ü"], ['"u', "ü"],
   ["vZ", "Ž"], ['vc', 'č'], ['Ho', "ő"], ['O', "Ø"],
   ['o', "ø"], ['l', 'ł'], ["'n", "ń"], ['vs', 'š'], 
   ['vS', 'Š'], ['L', 'Ł'], ['&', '&amp;'], ["'c", "ć"],
   ['vc', 'č'], ["cC", "Ç"], ['ua', 'ă'],
   ['~n', 'ñ']
]

def xml_string(text):
    text = text.replace("``", u"“")
    text = text.replace("''", u"”")

    for tex, utf8 in accents:
        # utf8 = utf8.decode('utf-8')
        text = text.replace('{{\\%s}}' % tex, utf8)          # {{\"a}}
        # text = text.replace('\\%s' % tex, utf8)            # \"a
        if len(tex) == 2:
            try:
                text = text.replace('{\\%s{%s}}' % tuple(tex), utf8) 
            except TypeError:
                pass
            # try:
            #     text = text.replace('{{\\\\%s%s}}' % tuple(tex), utf8) # {{\"a}}
            # except TypeError:
            #     pass
        # sometimes words are but in brackets in bibtex to make it {CapiTaliZed} correctly
    # text = text.replace('{', '').replace('}', '')
    return text


def authors2string(auth_list):
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