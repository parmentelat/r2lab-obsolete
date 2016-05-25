#!/bin/bash

DIRNAME=$(dirname "$0")
#echo Loading $DIRNAME/nodes.sh  >&2-
source $DIRNAME/nodes.sh

doc-sep "#################### subcommands to the oai command (alias o)"

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
# support for two config mechanisms.. sigh..
[ "${oai_cn_branch}" == master ] && new_config_mode="" || new_config_mode=true

run_dir=/root/openair-cn/SCRIPTS
[ -n "$runs_hss" ] && { log_hss=$run_dir/run_hss.log; add-to-logs $log_hss; }
[ -n "$runs_epc" ] && {
    if [ -z "$new_config_mode" ]; then
	log_epc=$run_dir/run_epc.log
	syslog_epc=$run_dir/run_epc.syslog
	add-to-logs $log_epc $syslog_epc
	conf_dir=/root/openair-cn/BUILD/EPC/
	config=epc.conf.in
	add-to-configs $conf_dir/$config
    else
	log_mme=$run_dir/mme.log; add-to-logs $log_mme
	out_mme=$run_dir/mme.out; add-to-logs $out_mme
	log_spgw=$run_dir/spgw.log; add-to-logs $log_spgw
	out_spgw=$run_dir/spgw.out; add-to-logs $out_spgw
	template_dir=/root/openair-cn/ETC/
	conf_dir=/usr/local/etc/oai
	add-to-configs $conf_dir/mme.conf
	add-to-configs $conf_dir/freeDiameter/mme_fd.conf
	add-to-configs $conf_dir/spgw.conf
    fi
}

doc-fun dumpvars "list environment variables"
function dumpvars() {
    echo "oai_role=${oai_role}"
    echo "oai_ifname=${oai_ifname}"
    echo "oai_subnet=${oai_subnet}"
    echo "runs_hss=$runs_hss"
    echo "runs_epc=$runs_epc"
    echo "run_dir=$run_dir"
    echo "conf_dir=$conf_dir"
    echo "configs=$(get-configs)"
    echo "logs=$(get-logs)"
    echo "datas=$(get-datas)"
    echo "new_config_mode=$new_config_mode"
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
    [ -n "$runs_hss" ] && ./build_hss -i 2>&1 | tee build-hss.build.log
    echo "========== Building EPC"
    if [ -n "$runs_epc" ]; then
	if [ -z "$new_config_mode" ]; then
	    ./build_epc -i 2>&1 | tee build-epc-i.log
	else
	    ./build_mme -i 2>&1 | tee build-spgw-i.log
	    ./build_spgw -i 2>&1 | tee build-spgw-i.log
	fi
    fi
    # building the kernel module : deferred to the init step
    # it looks like it won't run fine at that early stage
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
    echo "========== Checking out the ${oai_cn_branch} branch in openair-cn"
    cd ~/openair-cn
    cn-branch ${oai_cn_branch}
    echo "========== Rebuilding the GTPU module"
    cd $run_dir
    if [ -z "$new_config_mode" ]; then
	./build_epc -j -f 2>&1 | tee build-epc-j.log
    else
	./build_spgw -j -f 2>&1 | tee build-spgw-j.log
    fi
    echo "========== Refreshing the depmod index"
    depmod -a
    
}

doc-fun cn-branch "select branch in openair-cn; typically master or unstable"
function cn-branch() {
    branch=$1; shift
    cd /root/openair-cn
    git reset --hard HEAD
    git checkout --force $branch
    cd -
}

doc-fun configure "configure hss and/or epc"
function configure() {
    configure-hss
    configure-epc
}

doc-fun configure-epc "configures epc"
function configure-epc() {

    [ -n "$runs_epc" ] || { echo not running epc - skipping ; return; }

    if [ -z "$new_config_mode" ]; then
	echo EPC config OLD STYLE
	-configure-epc-old-style
    else
	echo EPC config NEW STYLE
	-configure-epc-new-style
    fi
}

####################
function -configure-epc-old-style() {
    id=$(r2lab-id)
    fitid=fit$id

    cd $conf_dir
    echo "========== Checking for backup file $config.distrib"
    [ -f $config.distrib ] || cp $config $config.distrib
    echo "========== Patching config file"
    cat > epc-r2lab.sed <<EOF 
s,eth0:1 *,${oai_ifname},g
s,192.170.0.1/24,192.168.${oai_subnet}.${id}/24,g
s,eth0:2 *,${oai_ifname},g
s,192.170.1.1/24,192.168.${oai_subnet}.${id}/24,g
s,eth0,${oai_ifname},g
s,192.168.12.17/24,192.168.${oai_subnet}.${id}/24,g
s,127.0.0.1:5656,${syslog_epc},g
s,TAC = "15",TAC = "1",g
s,192.188.2.0/24,192.168.100.0/24,g
s,192.188.8.0/24,192.168.101.0/24,g
s,192.168.106.12,138.96.0.10,g
s,192.168.12.100,138.96.0.11,g
EOF
    sed -f epc-r2lab.sed $config.distrib > $config

    echo "========== Rebuilding epc"
    cd $run_dir
    if [ -n "$runs_hss" ]; then
	# both services are local
	./build_epc --clean --clean-certificates --local-hss --realm ${oai_realm} 2>&1 | tee build-epc-conf.log
    else
	# MME only
	./build_epc --clean --clean-certificates --remote-hss hss.${oai_realm} --realm ${oai_realm} 2>&1 | tee build-epc-conf.log
    fi
}

####################
function -configure-epc-new-style() {
    mkdir -p /usr/local/etc/oai/freeDiameter
    local id=$(r2lab-id)
    local fitid=fit$id
    local localip="192.168.${oai_subnet}.${id}/24"

    cd $template_dir
    cat > mme-r2lab.sed <<EOF
s|RUN_MODE.*=.*|RUN_MODE = "OTHER";|
s|REALM.*=.*|REALM = "${oai_realm}";|
s|.*YOUR GUMMEI CONFIG HERE|{MCC="208" ; MNC="95"; MME_GID="4" ; MME_CODE="1"; }|
s|{MCC="208" ; MNC="93";  TAC = "15"; }.*|{MCC="208" ; MNC="95";  TAC = "1"; },|
s|MME_INTERFACE_NAME_FOR_S1_MME.*=.*|MME_INTERFACE_NAME_FOR_S1_MME = "${oai_ifname}";|
s|MME_IPV4_ADDRESS_FOR_S1_MME.*=.*|MME_IPV4_ADDRESS_FOR_S1_MME = "${localip}";|
s|MME_INTERFACE_NAME_FOR_S11_MME.*=.*|MME_INTERFACE_NAME_FOR_S11_MME = "${oai_ifname}";|
s|MME_IPV4_ADDRESS_FOR_S11_MME.*=.*|MME_IPV4_ADDRESS_FOR_S11_MME = "${localip}";|
s|SGW_IPV4_ADDRESS_FOR_S11.*=.*|SGW_IPV4_ADDRESS_FOR_S11 = "${localip}";|
s|"CONSOLE"|"${out_mme}"|
EOF
    echo "(Over)writing $conf_dir/mme.conf"
    sed -f mme-r2lab.sed < mme.conf > $conf_dir/mme.conf

    cat > mme_fd-r2lab.sed <<EOF
s|Identity.*=.*|Identity="${fitid}.${oai_realm}";|
s|Realm.*=.*|Realm="${oai_realm}";|
EOF
    echo "(Over)writing $conf_dir/freeDiameter/mme_fd.conf"
    sed -f mme_fd-r2lab.sed < mme_fd.conf > $conf_dir/freeDiameter/mme_fd.conf
    
    cat > spgw-r2lab.sed <<EOF
s|SGW_INTERFACE_NAME_FOR_S11.*=.*|SGW_INTERFACE_NAME_FOR_S11 = "${oai_ifname}";|
s|SGW_IPV4_ADDRESS_FOR_S11.*=.*|SGW_IPV4_ADDRESS_FOR_S11 = "${localip}";|
s|SGW_INTERFACE_NAME_FOR_S1U_S12_S4_UP.*=.*|SGW_INTERFACE_NAME_FOR_S1U_S12_S4_UP = "${oai_ifname}";|
s|SGW_IPV4_ADDRESS_FOR_S1U_S12_S4_UP.*=.*|SGW_IPV4_ADDRESS_FOR_S1U_S12_S4_UP = "${localip}";|
s|OUTPUT.*=.*|OUTPUT = "${out_spgw}";|
s|PGW_INTERFACE_NAME_FOR_SGI.*=.*|PGW_INTERFACE_NAME_FOR_SGI = "${oai_ifname}";|
s|PGW_IPV4_ADDRESS_FOR_SGI.*=.*|PGW_IPV4_ADDRESS_FOR_SGI = "${localip}";|
s|DEFAULT_DNS_IPV4_ADDRESS.*=.*|DEFAULT_DNS_IPV4_ADDRESS = "138.96.0.10";|
s|DEFAULT_DNS_SEC_IPV4_ADDRESS.*=.*|DEFAULT_DNS_SEC_IPV4_ADDRESS = "138.96.0.11";|
s|192.188.2.0/24|192.168.10.0/24|g
s|192.188.8.0/24|192.168.11.0/24|g
EOF
    echo "(Over)writing $conf_dir/spgw.conf"
    sed -f spgw-r2lab.sed < spgw.conf > $conf_dir/spgw.conf

    echo "========== Rebuilding mme"
    cd $run_dir
    # option --debug is in the doc but not in the code
    ./build_mme --clean --daemon
}

doc-fun configure-hss "configures hss"
function configure-hss() {

    [ -n "$runs_hss" ] || { echo not running hss - skipping ; return; }

    fitid=fit$(r2lab-id)

    echo "========== Reconfiguring hss"
    cd $run_dir
    if [ -z "$new_config_mode" ]; then
	build_args="--clean-certificates --fqdn hss.${oai_realm} --install-hss-files"
    else
	build_args=""
    fi
    if [ -n "$runs_epc" ]; then
	# both services are local
	./build_hss --clean ${build_args}  --local-mme 2>&1 | tee build-hss-conf.log
    else
	# xxx todo
	./build_hss --clean ${build_args} 2>&1 | tee build-hss-conf.log
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
	if [ -z "$new_config_mode" ]; then
	    echo "Running run_epc in background"
	    # --gdb is a possible additional option here
	    ./run_epc --set-nw-interfaces --remove-gtpu-kmodule >& $log_epc &
	else
	    echo "Starting mme in background"
	    ./run_mme >& $log_mme &
	    echo "Starting spgw in background"
	    ./run_spgw >& $log_spgw &
	fi
    fi
}

locks=""
[ -n "$runs_hss" ] && add-to-locks /var/run/oai_hss.pid
[ -n "$runs_epc" ] && add-to-locks /var/run/mme_gw.pid /var/run/mme.pid /var/run/mmed.pid /var/run/spgw.pid

function _manage() {
    # if $1 is 'stop' then the found processes are killed
    mode=$1; shift
    pids=""
    [ -n "$runs_hss" ] && pids="$pids $(pgrep run_hss) $(pgrep oai_hss)"
    [ -n "$runs_epc" ] && pids="$pids $(pgrep run_epc) $(pgrep run_mme) $(pgrep mme_gw) $(pgrep spgw)"
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
	locks=$(ls-locks 2> /dev/null)
	echo "========== Clearing locks $locks"
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
