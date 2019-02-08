import pytest
import glob
import json
from bs4 import BeautifulSoup

# local imports
import sys
import os
curpath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, curpath + '/../')
import utils

all_volumes = [18, 19, 20]

PREFIX = "/beta/"


def test_xml_string():
    t = r"\mathcal{O}"
    assert utils.xml_string(t) == t

def paper_iterator(volume):
    paper_dirs = glob.glob(f'v{volume}/??-???')
    for paper_dir in paper_dirs:
        paper_id = paper_dir[-6:]
        with open(f'output{PREFIX}papers/v{volume}/{paper_id}.html') as html_file:
            html = html_file.read()
        soup = BeautifulSoup(html, 'html.parser')
        with open(f'{paper_dir}/info.json', 'r') as json_file:
            info = json.load(json_file)
        yield soup, info


@pytest.mark.parametrize("volume", all_volumes)
def test_paper_json(volume):
    # check that json info file has all necessary fields
    for soup, info in paper_iterator(volume):
        for attr in ['abstract', 'authors', 'id',  'issue', 'pages', 'title', 'volume', 'year']:
            assert attr in info.keys()
        if 'special_issue' in info.keys():
            if info['special_issue'] == 'MLOSS':
                fields = [u[0] for u in info['extra_links']]
                # make sure that there's a code in the extra links
                assert 'code' in fields

@pytest.mark.parametrize("volume", all_volumes)
def test_paper_title(volume):
    for soup, info in paper_iterator(volume):
        assert soup.title.string == utils.xml_string(info['title'])

@pytest.mark.parametrize("volume", all_volumes)
def test_paper_metadata(volume):
    for soup, info in paper_iterator(volume):
        citation_title = soup.find_all(attrs={"name": "citation_title"})
        assert len(citation_title) == 1
        if 'title_html' in info.keys():
            citation_title[0]['content'] == info['title_html']
        else:
            assert citation_title[0]['content'] == utils.xml_string(info['title'])

        citation_journal = soup.find_all(attrs={"name": "citation_journal_title"})
        assert len(citation_journal) == 1
        assert citation_journal[0]['content'] == "Journal of Machine Learning Research"

        citation_issn = soup.find_all(attrs={"name": "citation_issn"})
        assert len(citation_issn) == 1
        assert citation_issn[0]['content'] == "1533-7928"

        citation_authors = soup.find_all(attrs={"name": "citation_author"})
        citation_authors = set([c['content'] for c in citation_authors])
        set_authors = set([utils.xml_string(c) for c in info['authors']])

        assert citation_authors == set_authors

        



@pytest.mark.parametrize("volume", all_volumes)
def test_pdf_exists(volume):
    for soup, info in paper_iterator(volume):
        citation_pdf = soup.find_all(attrs={"name": "citation_pdf_url"})
        assert len(citation_pdf) == 1
        citation_pdf = citation_pdf[0]['content']

        citation_pdf2 = soup.find_all(id='pdf')
        assert len(citation_pdf2) == 1
        citation_pdf2 = citation_pdf2[0]['href']

        assert citation_pdf2 == citation_pdf


@pytest.mark.parametrize("volume", all_volumes)
def test_issue_number(volume):
    all_issues = []
    for soup, info in paper_iterator(volume):
        all_issues.append(info['issue'])
    all_issues.sort()

    # check that the volume has all consecutive issue
    # numbers
    for i in range(len(all_issues)):
        assert all_issues[i] == i+1

