import json
import os
import sys
import glob
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape

import utils

# only build the new website
PREFIXES = ('/beta/', '/')

def get_info(vol):
    os.chdir('v%s' % vol)
    ids = glob.glob('??-???')
    info_list = []
    for id in ids:
        with open('%s/info.json' % id, 'r') as fp:
            # some cleanup for the html display
            id_info = json.load(fp)
            id_info['title'] = utils.xml_string(id_info['title'])
            # some authors write {TeXt} to ensure that its capitalized correctly in latex
            id_info['title'].replace('{', '').replace('}', '')

            id_info['authors_string'] = utils.xml_string(', '.join(id_info['authors']))
            id_info['abstract'] = utils.xml_string(id_info['abstract'])
            id_info['authors_bibtex'] = ' and '.join(id_info['authors'])
        info_list.append(id_info)
    os.chdir('..')
    # sort by issue
    return sorted(info_list, key=lambda k: k['issue'])

def process(info, prefix, env):
    vol = info['volume']
    id = info['id']
    if 'title_html' not in info:
        info['title_html'] = info['title']

    if 'authors_html' not in info:
        info['authors_html'] = [utils.xml_string(a) for a in info['authors']]

    if 'title_bibtex' not in info:
        info['title_bibtex'] = info['title']
    

    with open('output' + prefix + 'papers/v%s/%s.html' % (vol, id), 'w') as f:

        editorial_board_template = env.get_template('papers/item.html')
        out = editorial_board_template.render(**info, prefix=prefix)
        f.write(out)
    with open('output' + prefix + 'papers/v%s/%s.bib' % (vol, id), 'w') as f:
        editorial_board_template = env.get_template('papers/biblio.bib')
        out = editorial_board_template.render(**info, prefix=prefix)
        f.write(out)
    papers_dir = 'output' + prefix + 'papers/'
    os.makedirs('output' + prefix + 'papers/volume%s/%s' % (vol, id), exist_ok=True)
    shutil.copy(
        'v%s/%s/%s.pdf' % (vol, id, id),
        'output' + prefix + 'papers/volume%s/%s/%s.pdf' % (vol, id, id))




if __name__ == '__main__':

    vol = sys.argv[1]

    for prefix in PREFIXES:
        os.makedirs('output' + prefix + 'papers/v%s' % vol, exist_ok=True)
        os.makedirs('output' + prefix + 'mloss/', exist_ok=True)

        env = Environment(
            loader=FileSystemLoader('templates/' + prefix),
            autoescape=select_autoescape(['html', 'xml'])
        )

        info_list = get_info(vol)
        for info in info_list:
            process(info, prefix, env)

        # render volume html file
        with open('output' + prefix + 'papers/v%s/index.html' % vol, 'w') as f:
            volume_template = env.get_template('papers/volume.html')
            out = volume_template.render(info_list=info_list, vol=vol, prefix=prefix)
            f.write(out)
        with open('output' + prefix + 'papers/index.html', 'w') as f:
            editorial_board_template = env.get_template('papers/index.html')
            out = editorial_board_template.render(info_list=info_list, volume=vol, prefix=prefix)
            f.write(out)

        # rss feed
        with open('output' + prefix + 'jmlr.xml', 'w') as f:
            # sort by issue
            info_by_issue = sorted(info_list, key=lambda k: k['issue'])[::-1]
            editorial_board_template = env.get_template('jmlr.xml')
            out = editorial_board_template.render(info_list=info_by_issue, vol=vol, prefix=prefix)
            f.write(out)


        # mloss webpage
        # XXX FIXME: vol 19 is hardcoded
        if vol == '19':
            with open('output' + prefix + 'mloss/index.html', 'w') as f:
                info_mloss = filter(
                lambda x: x.get('special_issue', '') == 'MLOSS', info_list)
                editorial_board_template = env.get_template('mloss/index.html')
                out = editorial_board_template.render(info_list=info_mloss, volume=vol)
                f.write(out)
