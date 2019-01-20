import pytest
import glob
import json
from bs4 import BeautifulSoup

# local imports
import sys, os
curpath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, curpath + '/../')
import utils

all_volumes = [19, 20]

def paper_iterator(volume):
    paper_dirs = glob.glob(f'v{volume}/??-???')
    for paper_dir in paper_dirs:
        paper_id = paper_dir[-6:]
        with open(f'output/papers/v{volume}/{paper_id}.html') as html_file:
            html = html_file.read()
        soup = BeautifulSoup(html, 'html.parser')
        with open(f'{paper_dir}/info.json', 'r') as json_file:
            info = json.load(json_file)
        yield soup, info


@pytest.mark.parametrize("volume", all_volumes)
def test_paper_title(volume):
    for soup, info in paper_iterator(volume):
        assert soup.title.string == info['title']

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


@pytest.mark.parametrize("volume", all_volumes)
def test_pdf_exists(volume):
    for soup, info in paper_iterator(volume):
        citation_pdf = soup.find_all(attrs={"name": "citation_pdf_url"})
        assert len(citation_pdf) == 1
        citation_pdf = citation_pdf[0]['content']

        citation_pdf2 = soup.find_all(id='pdf')
        assert len(citation_pdf2) == 1
        citation_pdf2 = 'http://jmlr.org' + citation_pdf2[0]['href']

        assert citation_pdf2 == citation_pdf
