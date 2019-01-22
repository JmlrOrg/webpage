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


def clean_name(name):
    name = re.sub(r'\\thanks.*$', '', name)
    name = re.sub(r'\\email.*$', '', name)
    name = re.sub(r'\\\\', ' ', name)
    name = re.sub(r'\\footnotemark.*$', '', name)
    name = re.sub(r'\\ddag.*$', '', name)
    name = re.sub(r'\\dag.*$', '', name)
    name = name.strip()
    return name

def clean_abstract(abstract):
    abstract = re.compile(r'^\s*%.*$', flags=re.MULTILINE).sub('', abstract).replace("\r", "")
    abstract = abstract.replace("\n", ' ').replace('~', ' ')
    abstract = re.sub(r'\s+', ' ', abstract).strip()
    return abstract

def clean_title(title):
    title = re.sub(r'\\thanks.*$', '', title)
    title.strip()
    return title
    

# extract title, author, pages, abstract from tex source
# - volume is the volume number
# - paper id is something like 'alquier13a'
def extract_information(volume, paper_id):
    src_file = 'v%s/%s/source/%s.tex' % (volume, paper_id, paper_id)
    pdf_file = 'v%s/%s/%s.pdf' % (volume, paper_id, paper_id)

    print(src_file)
    with codecs.open(src_file, 'r', 'latin1') as ins:
        src = ins.read()
        # filter all comments to avoid confusing the parser
        src = re.sub(re.compile(r'^\s*%.*$', re.M), '', src)
        src = re.sub(re.compile(r'([^\\])%.*$', re.M), r'\1', src)

        header = re.split(r"\\maketitle", src)[0]
        names = re.compile(r'\\name(.*)$', flags=re.MULTILINE).findall(header)
        names = [clean_name(name) for name in names]

        # This cannot handle the case other LaTeX command is used in title
        title = re.search(r'\\title\{([^}]*)\}', header).group(1)
        title = re.sub(r'\s+', ' ', title.replace(r'\\', ' '))
        title = clean_title(title)
        title = title.replace('\n', '')

        email_regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
"\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
        emails = email_regex.findall(header)
        emails = [str(e[0]) for e in emails]

        with open(pdf_file, 'rb') as pdf:            
            pages = [1, PdfFileReader(pdf).getNumPages()]

        abstract = re.search(r'\\begin\{abstract\}(.*)\\end\{abstract\}', src, re.DOTALL).group(1)
        abstract = clean_abstract(abstract)

        return {
            'authors':    names,
            'title':     title,
            'pages':     pages,
            'abstract':  abstract,
            'id':        paper_id,
            'volume':    volume,
            'year':      1999 + int(volume),  # datetime.date.today().year
            'emails':   emails
        }


def compute_issue(vol, id):
    # scan through all inf.json files and assign the first free slot
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
        info = extract_information(int(vol), id)
        info['issue'] = compute_issue(vol, id)
        print('Issue: %s' % info['issue'])

        json_path = 'v%s/%s/info.json' % (vol, id)
        if os.path.exists(json_path):
            os.remove(json_path)
        with open(json_path, 'w') as outfile:
            out = json.dump(info, outfile, sort_keys=True, indent=4, separators=(',', ': '))
        with open(json_path, 'r') as outfile:
            print(outfile.read())
        # print(emails)
        # print()
        # with open('v%s/%s/.emails.txt' % (vol, id), 'w') as outfile:
        #     outfile.write("\n".join(emails))
        #     outfile.write("\n")
        print('Done %s' % id)
