for service in api www; do
    install -m 400 /root/ssl-certificate/2017-01/r2labapi_inria_fr.crt /etc/planetlab/${service}_ssl.crt
    install -m 400 /root/ssl-certificate/2017-01/CAbundle.crt /etc/planetlab/${service}_ca_ssl.crt
    install -m 400 /root/ssl-certificate/2017-01/r2labapi.inria.fr.key /etc/planetlab/${service}_ssl.key
done

echo ==================== the official certs
md5sum /etc/planetlab/{api,www}*{crt,key}
echo ==================== running PLC ssl setup
/etc/plc.d/ssl start >& /dev/null
echo ==================== the official certs (should be untouched)
md5sum /etc/planetlab/{api,www}*{crt,key}

