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
    

##########
doc-fun cn-git-fetch "run fetch origin in openair-cn git repo"
function cn-git-fetch() {
    cd /root/openair-cn
    git fetch origin
    cd - >& /dev/null
}

doc-fun cn-git-select-branch "select branch in openair-cn; typically master or unstable or v0.3.1"
function cn-git-select-branch() {
    branch=$1; shift
    if [ -z "$branch" ]; then
	cn-git-get-branch
    else
	cd /root/openair-cn
	git reset --hard HEAD
	rm BUILD/EPC/epc.conf.in
	git checkout --force $branch
	cd - >& /dev/null
    fi
}

####################
# 

run_dir=/root/openair-cn/SCRIPTS
[ -n "$runs_hss" ] && {
    log_hss=$run_dir/hss.log
    add-to-logs $log_hss
    template_dir=/root/openair-cn/ETC/
    conf_dir=/usr/local/etc/oai
    add-to-configs $conf_dir/hss.conf
    add-to-configs $conf_dir/freeDiameter/hss_fd.conf
}
[ -n "$runs_epc" ] && {
    log_mme=$run_dir/mme.log; add-to-logs $log_mme
    out_mme=$run_dir/mme.out; add-to-logs $out_mme
    log_spgw=$run_dir/spgw.log; add-to-logs $log_spgw
    out_spgw=$run_dir/spgw.out; add-to-logs $out_spgw
    template_dir=/root/openair-cn/ETC/
    conf_dir=/usr/local/etc/oai
    add-to-configs $conf_dir/mme.conf
    add-to-configs $conf_dir/freeDiameter/mme_fd.conf
    add-to-configs $conf_dir/spgw.conf
    add-to-datas /etc/hosts
}

doc-fun dumpvars "list environment variables"
function dumpvars() {
    echo "oai_role=${oai_role}"
    echo "oai_ifname=${oai_ifname}"
    echo "runs_hss=$runs_hss"
    echo "runs_epc=$runs_epc"
    echo "run_dir=$run_dir"
    echo "template_dir=$template_dir"
    echo "conf_dir=$conf_dir"
    echo "_configs=\"$(get-configs)\""
    echo "_logs=\"$(get-logs)\""
    echo "_datas=\"$(get-datas)\""
    echo "_locks=\"$(get-locks)\""
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

doc-fun image "builds hss and epc and installs dependencies" 
function image() {
    
    gitup
    cd $run_dir
    echo "========== Building HSS"
    [ -n "$runs_hss" ] && run-in-log  build-hss-image.log ./build_hss -i
    echo "========== Building EPC"
    if [ -n "$runs_epc" ]; then
	run-in-log build-mme-image-i.log ./build_mme -i
	run-in-log build-spgw-image-i.log ./build_spgw -i
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

    init-clock
    [ "$oai_ifname" == data ] && echo Checking interface is up : $(data-up)
    echo "========== Rebuilding the GTPU module"
    cd $run_dir
    run-in-log init-spgw-j.log ./build_spgw -j -f
    echo "========== Refreshing the depmod index"
    depmod -a
    
}

doc-fun build "build hss and/or epc"
function build() {
    build-hss
    build-epc
}

doc-fun configure "configure hss and/or epc"
function configure() {
    echo "========== Checking /etc/hosts"
    check-etc-hosts
    configure-hss
    configure-epc
}

function build-epc() {

    [ -n "$runs_epc" ] || { echo not running epc - skipping ; return; }

    echo "========== Rebuilding mme"
    # option --debug is in the doc but not in the code
    run-in-log build-mme.log ./build_mme --clean
    
    echo "========== Rebuilding spgw"
    run-in-log build-spgw.log ./build_spgw --clean
    
}    

function configure-epc() {

    [ -n "$runs_epc" ] || { echo not running epc - skipping ; return; }

    mkdir -p /usr/local/etc/oai/freeDiameter
    local id=$(r2lab-id)
    local fitid=fit$id
    local localip="192.168.${oai_subnet}.${id}/24"
    local hssid=$(get-peer)
    local hssip="192.168.${oai_subnet}.${hssid}"

    cd $template_dir

    cat > mme-r2lab.sed <<EOF
s|RUN_MODE.*=.*|RUN_MODE = "OTHER";|
s|REALM.*=.*|REALM = "${oai_realm}";|
s|.*YOUR GUMMEI CONFIG HERE|{MCC="208" ; MNC="95"; MME_GID="4" ; MME_CODE="1"; }|
s|MME_INTERFACE_NAME_FOR_S1_MME.*=.*|MME_INTERFACE_NAME_FOR_S1_MME = "${oai_ifname}";|
s|MME_IPV4_ADDRESS_FOR_S1_MME.*=.*|MME_IPV4_ADDRESS_FOR_S1_MME = "${localip}";|
s|MME_INTERFACE_NAME_FOR_S11_MME.*=.*|MME_INTERFACE_NAME_FOR_S11_MME = "lo";|
s|MME_IPV4_ADDRESS_FOR_S11_MME.*=.*|MME_IPV4_ADDRESS_FOR_S11_MME = "127.0.2.1/8";|
s|SGW_IPV4_ADDRESS_FOR_S11.*=.*|SGW_IPV4_ADDRESS_FOR_S11 = "127.0.3.1/8";|
s|"CONSOLE"|"${out_mme}"|
/MNC="93".*},/d
s|MNC="93"|MNC="95"|
EOF
    echo "(Over)writing $conf_dir/mme.conf"
    sed -f mme-r2lab.sed < mme.conf > $conf_dir/mme.conf
    # remove the extra TAC entries

    cat > mme_fd-r2lab.sed <<EOF
s|Identity.*=.*|Identity="${fitid}.${oai_realm}";|
s|Realm.*=.*|Realm="${oai_realm}";|
s|ConnectTo = "127.0.0.1"|ConnectTo = "${hssip}"|
s|openair4G.eur|r2lab.fr|g
EOF
    echo "(Over)writing $conf_dir/freeDiameter/mme_fd.conf"
    sed -f mme_fd-r2lab.sed < mme_fd.conf > $conf_dir/freeDiameter/mme_fd.conf
    
    cat > spgw-r2lab.sed <<EOF
s|SGW_INTERFACE_NAME_FOR_S11.*=.*|SGW_INTERFACE_NAME_FOR_S11 = "lo";|
s|SGW_IPV4_ADDRESS_FOR_S11.*=.*|SGW_IPV4_ADDRESS_FOR_S11 = "127.0.3.1/8";|
s|SGW_INTERFACE_NAME_FOR_S1U_S12_S4_UP.*=.*|SGW_INTERFACE_NAME_FOR_S1U_S12_S4_UP = "${oai_ifname}";|
s|SGW_IPV4_ADDRESS_FOR_S1U_S12_S4_UP.*=.*|SGW_IPV4_ADDRESS_FOR_S1U_S12_S4_UP = "${localip}";|
s|OUTPUT.*=.*|OUTPUT = "${out_spgw}";|
s|PGW_INTERFACE_NAME_FOR_SGI.*=.*|PGW_INTERFACE_NAME_FOR_SGI = "control";|
s|PGW_IPV4_ADDRESS_FOR_SGI.*=.*|PGW_IPV4_ADDRESS_FOR_SGI = "192.168.3.${id}/24";|
s|DEFAULT_DNS_IPV4_ADDRESS.*=.*|DEFAULT_DNS_IPV4_ADDRESS = "138.96.0.10";|
s|DEFAULT_DNS_SEC_IPV4_ADDRESS.*=.*|DEFAULT_DNS_SEC_IPV4_ADDRESS = "138.96.0.11";|
s|192.188.0.0/24|192.168.10.0/24|g
s|192.188.1.0/24|192.168.11.0/24|g
EOF
    echo "(Over)writing $conf_dir/spgw.conf"
    sed -f spgw-r2lab.sed < spgw.conf > $conf_dir/spgw.conf

    cd $run_dir
    echo "===== generating certificates"
    ./check_mme_s6a_certificate /usr/local/etc/oai/freeDiameter ${fitid}.${oai_realm}

}

function build-hss() {
    cd $run_dir
    if [ -n "$runs_epc" ]; then
	# both services are local
	# xxx never seen this setup yet
	echo "ERROR : new-style config of HSS+EPC in the same box is unsupported"
    else
	run-in-log build-hss-remote.log ./build_hss --clean
    fi
}

function configure-hss() {

    [ -n "$runs_hss" ] || { echo not running hss - skipping ; return; }

    fitid=fit$(r2lab-id)

    mkdir -p /usr/local/etc/oai/freeDiameter
    local id=$(r2lab-id)
    local fitid=fit$id
    local localip="192.168.${oai_subnet}.${id}/24"

    cd $template_dir

    cat > hss-r2lab.sed <<EOF
s|@MYSQL_user@|root|
s|@MYSQL_pass@|linux|
s|OPERATOR_key.*|OPERATOR_key = "11111111111111111111111111111111";|
EOF
    echo "(Over)writing $conf_dir/hss.conf"
    sed -f hss-r2lab.sed < hss.conf > $conf_dir/hss.conf

    cat > hss_fd-r2lab.sed <<EOF
s|openair4G.eur|${oai_realm}|
EOF

    echo "(Over)writing $conf_dir/freeDiameter/hss_fd.conf"
    sed -f hss_fd-r2lab.sed < hss_fd.conf > $conf_dir/freeDiameter/hss_fd.conf
    echo "(Over)writing $conf_dir/freeDiameter/acl.conf"
    sed -f hss_fd-r2lab.sed < acl.conf > $conf_dir/freeDiameter/acl.conf

    cd $run_dir
    echo "===== generating certificates"
    ./check_hss_s6a_certificate /usr/local/etc/oai/freeDiameter hss.${oai_realm}

    echo "===== populating DB"
    # xxx ???
    ./hss_db_create localhost root linux hssadmin admin oai_db
    ./hss_db_import localhost root linux oai_db ../SRC/OAI_HSS/db/oai_db.sql
    populate-db
}

# not declared in available since it's called by build
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
    cd $run_dir
    if [ -n "$runs_hss" ]; then
	echo "Running run_hss in background"
	./run_hss >& $log_hss &
    fi
    if [ -n "$runs_epc" ]; then
	echo "Launching mme and spgw in background"
	./run_mme >& $log_mme &
	./run_spgw -r >& $log_spgw &
    fi
}

locks=""
[ -n "$runs_hss" ] && add-to-locks /var/run/oai_hss.pid
[ -n "$runs_epc" ] && add-to-locks /var/run/mme_gw.pid /var/run/mme.pid /var/run/mmed.pid /var/run/spgw.pid

########################################
doc-fun status "displays the status of the epc and/or hss processes"
doc-fun stop "stops the epc and/or hss processes & clears locks"
doc-fun status "displays the status of the softmodem-related processes"
doc-fun stop "stops the softmodem-related processes"

function -list-processes() {
    pids=""
    [ -n "$runs_hss" ] && pids="$pids $(pgrep run_hss) $(pgrep oai_hss)"
    [ -n "$runs_epc" ] && pids="$pids $(pgrep run_epc) $(pgrep run_mme) $(pgrep mme_gw) $(pgrep spgw)"
    pids="$(echo $pids)"
    echo $pids
}

##############################
doc-fun manage-db "runs mysql on the oai_db database" 
function manage-db() {
    mysql --user=root --password=linux oai_db
}

####################
define_main

########################################
main "$@"
