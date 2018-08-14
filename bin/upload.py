import pexpect
import os

user = os.environ['JMLR_USER']
path = os.environ['JMLR_PATH']
passwd = os.environ['JMLR_PASSWORD']
origin = '.'

path = os.path.join(path, 'v2')
command = 'rsync -arvz %s %s@%s' % (origin, user, path)
print(command)

ssh_newkey = 'Are you sure you want to continue connecting'
child = pexpect.spawn(command)
i = p.expect([ssh_newkey,'password:',pexpect.EOF])
if i==0:
    print('I say yes')
    p.sendline('yes')
    i = p.expect([ssh_newkey,'password:',pexpect.EOF])
if i==1:
    child.sendline(passwd)
child.interact()
