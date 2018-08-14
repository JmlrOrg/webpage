import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


YEAR = datetime.today().year
# TODO detect if we are in the bin directory and go down one step

editorial_board = json.load(open('editorial-board.json', 'r'))

if not os.path.exists('output'):
    os.mkdir('output')

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

with open('output/editorial-board.html', 'w') as f:
    editorial_board_template = env.get_template('editorial-board.html')
    out = editorial_board_template.render(
        editors_in_chief=editorial_board['editors_in_chief'],
        managing_editors=editorial_board['managing_editors'],
        title='JMLR editorial board',
        year=YEAR
        )
    f.write(out)
print(out)
