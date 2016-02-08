# setup de etourdi

## Note historique

### Avant

Jusqu'au 8 février 2016
* tout se passait sur etourdi dans le répertoire

    `/home/etourdi/Documents/Arduino/`

* on n'avait à l'époque qu'une seule version logicielle, dans

    `NITOS_CM_Card_Firmware_v2_1b_for_shield_v1_2_watchdog_no_XML`

* à l'intérieur de ce répertoire on trouve le fichier

    `NITOS_CM_Card_Firmware_v2_1b_for_shield_v1_2_watchdog_no_XML.ino`

### Maintenant

Pour simplifier un peu la nomenclature, je renomme le tout de sorte à avoir

* Un nom + court pour la racine principale
* Qui reste malgré tout toujours propriété de `etourdi:etourdi`; l'outil IDE arduino est à utiliser sous cette identité sous le ubuntu de etourdi

```
# pwd
/home/etourdi/arduino-code
```    
    
À ce stade j'ai maintenant, en ajoutant les deux versions (shield 1.2 et shield 2.1) que nous a envoyés NITOS:

```
# find . -type f
./standalone-2_1b-shield-v1_2/NITOS_CM_Card_Firmware_v2_1b_for_shield_v1_2_watchdog_no_XML.ino
./withursp-3_1-shield-1_2/NITOS_CM_Card_Firm_v3_1_for_shield_v1_2_no_XML_USRP.ino
./withursp-3_1-shield-2_1/NITOS_CM_Card_Firm_v3_1_for_shield_v2_1_no_XML_USRP.ino  
```

* `standalone*` : pour les CMC sans extension
* `withusrp*` : pour les CMC raccordés (potentiellement) à une extension pour USRP