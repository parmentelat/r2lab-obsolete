#!/bin/bash

DIRNAME=$(dirname "$0")
#echo Loading $DIRNAME/nodes.sh  >&2-
source $DIRNAME/nodes.sh

doc-sep "oai subcommands; run e.g. oai start"

source $DIRNAME/oai-common.sh

COMMAND=$(basename "$0")
case $COMMAND in
    oai-gw*)
	runs_epc=true; runs_hss=true ;;
    oai-hss*)
	runs_epc=;     runs_hss=true ;;
    oai-epc*)
	runs_epc=true; runs_hss=     ;;
esac
    

####################
run_dir=/root/openair-cn/SCRIPTS
[ -n "$runs_epc" ] && log_epc=$run_dir/run_epc.log
[ -n "$runs_epc" ] && syslog_epc=$run_dir/run_epc.syslog
[ -n "$runs_hss" ] && log_hss=$run_dir/run_hss.log
logs="$log_epc $syslog_epc $log_hss"
conf_dir=/root/openair-cn/BUILD/EPC/
[ -n "$runs_epc" ] && config=epc.conf.in


doc-fun dumpvars "list environment variables"
function dumpvars() {
    echo "oai_role=${oai_role}"
    echo "oai_ifname=${oai_ifname}"
    echo "oai_subnet=${oai_subnet}"
    echo "runs_hss=$runs_hss"
    echo "runs_epc=$runs_epc"
    echo "run_dir=$run_dir"
    echo "conf_dir=$conf_dir"
    echo "config=$config"
    echo "logs=\"$logs\""
}


doc-fun base "the script to install base software on top of a raw image" 
function base() {

    echo "========== Installing mysql-server - select apache2 and set password=linux - press enter .."
    read _
    apt-get install -y mysql-server

    echo "========== Installing phpmyadmin - provide mysql-server password as linux and set password=admin"
    echo "Press enter .."
    read _
    apt-get install -y phpmyadmin

    echo "========== Running git clone for openair-cn and r2lab - press enter .."
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

doc-fun builds "builds hss and epc and installs dependencies" 
function builds() {
    
    gitup
    cd $run_dir
    echo "========== Building HSS"
    [ -n "$runs_hss" ] && ./build_hss -i 2>&1 | tee build_hss.build.log
    echo "========== Building EPC"
    [ -n "$runs_epc" ] && ./build_epc -i 2>&1 | tee build_epc-i.build.log
    # this was not actually run in oai-gw-builds2
    # it looks like it won't run fine at that early stage
    # that's why it is done in 'init' instead
    # and I even suspect it works fine only after configure in fact...
    # [ -n "$runs_epc" ] && ./build_epc -j -f 2>&1 | tee build_epc-j.build.log

    echo "========== Done - save image in oai-gw-builds"
}

function clean-hosts() {
    sed --in-place '/fit/d' /etc/hosts
    sed --in-place '/hss/d' /etc/hosts
}

doc-fun check-etc-hosts "adjusts /etc/hosts; run with hss as first arg to define hss"
function check-etc-hosts() {
    clean-hosts

    id=$(r2lab-id)
    fitid=fit$id
    
    if [ -n "$runs_hss" -a -n "$runs_epc" ]; then
	# box runs both services
	echo "127.0.1.1 $fitid $fitid.${oai_realm} hss hss.${oai_realm}" >> /etc/hosts
    elif [ -n "$runs_hss" ]; then
	# HSS only
	echo "127.0.1.1 $fitid $fitid.${oai_realm}" >> /etc/hosts
	echo "192.168.${oai_subnet}.${id} hss hss.${oai_realm}" >> /etc/hosts
    else
	# EPC only : need to know where the hss server is running
	hss_id=$(get-peer)
	[ -z "$hss_id" ] && { echo "ERROR: no peer defined"; return; }
	echo "Using hss $gw_id"
	echo "127.0.1.1 $fitid $fitid.${oai_realm}" >> /etc/hosts
	echo "192.168.${oai_subnet}.${hss_id} hss hss.${oai_realm}" >> /etc/hosts
    fi
}
	
    
doc-fun init "sync clock from NTP, checks /etc/hosts, rebuilds gtpu and runs depmod"
function init() {

    echo "========== Sync clock at NTP"
    init-clock
    echo "========== Checking /etc/hosts"
    check-etc-hosts
    echo "========== Rebuilding the GTPU module"
    cd $run_dir
    ./build_epc -j -f
    echo "========== Refreshing the depmod index"
    depmod -a
    
}

doc-fun configure "configure hss and/or epc"
function configure() {
    configure-hss
    configure-epc
}

doc-fun configure-epc "configures epc"
function configure-epc() {

    [ -n "$runs_epc" ] || { echo not running epc - skipping ; return; }

    id=$(r2lab-id)
    fitid=fit$id

    cd $conf_dir
    echo "========== Checking for backup file $config.distrib"
    [ -f $config.distrib ] || cp $config $config.distrib
    echo "========== Patching config file"
    sed -e s,xxx,$id,g <<EOF > epc-r2lab.sed
s,eth0:1 *,${oai_ifname},g
s,192.170.0.1/24,192.168.${oai_subnet}.xxx/24,g
s,eth0:2 *,${oai_ifname},g
s,192.170.1.1/24,192.168.${oai_subnet}.xxx/24,g
s,eth0,${oai_ifname},g
s,192.168.12.17/24,192.168.${oai_subnet}.xxx/24,g
s,127.0.0.1:5656,${syslog_epc},g
s,TAC = "15",TAC = "1",g
s,192.188.2.0/24,192.168.10.0/24,g
s,192.188.8.0/24,192.168.11.0/24,g
s,192.168.106.12,138.96.0.10,g
s,192.168.12.100,138.96.0.11,g
EOF
    sed -f epc-r2lab.sed $config.distrib > $config

    echo "========== Reconfiguring epc"
    cd $run_dir
    if [ -n "$runs_hss" ]; then
	# both services are local
	./build_epc --clean --clean-certificates --local-hss --realm ${oai_realm} 2>&1 | tee build_epc.conf.log
    else
	./build_epc --clean --clean-certificates --remote-hss hss.${oai_realm} --realm ${oai_realm} 2>&1 | tee build_epc.conf.log
    fi
}

doc-fun configure-hss "configures hss"
function configure-hss() {

    [ -n "$runs_hss" ] || { echo not running hss - skipping ; return; }

    fitid=fit$(r2lab-id)

    echo "========== Reconfiguring hss"
    cd $run_dir
    if [ -n "$runs_epc" ]; then
	# both services are local
	./build_hss --clean --clean-certificates --fqdn hss.${oai_realm} --install-hss-files --local-mme 2>&1 | tee build_hss.conf.log
    else
	# xxx todo
	./build_hss --clean --clean-certificates --fqdn hss.${oai_realm} --install-hss-files 2>&1 | tee build_hss.conf.log
    fi
	
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
    # this runs in the hss box
    if [ -n "$runs_epc" ] ; then
	mmehost=fit$(r2lab-id).${oai_realm}
    else
	epc_id=$(get-peer)
	mmehost=fit${epc_id}.${oai_realm}
    fi	

###    
###    # users table
###    insert_command="INSERT INTO users (imsi, msisdn, access_restriction, mmeidentity_idmmeidentity, \`key\`, sqn) VALUES ("
###    update_command="ON DUPLICATE KEY UPDATE "
###    name_value imsi "'208950000000002'"
###    name_value msisdn "'33638060010'"
###    name_value access_restriction "'47'"
###    name_value mmeidentity_idmmeidentity "'${idmmeidentity}'"
###    name_value "\`key\`" "0x8BAF473F2F8FD09487CCCBD7097C6862"
###    name_value sqn "'000000000020'" last
###
####    mysql --user=root --password=linux -e 'select imsi from users where imsi like "20895%"' oai_db 
###
###    echo issuing SQL "$insert_command $update_command"
###    mysql --user=root --password=linux -e "$insert_command $update_command" oai_db

    hack_command="update users set mmeidentity_idmmeidentity=100 where imsi=208950000000002;"
    echo issuing HACK SQL "$hack_command"
    mysql --user=root --password=linux -e "$hack_command" oai_db

    # mmeidentity table
    insert_command="INSERT INTO mmeidentity (idmmeidentity, mmehost, mmerealm) VALUES ("
    update_command="ON DUPLICATE KEY UPDATE "

    name_value idmmeidentity ${idmmeidentity}
    name_value mmehost "'${mmehost}'"
    name_value mmerealm "'${oai_realm}'" last
    
    echo issuing SQL "$insert_command $update_command"
    mysql --user=root --password=linux -e "$insert_command $update_command" oai_db
    
}

doc-fun start "starts the hss and/or epc service(s)"
function start() {
    [ "$oai_ifname" == data ] && echo Checking interface is up : $(data-up)
    cd $run_dir
    if [ -n "$runs_hss" ]; then
	echo "Running run_hss in background"
	./run_hss >& $log_hss &
    fi
    if [ -n "$runs_epc" ]; then
	echo "Running run_epc in background"
	# --gdb is a possible additional option here
	./run_epc --set-nw-interfaces --remove-gtpu-kmodule >& $log_epc &
    fi
}

locks=""
[ -n "$runs_hss" ] && locks="$locks /var/run/oai_hss.pid"
[ -n "$runs_epc" ] && locks="$locks /var/run/mme_gw.pid"

function _manage() {
    # if $1 is 'stop' then the found processes are killed
    mode=$1; shift
    pids=""
    [ -n "$runs_hss" ] && pids="$pids $(pgrep run_hss) $(pgrep oai_hss)"
    [ -n "$runs_epc" ] && pids="$pids $(pgrep run_epc) $(pgrep mme_gw)"
    pids="$(echo $pids)"

    if [ -z "$pids" ]; then
	echo "No running process"
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

doc-fun status "displays the status of the epc and/or hss processes"
function status() { _manage; }
doc-fun stop "stops the epc and/or hss processes & clears locks"
function stop() { _manage stop; }


doc-fun manage-db "runs mysql on the oai_db database" 
function manage-db() {
    mysql --user=root --password=linux oai_db
}

####################
define_main

########################################
main "$@"
