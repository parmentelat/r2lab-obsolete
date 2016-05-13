#!/bin/bash

DIRNAME=$(dirname "$0")
#echo Loading $DIRNAME/nodes.sh  >&2-
source $DIRNAME/nodes.sh

realm="r2lab.fr"

####################
run_dir=/root/openair-cn/SCRIPTS
log_epc=$run_dir/run_epc.log
syslog_epc=$run_dir/run_epc.syslog
log_hss=$run_dir/run_hss.log
logs="$log_epc $syslog_epc $log_hss"
conf_dir=/root/openair-cn/BUILD/EPC/
config=epc.conf.in


doc-sep "oai commands" 

doc-fun places "List environment variables"
function places() {
    echo "run_dir=$run_dir"
    echo "conf_dir=$conf_dir"
    echo "config=$config"
    echo "logs=\"$logs\""
}


doc-fun base "\tThe script to install base software on top of a raw image" 
function base() {

    echo "========== Installing mysql-server - select apache2 and set password=linux"
    read _
    apt-get install -y mysql-server

    echo "========== Installing phpmyadmin - provide mysql-server password as linux and set password=admin"
    apt-get install -y phpmyadmin

    echo "========== Running git clone for openair-cn and r2lab"
    read _
    cd
    echo -n | \
	openssl s_client -showcerts -connect gitlab.eurecom.fr:443 2>/dev/null | \
	sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' >> \
	    /etc/ssl/certs/ca-certificates.crt
    git clone https://gitlab.eurecom.fr/oai/openair-cn.git
    # this is probably useless, but well
    git clone https://github.com/parmentelat/r2lab.git

    echo "========== Setting up cpufrequtils"
    apt-get install -y cpufrequtils
    echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
    update-rc.d ondemand disable
    /etc/init.d/cpufrequtils restart
    # this seems to be purely informative ?
    cd
    cpufreq-info > cpufreq.info

    echo "========== Done - save image in oai-gw-base"
}

doc-fun builds "\tBuilds hss and epc and installs dependencies" 
function builds() {
    
    gitup
    cd $run_dir
    echo "========== Building HSS"
    ./build_hss -i 2>&1 | tee build_hss.log
    echo "========== Building EPC"
    ./build_epc -i 2>&1 | tee build_epc-i.log
    ./build_epc -j 2>&1 | tee build_epc-j.log

    echo "========== Done - save image in oai-gw-builds"
}

doc-fun configure "tweaks local files, and runs build_hss and build_epc"
function configure() {

    gitup
    id=$(r2lab-id)
    fitid=fit$id

    echo "========== Turning on the data interface"
    ifup data
    echo "========== Refreshing the depmod index"
    depmod -a
    if grep -q $fitid /etc/hosts && grep -q hss /etc/hosts; then
	echo $fitid already in /etc/hosts
    else
	echo "========== Defining $fitid in /etc/hosts"
	echo "127.0.1.1 $fitid $fitid.${realm} hss hss.${realm}" >> /etc/hosts
    fi

    cd $conf_dir
    echo "========== Checking for backup file $config.distrib"
    [ -f $config.distrib ] || cp $config $config.distrib
    echo "========== Patching config file"
    sed -e s,xxx,$id,g <<EOF > epc-r2lab.sed
s,eth0:1 *,data,g
s,192.170.0.1/24,192.168.2.xxx/24,g
s,eth0:2 *,data,g
s,192.170.1.1/24,192.168.2.xxx/24,g
s,eth0,data,g
s,192.168.12.17/24,192.168.2.xxx/24,g
s,127.0.0.1:5656,${syslog_epc},g
s,TAC = "15",TAC = "1",g
s,192.168.106.12,138.96.0.10,g
s,192.168.12.100,138.96.0.11,g
EOF
    sed -f epc-r2lab.sed $config.distrib > $config

    echo "========== Rebuilding hss and epc configs"
    cd $run_dir
#    ./build_hss --clean --clean-certificates --local-mme --fqdn fit$fitid.${realm} 2>&1 | tee build_hss-run2.log
    ./build_hss --clean --clean-certificates --local-mme 2>&1 | tee build_hss-run2.log
    ./build_epc --clean --clean-certificates --local-hss 2>&1 | tee build_epc.run2.log

    populate-db
}

# not declared in available since it's called by configure
function populate-db() {
    # insert our SIM in the hss db
    # NOTE: setting the 'key' column raises a special issue as key is a keyword in
    # the mysql syntax
    # this will need to be fixed if it's important that we set a key

# sample from the doc    
# ('208930000000001',  '33638060010', NULL, NULL,
#  'PURGED', '120', '50000000', '100000000', 
#  '47', '0000000000', '3', 0x8BAF473F2F8FD09487CCCBD7097C6862,
#  '1', '0', '', 0x00000000000000000000000000000000, '');
###    insert_command="INSERT INTO users (imsi, msisdn, imei, imei_sv, 
###                                       ms_ps_status, rau_tau_timer, ue_ambr_ul, ue_ambr_dl,
###                                       access_restriction, mme_cap, mmeidentity_idmmeidentity, key,
###                                       RFSP-Index, urrp_mme, sqn, rand, OPc) VALUES ("
###    # imsi PRIMARY KEY
###    insert_command="$insert_command '222220000000001',"
###    # msisdn - unused but must be non-empty
###    insert_command="$insert_command '33638060010',"
###    # imei
###    insert_command="$insert_command NULL,"
###    # imei_sv
###    insert_command="$insert_command NULL,"
###    # ms_ps_status
###    insert_command="$insert_command 'PURGED',"
###    # rau_tau_timer
###    insert_command="$insert_command '120',"
###    # ue_ambr_ul upload ?
###    insert_command="$insert_command '50000000',"
###    # ue_ambr_dl download ?
###    insert_command="$insert_command '100000000',"
###    # access_restriction
###    insert_command="$insert_command '47',"
###    # mme_cap
###    insert_command="$insert_command '0000000000',"
###    # mmeidentity_idmmeidentity PRIMARY KEY
###    insert_command="$insert_command '3',"
###    # key
###    insert_command="$insert_command '0x8BAF473F2F8FD09487CCCBD7097C6862',"
###    # RFSP-Index
###    insert_command="$insert_command '1',"
###    # urrp_mme
###    insert_command="$insert_command '0',"
###    # sqn
###    insert_command="$insert_command '',"
###    # rand
###    insert_command="$insert_command '0x00000000000000000000000000000000',"
###    # OPc
###    insert_command="$insert_command '');"

    # from https://gitlab.eurecom.fr/oai/openairinterface5g/wikis/SIMInfo
    # SIM card # 2

    function name_value() {
	name="$1"; shift
	value="$1"; shift
	last="$1"; shift
	insert_command="$insert_command $value"
	update_command="$update_command $name=$value"
	if [ -n "$last" ]; then
	    insert_command="$insert_command)"
	else
	    insert_command="$insert_command",
	    update_command="$update_command",
	fi
    }

    idmmeidentity=100
    fdqn=fit$(r2lab-id).${realm}
	
    # users table
    insert_command="INSERT INTO users (imsi, msisdn, access_restriction, mmeidentity_idmmeidentity, \`key\`, sqn) VALUES ("
    update_command="ON DUPLICATE KEY UPDATE "
    name_value imsi "'208950000000002'"
    name_value msisdn "'33638060010'"
    name_value access_restriction "'47'"
    name_value mmeidentity_idmmeidentity "'${idmmeidentity}'"
    name_value "\`key\`" "0x8BAF473F2F8FD09487CCCBD7097C6862"
    name_value sqn "'000000000020'" last

#    mysql --user=root --password=linux -e 'select imsi from users where imsi like "20895%"' oai_db 

    echo issuing SQL "$insert_command $update_command"
    mysql --user=root --password=linux -e "$insert_command $update_command" oai_db


    # mmeidentity table
    insert_command="INSERT INTO mmeidentity (idmmeidentity, mmehost, mmerealm) VALUES ("
    update_command="ON DUPLICATE KEY UPDATE "

    name_value idmmeidentity ${idmmeidentity}
    name_value mmehost "'${fdqn}'"
    name_value mmerealm "'${realm}'" last
    
    echo issuing SQL "$insert_command $update_command"
    mysql --user=root --password=linux -e "$insert_command $update_command" oai_db
    
}

doc-fun start "\tStarts hss + epc"
function start() {
    echo Turning on interface $(data-up)
    cd $run_dir
    # echo "In $(pwd)"
    echo "Running run_epc in background"
    # --gdb is a possible additional option here
    ./run_epc --set-nw-interfaces --remove-gtpu-kmodule >& $log_epc &
    echo "Running run_hss in background"
    ./run_hss >& $log_hss &
}

locks="/var/run/mme_gw.pid /var/run/oai_hss.pid"

function _manage() {
    # if $1 is 'stop' then the found processes are killed
    mode=$1; shift
    pids="$(pgrep run_) $(pgrep mme_gw) $(pgrep oai_hss)"
    pids="$(echo $pids)"

    if [ -z "$pids" ]; then
	echo "No running process - exiting"
	return 1
    fi
    echo "========== Found processes"
    ps $pids
    if [ "$mode" == 'stop' ]; then
	echo "========== Killing $pids"
	kill $pids
	echo "========== Their status now"
	ps $pids
	echo "========== Clearing locks"
	echo "$locks"
	rm -f $locks
    fi
}

doc-fun status "\tDisplays the status of the epc and hss processes"
function status() { _manage; }
doc-fun stop "\tStops the epc and hss processes & clears locks"
function stop() { _manage stop; }


doc-fun manage-db "Runs mysql on the oai_db database" 
function manage-db() {
    mysql --user=root --password=linux oai_db
}
####################
define_main

########################################
main "$@"
