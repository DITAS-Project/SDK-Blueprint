### TODO
##### Incontro del 10/07

- ~~aggiungere anche lo scheletro blueprint vuoto in vdc_template~~
- ~~nel comando create, di default non viene fatto il push del bp generato,
  se invece viene specificato l'opzione push sì~~
- ~~nel dal_template inserire una cartella 'proto'~~
- ~~IS - Testing_Output_Data: se il file zip non esiste, mettiamo stringa
  vuota a 'zip_data'~~
- ~~rendere la generazione del blueprint libera da crash dovuti a campi
  all'interno dei file di configurazione lasciati vuoti~~

- cookbook_appendix: bisogna unire file provienienti da vdc e dal, in
  qualche modo. In attesa di indicazioni da Giovanni
- aggiungere print per lo stato della generazione del blueprint, sezione
  cookbook


- ~~in fase di repo-init creare la cartella data-management~~
- ~~aggiustata l'indentazione, file in vdc_template/DATA_MANAGEMENT.json~~
  - ~~dataUtility, privacy, security sono degli array di elementi struttu-
    rati come DATA_MGMT_dataUtility_security_privacy_elem.json~~
  - ~~a sua volta ognuno di questi elementi avrà all'interno di properties
    un ulteriore oggetto JSON il CUI NOME E' QUELLO DELLA METRICA, quindi
    non si può definire a priori ma c'è un ulteriore file della sua
    struttura DATA_MGMT_dataUtility_security_privacy_elem_prop.json~~

~~in fase di create, creare un file con la lista delle metriche che
  andrà a popolare la sezione data_management sotto data utility.~~
  - ~~Di default vengono messe tutte le metriche possibili, poi verranno can-
    cellate manualmente quelle non interessanti/non calcolabili.~~
- ~~per ogni metodo, si suppone che esista un file metodo.json contenente tutte le metriche nella
  stessa cartella dei zip (d'ora in avanti data-management conterrà entrambe le informazioni)~~


##### Incontro del 23/07

- ~~Definire uno step intermedio tra repo-init e bp create in cui 
  per ogni metodo dell'API viene creato un file con tutte le metriche 
  possibili.
  L'utente potrebbe modificare manualmente queste liste per metodo, 
  invece la parte bp create prenderà solo le metriche "sopravvissute" e
  compilerà il blueprint~~
- Testare lo step precedente usando un VDC remoto invece che precedentemente scaricato in tmp

##### Incontro del 25/09

- provare se si riesce a installare senza problemi su macchina vuota
  (nello specifico senza git)
- fare uno shell script per l'installazione del programma
- un nuovo comando 'publish' per fare una chiamata REST POST al servizio
  di pubblicazione blueprint 
- fare anche un 'unpublish'

- ~~Mettere i nomi al codice~~
