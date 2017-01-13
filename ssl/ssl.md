# SSL certificates

* January 2017
* obtained through digicert using DSI recommendation
* see M. Vesin's emails

[https://wiki.inria.fr/support/Demander_un_certificat_serveur]()

# r2labapi

Delivery by digicert contains 2 files

```
[root@r2labapi 2017-01]# ls -l *.crt
-rw-r--r-- 1 root root 1818 Jan 12 05:34 DigiCertCA.crt
-rw-r--r-- 1 root root 1946 Jan 12 05:34 r2labapi_inria_fr.crt
```

the trick is that `/etc/plc.d/ssl` expects e.g. `api_ssl.crt` and `api_ca_ssl.crt` to verify this

```
openssl verify -CAfile api_ca_ssl.crt api_ssl.crt
```

***BUT*** `DigiCertCA.crt` is not self-signed, so we need to complete the chain up to the self-signed root certificate; here's how:

```
openssl x509 -in DigiCertCA.crt -noout -text
```

look for 

```
            Authority Information Access:
                OCSP - URI:http://ocsp.digicert.com
                CA Issuers - URI:http://cacerts.digicert.com/DigiCertAssuredIDRootCA.crt
```

then fetch it, convert to pem, and build a bundle by adding the intermediate and the root

```
# fetch it - it's actually a DER 
curl -o DigiCertAssuredIDRootCA.der http://cacerts.digicert.com/DigiCertAssuredIDRootCA.crt
# convert it to PEM
openssl x509 -inform der -in DigiCertAssuredIDRootCA.der > DigiCertAssuredIDRootCA.crt
# create bundle
cat DigiCertCA.crt DigiCertAssuredIDRootCA.crt > CAbundle.crt
# check it
openssl verify -CAfile CAbundle.crt r2labapi_inria_fr.crt
r2labapi_inria_fr.crt: OK
```

then install in `/etc/planetlab` as usual, using `CAbundle.crt` as `api_ca_ssl.crt` (same for www of course)

# r2lab

