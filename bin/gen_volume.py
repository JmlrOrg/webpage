import json
import os
import sys
import glob
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape


accents = [
   ["'a", "á"], ['"a', "ä"], ["^a", "â"], ["`a", "à"],
   ["'e", "é"], ['"e', "ë"], ["^e", "ê"], ["`e", "è"],
   ["'i", "í"], ['"i', "ï"], ["^i", "î"], ["`i", "ì"],
   ["'o", "ó"], ['"o', "ö"], ["^o", "ô"], ["`o", "ò"],
   ["'u", "ú"], ['"u', "ü"], ["^u", "û"], ["`u", "ù"],
   ["cc", "ç"], ['ug', 'ğ'], ['"U', "Ü"], ['"u', "ü"],
   ["vZ", "Ž"], ['vc', 'č'], ['Ho', "ő"], ['O', "Ø"],
   ['o', "ø"], ['l', 'ł'], ["'n", "ń"], ['v{s}', 'š']
]

def xml_string(text):
    text = text.replace("``", u"“")
    text = text.replace("''", u"”")

    for tex, utf8 in accents:
        # utf8 = utf8.decode('utf-8')
        text = text.replace('{\\%s}' % tex, utf8)          # {\"a}
        text = text.replace('\\%s' % tex, utf8)            # \"a
        try:
            text = text.replace('\\%s{%s}' % tuple(tex), utf8) # \"{a}
        except TypeError:
            pass
    return text


def get_info(vol):
    os.chdir('data/v%s' % vol)
    ids = glob.glob('??-???')
    info = []
    for id in ids:
        with open('%s/info.json' % id, 'r') as fp:
            # some cleanup for the html display
            id_info = json.load(fp)
            id_info['authors_string'] = xml_string(', '.join(id_info['authors']))
            id_info['abstract'] = id_info['abstract']
            id_info['authors_bibtex'] = ' and '.join(id_info['authors'])
        info.append(id_info)
    os.chdir('../..')
    # sort by issue
    return sorted(info, key=lambda k: k['issue'])

def process(info):
    vol = info['volume']
    id = info['id']
    with open('output/papers/v%s/%s.html' % (vol, id), 'w') as f:
        editorial_board_template = env.get_template('paper.html')
        out = editorial_board_template.render(**info)
        f.write(out)
    with open('output/papers/v%s/%s.bib' % (vol, id), 'w') as f:
        editorial_board_template = env.get_template('biblio.bib')
        out = editorial_board_template.render(**info)
        f.write(out)
    papers_dir = 'output/papers/'
    os.makedirs('output/papers/volume%s/%s' % (vol, id), exist_ok=True)        
    shutil.copy(
        'data/v%s/%s/%s.pdf' % (vol, id, id),
        'output/papers/volume%s/%s/%s.pdf' % (vol, id, id))




if __name__ == '__main__':

    vol = sys.argv[1]

    if not os.path.exists('output/papers/v%s' % vol):
        os.makedirs('output/papers/v%s' % vol, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    info_list = get_info(vol)
    for info in info_list:
        process(info)

    # render volume html file
    with open('output/papers/v%s/index.html' % vol, 'w') as f:
        editorial_board_template = env.get_template('volume.html')
        out = editorial_board_template.render(info_list=info_list, volume=vol)
        f.write(out)
