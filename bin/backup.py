import pexpect
import os

user = os.environ['JMLR_USER']
path = os.environ['JMLR_PATH']
passwd = os.environ['JMLR_PASSWORD']
backup_dir = os.environ['JMLR_BACKUP_DIR']

path = os.path.join(path, '')
command = 'rsync -arvz %s@%s %s' % (user, path, backup_dir)
print('Running command')
print(command)

ssh_newkey = 'Are you sure you want to continue connecting'
child = pexpect.spawn(command)
i = child.expect([ssh_newkey,'Password:',pexpect.EOF])
if i==0:
    child.sendline('yes')
    i = child.expect([ssh_newkey,'Password:',pexpect.EOF])
if i==1:
    child.sendline(passwd)
child.interact()
