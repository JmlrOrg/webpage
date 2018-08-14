import pexpect
import os

user = os.environ['JMLR_USER']
path = os.environ['JMLR_PATH']
passwd = os.environ['JMLR_PASSWORD']
origin = '.'

path = os.path.join(path, 'v2')
command = 'rsync -arvz output/%s %s@%s' % (origin, user, path)

ssh_newkey = 'Are you sure you want to continue connecting'
child = pexpect.spawn(command)
i = child.expect([ssh_newkey,'Password:',pexpect.EOF])
if i==0:
    child.sendline('yes')
    i = child.expect([ssh_newkey,'Password:',pexpect.EOF])
if i==1:
    child.sendline(passwd)
child.interact()
