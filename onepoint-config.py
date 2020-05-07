import os
import json
import sys
import time
import wget
import mysql.connector as mysql

def Default():
	print("Iniciando configuracao Padrao")
	cmd = "yum install -y https://rpms.remirepo.net/enterprise/remi-release-7.rpm -q | pv -L 1m"
	os.system("systemctl disable firewalld && systemctl stop firewalld")
	os.system(cmd)
	print("Verificando Diretorios Padrao")
	DefaultDir = ["/mnt/onepoint", "/opt/vault", "/opt/vault/data", "/opt/vault/log", "/opt/vault/bin", "/etc/vault"]
	for Dir in DefaultDir:
		#print(Dir)
		d = os.path.isdir(Dir)
		if d:
			print("Diretorio ja existe " + Dir) 
			pass
		else:
			print("Criando diretorio " + Dir)
			cmd = "mkdir %s" %Dir
			os.system(cmd)

	print("Iniciando instalacao Dependencias Padrao Onepoint")
	phpDep = ["php72-php","php72-php-common","php72-php-bz2","php72-php-curl","php72-php-ldap","php72-php-gd","php72-php-gmp","php72-php-imap","php72-php-mbstring","php72-php-mcrypt","php72-php-soap","php72-php-mysqlnd","php72-php-xml","php72-php-zip","php72-php-json"]
	for php in phpDep:
		checkDep = os.system("rpm -qa | grep " + php)
		print("Iniciando instalacao Dependencia " + php)
		phpinst = "yum install -y " + php + " -q | pv -L 1m"
		os.system(phpinst)
	epel = "yum install -y epel-release  -q | pv -L 1m"
	print("Iniciando instalacao Servidor Apache")
	webDB = ["httpd", "mariadb", "mariadb-server"]
	for dep in webDB:
		print("Iniciando instalacao das dependencias --> "  + dep)
		insDEP = "yum install -y " + dep + "  -q | pv -L 1m"
		os.system(insDEP)
		os.system("systemctl enable " + dep)
		os.system("systemctl start " + dep)
	os.system("yum install -y curl http://download-ib01.fedoraproject.org/pub/epel/6/x86_64/Packages/c/curlpp-0.7.3-5.el6.x86_64.rpm  -q | pv -L 1m")

	depPython = ["python-pip","python-requests","python-ldap","python-paramiko","libssh","json-c","jsoncpp"]
	for depP in depPython:
		print("Instalando outros pre-requisitos -->" + depP)
		cmd = os.system("yum install -y " + depP + " -q | pv -L 1m")
	MariaDB()
def VaultH():
	print("Iniciando instalacao Hashicorp Vault")
	print("Verificando pre-requisitos Vault")
	DefaultDir = ["/opt/vault", "/opt/vault/data", "/opt/vault/log", "/opt/vault/bin"]
	for Dir in DefaultDir:
		d = os.path.isdir(Dir)
		if d:
			print("Diretorio ja existe " + Dir)
			pass
		else:
			print("Criando diretorio " + Dir)
			cmd = "mkdir %s" %Dir
			os.system(cmd)
	fileVault = os.path.isfile("/mnt/onepoint/onepoint-install/vault_1.4.1_linux_amd64.zip")
	cmd = os.system("unzip vault_1.4.1_linux_amd64.zip")

	print(fileVault)
	#downloadVault = wget.download(urlVault)
	if fileVault:
		print("Arquivo Vault ja existe")
		cmd = os.system("unzip vault_1.4.1_linux_amd64.zip")
		fileVault = os.path.isfile("/mnt/onepoint/onepoint-install/vault")
		if fileVault:
			print("Vault descompactado com sucesso")
			vaultBin = os.path.isfile("/opt/vault/bin/vault")
			if vaultBin:
				pass
			else:
				print("Configuranco Vault Bin")
				vaultcp = os.system("cp -rf /mnt/onepoint/onepoint-install/vault /opt/vault/bin")
		else:
			print("Descompactando Vault")
			cmd = os.system("unzip vault_1.4.1_linux_amd64.zip")
			print("Configuranco Vault Bin")
			vaultcp = os.system("cp -rf /mnt/onepoint/onepoint-install/vault /opt/vault/bin")

	else:
		print("Realizando download do Vault")
		urlVault = "https://releases.hashicorp.com/vault/1.4.1/vault_1.4.1_linux_amd64.zip"
		fileVault = wget.download(urlVault)
		cmd = os.system("unzip vault_1.4.1_linux_amd64.zip")

	VaultConfig()
def VaultConfig():

	print("Iniciando configuracao Vault as a Service")
	dirVault = "/etc/vault"
	fileVault = ("/etc/vault/config.json")
	d = os.path.isdir(dirVault)
	f = os.path.isfile(fileVault)
	if d:
		
		confgText = open("/etc/vault/config.json", "w")
		print("Teste")
		confgText.write('ui = true\nstorage "file" {\npath = "/opt/vault/data"\n}\nlistener "tcp" {\naddress	= "0.0.0.0:8200"\ntls_disable = 1\n}\n')
		confgText.close()
		print("Arquivo de configuracao Vault criado com sucesso")
		print("Criando conta vault")
		acVault = os.system("useradd -r vault")
		print("Atribuindo permissao a conta vault - Diretorio de instalacao")
		acPermission = os.system("chown -Rv vault:vault /opt/vault")
		print("Executando Vault como Servico")
		acService = os.system("cp -rf vault.service /etc/systemd/system/")
		acServiceF = os.path.isfile("/etc/systemd/system/vault.service")
		if acServiceF:
			print("Iniciando Servico Vault")
			startService = os.system("systemctl enable vault.service && systemctl start vault.service")
			statusService = os.system("systemctl status vault")
		
	else:
               	os.system("mv config.json /etc/vault/config.json")
                print("Arquivo de configuracao Vault criado com sucesso")
	InstallOnepoint()
def MariaDB():
        print("Iniciando servico MariaDB")
	cmd = "systemctl start mariadb && systemctl enable mariadb"
	print("Iniciando servico MariaDB")
	os.system(cmd)
	db = mysql.connect(
 			host = "localhost",
    			user = "root"

			)
	cursor = db.cursor()
	cursor.execute("SHOW DATABASES like 'onepoint'") 
	onepointdb = cursor.fetchall() 
	if onepointdb:
		print("Database Onepoint existe")
		pass
	else:
		print("Criando database Onepoint")
		cursor.execute("create database onepoint")
	VaultH()
def InstallOnepoint():
	print("Instalando repositorio Onepoint")
	cmd = os.system("yum install -y http://repo.onepoint.net.br/yum/centos/repo/onepoint-repo-0.1-1centos.noarch.rpm  -q | pv -L 1m")
	if cmd:
		print("Instalando Onepoint")
		cmd = os.system("yum install -y onepoint")
		if cmd:
			print("Onepoint Instalado com sucesso")
			
		else:
			print("Por favor avaliar os logs de erro")
	VaultConfigFinal()

def VaultConfigFinal():
	arq="vault-init"
	exp = os.system("export VAULT_ADDR=http://127.0.0.1:8200")
	print("Iniciando processo de configuracao do Vault")
	print("Iniciando processo de Unseal")
	os.system("/opt/vault/bin/vault operator init >> " + arq)
	print(os.system("cat " + arq))
	cmd = os.system("cat vault-init | grep Unseal | awk -F ' ' '{print $4}' >> initv")
	with open('initv','r') as f:
		for line in f.readlines()[0:3]:
			print("Processo Unseal Iniciado " + line)
			os.system("/opt/vault/bin/vault operator unseal " + line)
	print("Processo de Unseal Concluido com sucesso")
	print("Iniciando Processo - Login")
	rooToken = os.system("cat vault-init | grep Root | awk -F ' ' '{print $4}' >> root-login")
	with open('root-login','r') as f:
		for line in f.readlines():
			print("Line " + line)
			os.system("/opt/vault/bin/vault login " + line)
	print("Iniciando processo de Criacao Vault")
	cmdArgs = ["vault secrets enable -version=2 -path=secret kv","vault secrets enable -path=secret kv","vault policy write secret-full policy.hcl","vault auth enable approle","vault write auth/approle/role/secret-role token_ttl=20m token_max_ttl=30m policies='default,secret-full'"]
	for cmd in cmdArgs:
		os.system("/opt/vault/bin/" + cmd)
	cmdID = ["vault read auth/approle/role/secret-role/role-id","vault write -f auth/approle/role/secret-role/secret-id"]
	for cmd in cmdID:
		os.system("/opt/vault/bin/" + cmd + " >> secret-role-id")
		print("Arquivo gerado com sucesso")



if __name__ == "__main__":
	Default()
	#VaultH()
#	MariaDB()
#	VaultConfigFinal()
