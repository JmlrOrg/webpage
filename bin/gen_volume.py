import json
import os
import sys
import glob
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape


def process(vol, id, issue):
    with open('data/v%s/%s/info.json' % (vol, id), 'r') as fp:
        ids_info = json.load(fp)
        ids_info['authors_string'] = ', '.join(ids_info['authors'])
        ids_info['authors_bibtex'] = ' and '.join(ids_info['authors'])
    with open('output/papers/v%s/%s.html' % (vol, id), 'w') as f:
        editorial_board_template = env.get_template('old/paper.html')
        out = editorial_board_template.render(**ids_info)
        f.write(out)
    with open('output/papers/v%s/%s.bib' % (vol, id), 'w') as f:
        editorial_board_template = env.get_template('biblio.bib')
        out = editorial_board_template.render(**ids_info)
        f.write(out)
    papers_dir = 'output/papers/'
    if not os.path.exists('output/papers/volume%s' % vol):
        os.makedirs('output/papers/volume%s' % vol, exist_ok=True)
    shutil.copy(
        'data/v%s/%s/%s.pdf' % (vol, id, id),
        'output/papers/volume%s/%s.pdf' % (vol, id))

if __name__ == '__main__':

    vol = sys.argv[1]

    if not os.path.exists('output/papers/v%s' % vol):
        os.makedirs('output/papers/v%s' % vol, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    

    ids = [id.replace('data/v19/', '') for id in glob.glob('data/v%s/??-???' % vol)]
    [process(vol, id, issue+1) for issue, id in enumerate(ids)]
