import pexpect
import os

user = os.environ['JMLR_USER']
path = os.environ['JMLR_PATH']
passwd = os.environ['JMLR_PASSWORD']
origin = '.'

path = os.path.join(path, 'v2')
command = 'rsync -arvz %s %s@%s' % (origin, user, path)
print(command)

child = pexpect.spawn(command)
child.expect('Password:')
child.sendline(passwd)
child.interact()
