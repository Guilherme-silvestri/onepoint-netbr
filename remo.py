import os
phpDep = ["php72-php","php72-php-common","php72-php-bz2","php72-php-curl","php72-php-ldap","php72-php-gd","php72-php-gmp","php72-php-imap","php72-php-mbstring","php72-php-mcrypt","php72-php-soap"]
for a in phpDep:
	os.system("yum remove -y " + a)

