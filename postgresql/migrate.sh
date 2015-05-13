#!/bin/bash

# not a runnble script yet, more a bunch of cut-n-paste bash sentences ...

#################### postgresql setup
# tweak /etc/postgresql/9.3/main/pg_hba.conf
# being kind of old-school I'm more comfy with plain text password
# plus I like the idea that I can find the password again next time I need it
# so that authentication is done using plain text password
# (was md5 instead)
### host    all             all             127.0.0.1/32            password
### host    all             all             ::1/128                 password

cd /etc/postgresql/9.3/main

if [ ! -f pg_hba.conf.distrib ] ; then
    cp pg_hba.conf pg_hba.conf.distrib
    sed -e 's|^host\(.*\)md5|host\1password|' pg_hba.conf.distrib > pg_hba.conf
fi
    
# bootstrap the root user so we can use plain psql 
su postgres -c psql <<EOF
create role root superuser login;
\q
EOF

# create the omf_sfa user and prompt for password
# not sure this worked fine, I had to redo it manually later on
echo -n 'password for omf_sfa '; read password
psql -c "CREATE USER omf_sfa PASSWORD '$password'" template1

# create db
createdb --template=template0 --encoding=UNICODE --owner=root inventory

####################
cd /root/omf_sfa

service omf-sfa stop

# edit config file
#   database: postgres://omf_sfa:<password>@localhost/inventory
echo emacs etc/omf-sfa/omf-sfa-am.yaml - type enter when ready
read _

# tweak the gemspec file
if [ ! -f omf_sfa.gemspec.distrib ] ; then
    cp omf_sfa.gemspec omf_sfa.gemspec.distrib
    sed -e 's|s.add_runtime_dependency "sqlite3", "~> 1.3.10"|s.add_runtime_dependency "pg", "~> 0.18.1"|' omf_sfa.gemspec.distrib > omf_sfa.gemspec
fi

apt-get install -y postgresql-server-dev-9.3

bundle update
bundle install

rake db:migrate

echo to run the service manually, do
echo bundle exec ruby -I lib/ lib/omf-sfa/am/am_server.rb start

echo "also make sure to check your upstart script in /etc/init/omf-sfa.comf"

