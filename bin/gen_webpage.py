import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


YEAR = datetime.today().year
# TODO detect if we are in the bin directory and go down one step

info = json.load(open('data/editorial-board.json', 'r'))

if not os.path.exists('output'):
    os.mkdir('output')

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

for page in ['editorial-board.html', 'contact.html']:
    with open('output/%s' % page, 'w') as f:
        template = env.get_template('templates/%s' % page)
        out = template.render(**info, year=YEAR)
        f.write(out)
    
