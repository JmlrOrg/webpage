#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataSciece.changeDirOnImportExport setting
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'legacy'))
	print(os.getcwd())
except:
	pass


#%%
from bs4 import BeautifulSoup
import re
import os
import requests

VOL = 17
vol_page = requests.get(f'http://www.jmlr.org/papers/v{VOL}/')
soup = BeautifulSoup(vol_page.text, 'html.parser')


#%%
id_list = []
bib_url_list = []
pdf_url_list = []
abs_url_list = []

for a in soup.find_all(href=re.compile(r'/papers/v%s/([^\s]+).bib' % VOL)):
    tmp = a.attrs['href']
    print(tmp)
    p = re.compile(r'/papers/v%s/([^\s]+).bib' % VOL)
    print(p.match(tmp).groups())
    id0, = p.match(tmp).groups()

    bib_url_list.append(tmp)
    abs_url_list.append(tmp.replace('.bib', '.html'))
    pdf_url_list.append(f'/papers/volume{VOL}/{id0}/{id0}.pdf')
    dirname = "v%s/%s" % (VOL, id0)
    print(dirname)
    os.makedirs(dirname, exist_ok=True)


#%%
pdf_url_list

#%%
abs_url_list

#%%
import requests
chunk_size = 2000

for pdf_url in pdf_url_list:

    url = 'http://jmlr.org' + pdf_url
    print(url)
    r = requests.get(url, stream=True)

    file_name = pdf_url.split('/')[-1]
    with open('v%s/%s/%s' % (VOL, file_name[:-4], file_name), 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)


#%%
for bib_url in bib_url_list:
    print(bib_url)
    url = 'http://jmlr.org' + bib_url
    r = requests.get(url, stream=True)

    file_name = bib_url.split('/')[-1]
    with open('v%s/%s/%s' % (VOL, file_name[:-4], file_name), 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)


#%%
for abs_url in abs_url_list:
    print(abs_url)

#%%
import bibtexparser
import json

for (abs_url, bib_url) in zip(abs_url_list, bib_url_list):
#     print(bib_url)
    file_name = bib_url.split('/')[-1]
    f_path = 'v%s/%s/%s' % (VOL, file_name[:-4], file_name)
    with open(f_path) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

#     print(bib_database.entries)
#     print()
    
    info = {}
    info['id'] = bib_database.entries[0]['ID'].split(':')[-1]
    info['pages'] = [int(a) for a in bib_database.entries[0]['pages'].split('-')]
    info['issue'] = int(bib_database.entries[0]['number'])
    info['title'] = bib_database.entries[0]['title']
    info['volume'] = int(bib_database.entries[0]['volume'])
    info['year'] = int(bib_database.entries[0]['year'])
    info['authors'] = [a.strip() for a in bib_database.entries[0]['author'].split('and')]


    vol_page = requests.get('http://www.jmlr.org' + abs_url)
    soup = BeautifulSoup(vol_page.text, 'html.parser')

    t = soup.find(id='content')
    # n = t.find('\nAbstract\n\n') + len('\nAbstract\n\n')
    # t = t[n:].replace('\n', ' ').strip('[abs]')
    t = str(t)
    n = t.find('<h3>Abstract</h3>') + len('<h3>Abstract</h3>')
    t = t[n:]
    t = t.replace('\n', ' ')
    if t[:2] == '  ':
        t = t[2:]
    m = t.find('<font color="gray">')
    t = t[:m]

    info['abstract'] = t
    json_path = 'v%s/%s/info.json' % (info['volume'], info['id'])
    with open(json_path, 'w') as outfile:
        json.dump(info, outfile, sort_keys=True, indent=4, separators=(',', ': '))
    print(info)
    
    print()


#%%
bib_database.entries[0]


#%%



