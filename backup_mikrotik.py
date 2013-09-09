#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
Script for Backup Mikrotik (backup-mikrotik.py)
Copyrighted by Fellipe Henrique <fellipeh at gmail.com>
License: GPLv2
 
Required python-paramiko
to install in  Debian, Ubuntu, OpenSUSE, CentOS
 
apt-get install python-paramiko
zypper install python-paramiko
yum install python-paramiko
 
 Como utilizar:
 - Primeiro você tem que criar um usuário no Mikrotik que tenha permissão de leitura.
 - python backup-mikrotik.py --ip ip_do_mikrotik --add-backup-user
 - Esse comando vai criar um usuário com o login backupuser e a sua Senha vai ser a senha do admin criptografada em md5
 - Apos efetuar o passo acima você já pode executar o comando de backup com o comando
 - python backup-mikrotik.py --ip ip_do_mikrotik --backup
 

 How to use:
 - First, create a read-write user in mikrotik
 - python backup-mikrotik.py --ip ip_do_mikrotik --add-backup-user
  These command will create a user backupuser and the password will be the admin password
- After that you can execute the command:
  python backup-mikrotik.py -ip IP_FOR_MIKROTIK --backup
"""
 
import os
import optparse
import gzip
import time
import hashlib
import paramiko
 
## Default config, se precisar mudar alguma coisa mude essas três linhas abaixo
## default config, if you need to change anything, change here..

backup_user  = 'backupuser'
admin_user   = 'admin'
default_pass = '123456789'
 
Mydata     = time.strftime("%Y%m%d_%H%M")
BackupDir  = '/usr/local/mikrotik/backup'
 
if not os.path.lexists(BackupDir):
    os.makedirs(BackupDir)
 
def BackupMikrotik(host, backup_user, passwd, port_ssh):
    MyFileName = ('rb_%s-%s.rsc') % (host, Mydata)
    MyPassUuid = hashlib.md5(passwd).hexdigest()
    # Create instance of the SSHClient class
    MyClient = paramiko.SSHClient()
 
    # Create instance of the AutoAddPolicy class
    addpolicy = paramiko.AutoAddPolicy()
 
    # Set the missing host key policy to "auto add", because we can't
    MyClient.set_missing_host_key_policy(addpolicy)
 
    # Connect to a remote host
    MyClient.connect(host, username=backup_user, password=MyPassUuid, port=port_ssh)
 
    print ('Backup RB IP: %s arquivo: %s/%s.gz') %(host, BackupDir, MyFileName)
    mystdin, mystdout, mystderr = MyClient.exec_command('export')
 
    #MyFileConf = open(MyFileName, 'wb')
    #MyFileConf.write(mystdout.read())
    #MyFileConf.close
 
    f = gzip.open(BackupDir + '/' + MyFileName + '.gz', 'wb')
    f.write(mystdout.read())
    f.close()
 
    #print mystdout.read()
 
    # Finally, close the ssh connection:
    MyClient.close()
 
def AddBackupUser(host, admin_user, backup_user, passwd, port_ssh):
 
    MyClient = paramiko.SSHClient()
    MyPassUuid = hashlib.md5(passwd).hexdigest()
 
    # Create instance of the AutoAddPolicy class
    addpolicy = paramiko.AutoAddPolicy()
    MyClient.set_missing_host_key_policy(addpolicy)
 
    # Connect to a remote host
    MyClient.connect(host, username=admin_user, password=passwd, port=port_ssh)
 
    print ('Criando o usuario de backup no Mikrotik Login: %s Senha: %s') % (backup_user, MyPassUuid)
    MyCommand = ('user add name=%s password=%s group=read; user print') % (backup_user, MyPassUuid)
    mystdin, mystdout, mystderr = MyClient.exec_command(MyCommand)
 
    print mystdout.read()
    MyClient.close()
 
def CleanFiles(BackupDir, DaysToKeep):
    now = time.time()
    for f in os.listdir(BackupDir):
        f = os.path.join(BackupDir, f)
        if os.stat(f).st_mtime < now - (DaysToKeep * 86400):
            if os.path.isfile(f):
                os.remove(f)
                print "APAGANDO O ARQUIVO ANTIGO COM MAIS DE %s DIAS" % DaysToKeep
                print f
 
def main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-i", "--ip", action="store", type="string", dest="ip", default='0.0.0.0', help="Entre com o IP da RB")
    parser.add_option("--port", action="store", type="int", dest="port", default='22', help="Porta Default SSH 22")
    parser.add_option("--backup-user", action="store", type="string", dest="backup_user", default=backup_user, help="Username backup Mikrotik")
    parser.add_option("--admin-user", action="store", type="string", dest="admin_user", default=admin_user, help="Username admin Mikrotik")
    parser.add_option("-p", "--passwd", action="store", type="string", dest="passwd", default=default_pass, help="Password Mikrotik")
    parser.add_option("-b", "--backup", action="store_true", dest="Backup", default=False, help="Para executar o Backup da RB")
    parser.add_option("-a", "--add-backup-user", action="store_true", dest="AddUser", default=False, help="Para adicionar o user de backup")
    options, args = parser.parse_args()
 
    if (options.ip) and (options.Backup):
        BackupMikrotik(options.ip, options.backup_user, options.passwd, options.port)
        CleanFiles(BackupDir, 30)
 
    if (options.ip) and (options.AddUser):
        AddBackupUser(options.ip, options.admin_user, options.backup_user, options.passwd, options.port)
 
if __name__ == "__main__":
    main()