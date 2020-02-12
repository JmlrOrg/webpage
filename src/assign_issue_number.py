"""
Usage:

   python bin/gen_json.py vol_number id_number1 id_number2
"""


import sys
import os
import codecs
import re
import glob
import json
from PyPDF2 import PdfFileReader

# extract pages from pdf
# - volume is the volume number
# - paper id is something like '19-132'
def extract_new_information(volume, paper_id):
    pdf_file = 'v%s/%s/%s.pdf' % (volume, paper_id, paper_id)

    with open(pdf_file, 'rb') as pdf:
        pages = [1, PdfFileReader(pdf).getNumPages()]

    return {
        'pages':     pages,
        'id':        paper_id,
        'volume':    volume,
        'year':      1999 + int(volume),
    }


def compute_issue(vol, id):
    # scan through all info.json files and assign the first free slot
    issue = 0
    ids_paths = glob.glob('v%s/??-???/info.json' % vol)
    for id_path in ids_paths:
        with open(id_path, 'r') as fp:
            ids_info = json.load(fp)
        issue = max(issue, ids_info.get('issue', 0))
    return issue + 1



if __name__ == '__main__':
    vol = sys.argv[1]
    ids = sys.argv[2:]
    for id in ids:
        new_info = extract_new_information(int(vol), id)
        new_info['issue'] = compute_issue(vol, id)
        print('Issue: %s' % new_info['issue'])

        info_path = 'v%s/%s/info.json' % (vol, id)
        with open(info_path, 'r') as f:
            current_info = json.load(f)

        info = {**current_info, **new_info}

        if os.path.exists(info_path):
            os.remove(info_path)
        with open(info_path, 'w') as outfile:
            out = json.dump(info, outfile, sort_keys=True, indent=4, separators=(',', ': '))

        print('Done %s' % id)
