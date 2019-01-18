"""
Utility to normalize filenames
"""
import glob, os
import shutil
os.chdir('.')
paths = glob.glob('*/')

upload_file = ''

for p in paths:
    id = p.strip('/')
    upload_file += p.strip('/') + '\n'
    os.chdir(p)
    if not os.path.exists('source'):
        # if instead there is a single directory with a different name
        # then the sources are probably inside it. Just rename
        filenames = os.listdir('.')
        print(filenames)
        if len(filenames) == 1:
            os.rename(filenames[0], 'source')
        else:
            files_in_source = glob.glob('*')
            os.mkdir('source')
            for fs in files_in_source:
                shutil.move(fs, os.path.join('source', fs))
    if not os.path.exists(os.path.join('source', id + '.tex')):
        raise ValueError('source directory does not contain %s.tex file' % id)
    os.chdir('..')
print(upload_file)
for pdf_file in glob.glob('*.pdf'):
    dir, _ = pdf_file.split('.')
    shutil.move(pdf_file, dir + '/')
