import json
import os
import sys
import glob
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape

import utils


def get_info(vol):
    os.chdir('v%s' % vol)
    ids = glob.glob('??-???')
    info = []
    for id in ids:
        with open('%s/info.json' % id, 'r') as fp:
            # some cleanup for the html display
            id_info = json.load(fp)
            id_info['authors_string'] = utils.xml_string(', '.join(id_info['authors']))
            id_info['abstract'] = utils.xml_string(id_info['abstract'])
            id_info['authors_bibtex'] = ' and '.join(id_info['authors'])
        info.append(id_info)
    os.chdir('..')
    # sort by issue
    return sorted(info, key=lambda k: k['issue'])

def process(info):
    vol = info['volume']
    id = info['id']
    if 'title_html' not in info:
        info['title_html'] = info['title']

    if 'title_bibtex' not in info:
        info['title_bibtex'] = info['title']

    with open('output/papers/v%s/%s.html' % (vol, id), 'w') as f:

        editorial_board_template = env.get_template('papers/item.html')
        out = editorial_board_template.render(**info)
        f.write(out)
    with open('output/papers/v%s/%s.bib' % (vol, id), 'w') as f:
        editorial_board_template = env.get_template('papers/biblio.bib')
        out = editorial_board_template.render(**info)
        f.write(out)
    papers_dir = 'output/papers/'
    os.makedirs('output/papers/volume%s/%s' % (vol, id), exist_ok=True)
    shutil.copy(
        'v%s/%s/%s.pdf' % (vol, id, id),
        'output/papers/volume%s/%s/%s.pdf' % (vol, id, id))




if __name__ == '__main__':

    vol = sys.argv[1]

    os.makedirs('output/papers/v%s' % vol, exist_ok=True)
    os.makedirs('output/mloss/', exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    info_list = get_info(vol)
    for info in info_list:
        process(info)

    # render volume html file
    with open('output/papers/v%s/index.html' % vol, 'w') as f:
        volume_template = env.get_template('papers/volume.html')
        out = volume_template.render(info_list=info_list, vol=vol)
        f.write(out)
    with open('output/papers/index.html', 'w') as f:
        editorial_board_template = env.get_template('papers/index.html')
        out = editorial_board_template.render(info_list=info_list, volume=vol)
        f.write(out)

    # rss feed
    with open('output/jmlr.xml', 'w') as f:
        # sort by issue
        info_by_issue = sorted(info_list, key=lambda k: k['issue'])[::-1]
        editorial_board_template = env.get_template('jmlr.xml')
        out = editorial_board_template.render(info_list=info_by_issue, vol=vol)
        f.write(out)


    # mloss webpage
    with open('output/mloss/index.html', 'w') as f:
        info_mloss = filter(
        lambda x: x.get('special_issue', '') == 'MLOSS', info_list)
        editorial_board_template = env.get_template('mloss/index.html')
        out = editorial_board_template.render(info_list=info_mloss, volume=vol)
        f.write(out)
