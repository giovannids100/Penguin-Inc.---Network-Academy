## Giorno 1:

- **step 1**: uno switch collega 2 pc, schermata vuota fai tutto da zero è un tutorial, puoi chiedere gratuitamente consigli al pinguino sr., assegna ip statici ai pc


soluzione:

PC1 --------SWITCH------- PC2

- **step 2**: inserire router verso l'esterno

soluzione:

PC1 --------SWITCH------- PC2
            |
            ROUTER



- **step 3**: doppio switch, separiamo le lan

soluzione:

PC00-02 -----SWITCH1----ROUTER------SWITCH2-----PC10-12

## Giorno 2:

- **step 1**: partendo da una rete già esistente, crea una sala server dislocata, collega i due router e attiva DHCP sulla rete server


soluzione:
rete 1 ----router 1 --------router 2(DHCP)--switch2----server endpoints

- **step 2**: DNS server, assegnare hostname

soluzione:
rete 1 ----router 1 --------router 2(DHCP)--switch2----DNS server interno------server endpoints (con hostname assegnati)

- **step 3**: firewall tra le reti, abilita porta 22 e 25 per connettersi ai server in ssh e smtp, abilita porta 53 per il DNS server

soluzione:
rete 1 ----router 1 -----FIREWALL---router 2(DHCP)--switch2----DNS server interno------server endpoints (con hostname assegnati)


## Giorno 3:

- **step 1**: rete già esistente con servizi, server e utenti, piazzare i firewall e creare la DMZ

soluzione

        FW-DMZ
          |
          ROUTER1---SWITCH1---SERVER HTTP
          |
          FW INTERNO
          |
          ROUTER 2
          |
          SWITCH2
          |
        endpoints

- **step 2**: gli utenti hanno bisogno di connettersi da remoto, aggiungi una subnet VPN

soluzione

        FW-DMZ
          |
          ROUTER1---SWITCH1---SERVER HTTP
          |
          FW INTERNO
          |
          ROUTER 2---------F2-VPN---SWITCH3----VPN
          |
          SWITCH2
          |
        endpoints

- **step 3**: alcuni appliance verranno hostati in cloud, integra la rete cloud

soluzione

                                    FW-DMZ
                                    |
                                    ROUTER1---SWITCH1---SERVER HTTP
                                    |
                                    FW INTERNO
                                    |
cloud---SWITCH4---FW-Cloud-------ROUTER 2---------F2-VPN---SWITCH3----VPN
                                    |
                                    SWITCH2
                                    |
                                    endpoints


