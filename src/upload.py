import pexpect
import os

user = os.environ['JMLR_USER']
path = os.environ['JMLR_PATH']
passwd = os.environ['JMLR_PASSWORD']

path = os.path.join(path, '')
command = 'rsync -arvz output/beta/ %s@%s' % (user, os.path.join(path, 'beta')) # only the beta webpage
# command = 'rsync -arvz output/ %s@%s' % (user, path)

ssh_newkey = 'Are you sure you want to continue connecting'
child = pexpect.spawn(command)
i = child.expect([ssh_newkey,'Password:',pexpect.EOF])
if i==0:
    child.sendline('yes')
    i = child.expect([ssh_newkey,'Password:',pexpect.EOF])
if i==1:
    child.sendline(passwd)
child.interact()
