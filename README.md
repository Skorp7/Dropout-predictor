# Pudokasennustaja

Tällä ohjelmistolla voi ennustaa opiskelijan kurssisuoritusaineiston (+ kurssi-ilmoittautumisaineiston) ja taustatietojen perusteella, onko opiskelija potentiaalinen pudokas. Ohjelmistolla voi myös kouluttaa koneoppimismallin uudelleen.

## Mikä on pudokas?

Ohjelmistossa pudokas on määritelty opiskelijana, jolla ei ole kurssisuorituksia 14-15 kuukauteen ja opiskelija ei myöskään ole ilmoittautunut poissaolevaksi.

## Tekniset vaatimukset

Ohjelmisto tarvitsee toimiakseen pyhon-ympäristön, jossa on tietyt kirjastot asennettuna. Tämän voit luoda esim. condalla tai Dockerilla. Alla ohjeet molempiin.

### Conda
Luo python-ympäristö, jossa on environment.yaml -tiedoston osoittamat kirjastot asennettuna. Esim. condalla: 
```
conda env create -f environment.yaml
conda activate dropout-env
```
Ensimmäinen rivi luo ympäristön, toinen käynnistää sen. Voit sammuuttaa ympäristön ```conda deactivate```.

### Docker

Rakenna ja käynnistä Docker-kontti komennolla:
```
docker compose run --rm --build app
```

## Ohjelman käynnistäminen

### Conda
Aja terminaalissa:
```
conda activate dropout-env
python3 main.py
```

### Docker
Ohjelma käynnistyi jo konttia rakentaessa. Jos sammutit kontin, voit käynnistää sen uudelleen:
```
docker compose run --rm app
```

## Teknisten vaatimusten tarkistaminen

Voit tarkistaa kahdella tavalla, onko kaikki tarpeellinen asennettuna.
1. [Käynnistä ohjelma](#ohjelman-käynnistäminen) ja valitse "V", eli testaa ympäristö.
2. [Käynnistä ohjelma](#ohjelman-käynnistäminen) ja valitse "A", eli testaa kouluttamista esimerkkiaineistolla. Tämän jälkeen valitse "B", eli testaa ennustamista äsken koulutetulla esimerkkimallilla.

Jos kumpikin kohta meni läpi ilman virheilmoituksia, ohjelmointiympäristö on kunnossa. Esimerkkiaineiston ennustukset ovat kansiossa ```data_out/samples/```. (Sivuhuomio: esimerkkiaineiston pitäisi tuottaa yltiöpositiivinen ennuste, eli kukaan ei ole pudokas.)

## Aineiston vaatimukset

Aineisto lisätään kahtena tai kolmena ```.csv``` -tiedostona per vuosikurssi ```data_in/``` -kansioon. Tarkemmin joko ```data_in/predicting/``` tai ```data_in/training/``` riippuen siitä, aiotko kouluttaa mallin uudelleen vai tehdä ennusteen.
Ilmoittautumisaineisto on kolmas aineisto eikä se ole pakollinen jos sitä ei haluta käyttää mallissa.

Huomaa, että .csv tiedostoissa erottimena käytetään puolipistettä. Opiskelija-aineistossa lukukausi-ilmoittautumiset on eroteltu toisitaan pilkuilla.

### Erityisvaatimukset ennustusaineistolle

Tehdäksesi ennusteen, tarvitset opiskelijoiden kurssisuoritus- ja taustatietoaineistot. Jos käytössäsi on esikoulutettu malli, tarvitset aineistoa vähintään 1,5 vuoden ajalta. Toisin sanoen, opiskelijoiden on täytynyt ehtiä opiskella aineiston keruupävään mennessä vähintään 1,5 vuotta (riittää, että opinto-oikeus on ollut voimassa). Voit tehdä ennustuksen kerraallaan vain yhden vuosikurssin opiskelijoille.

Ennustamista varten tarvitset tiedostot ```vuosi_students.csv```, ```vuosi_credits.csv``` ja mallistasi riippuen myös ```vuosi_enrollments.csv```. Korvaa vuosi sillä vuodella, jolloin vuosikurssin opiskelijat saivat opinto-oikeutensa. Tiedostojen muodot on esitelty [alla](#opiskelija-aineisto).

### Erityisvaatimukset koulutusaineistolle

Koulutusaineiston tulee olla riittävän laaja: kerää aineistoa vähintään 800 opiskelijasta ja varmista, että "tuoreimmat" opiskelijat ovat ehtineet opiskella vähintään 15 kuukautta (muuten opiskelijoita ei voi koulutusta varten leimata pudokkaiksi lainkaan).

Aineistot annetaan siten, että jokaista vuotta kohden on 2-3 tiedostoa (esim. 2022_students.csv, 2022_credits.csv ja 2022_enrollments.csv).
Vuosi tarkoittaa tässä tapauksessa tuona vuonna opinto-oikeuden saaneita opiskelijoita.

Esimerkki: Vuonna 2022 aloittaneiden opiskelijoiden kurssisuoritustiedot 2022 alkaen 2025 tammikuuhun asti ovat siis tiedostossa ```2022_credits.csv``` jos aineisto luotaisiin tammikuussa 2025.

Esimerkki: Jos koulutusaineisto koostuisi neljästä vuosikurssista: 2017, 2018, 2019 ja 2020 opinto-oikeuden saaneista opiskelijoista, tarvitsisit tiedostot: ```2017_students.csv```, ```2018_students.csv```, ```2019_students.csv```, ```2020_students.csv``` ```2017_credits.csv```, ```2018_credits.csv```, ```2019_credits.csv```, ```2020_credits.csv```.

### Esimerkkiaineistot

Kansioissa ```data_in/training/samples/``` ja  ```data_in/predicting/samples/``` on esimerkkitiedostot kuvitteellisesti 2023 ja 2024 aloittaneista opiskelijoista. Voit ottaa mallia aineiston muotoiluun näistä tiedostoista.

### Opiskelija-aineisto
Tiedoston nimi: ```vuosi_students.csv```, jossa 'vuosi' on se vuosi muodossa vvvv, jolloin nämä opiskelijat ovat saaneet opinto-oikeutensa.
Formaatti on annettu alla, mutta poista aineistostasi otsikkorivi. Se on vain selkeyden vuoksi.
Formaatti:
```
opisknro;opinto-oik_alku;opinto-oik_loppu;aloituspvm;valmistunut;lukukausi-ilmot;
syntynyt;sukupuoli
a123;2018-08-01;2024-06-19;2018-08-01;true;137:1,138:1,139:3 ... ,1998,1
b124;2017-08-01;2024-06-19;2017-08-01;false;137:1,138:1,139:1 ... ,1980,2
```
### Kurssisuoritusaineisto
Tiedoston nimi: ```vuosi_credits.csv```, jossa 'vuosi' on se vuosi muodossa vvvv, jolloin nämä opiskelijat ovat saaneet opinto-oikeutensa.
Formaatti on annettu alla, mutta poista aineistostasi otsikkorivi. Se on vain selkeyden vuoksi.
```
opisknro;arvosana;opintopisteet;suoritus_pvm;kurssi
a123;4;10;2019-05-08;TKT20001
a123;5;5;2018-12-21;TKT10001
b124;4;5;2018-12-21;TKT10001
```

### Ilmoittautumisaineisto (vapaaehtoinen)
Tiedoston nimi: ```vuosi_enrollments.csv```, jossa 'vuosi' on se vuosi muodossa vvvv, jolloin nämä opiskelijat ovat saaneet opinto-oikeutensa.
Formaatti on annettu alla, mutta poista aineistostasi otsikkorivi. Se on vain selkeyden vuoksi.
```
opisknro;lukukausi;ilm-pvm;kurssi
a123;138;2018-11-01;TKT10001
a123;143;2019-03-01;TKT20001
b124;138;2018-11-01;TKT10001
```

## Ennustaminen

Jos sinulle on toimitettu esikoulutettu malli, voit tehdä ennusteita ilman koulutusvaihetta. Käyttääksesi valmista mallia, käynnistä ohjelma ylläolevan ohjeen mukaisesti ja valitse ohjelmasta valinta "Ennusta". Ohjelma kertoo tarkemmin, minkälainen valmiiksi koulutettu malli on. Lisää tarpeelliset aineistot kansioon ```data_in/predicting/``` ja käynnistä ennustaminen.

Ennustusten tulokset tulee tiedostoon ```data_out/predictions.csv```. Tiedostossa kunkin opiskelijanumeron kohdalla on ennusteen tulos 1 (pudokas) tai 0 (ei-pudokas).

Esimerkki ennustamisen käyttöliittymästä:
![Käyttöliittymä](app/pictures/ui_pred.png)

## Uudelleen kouluttaminen

Mallin uudelleenkouluttaminen tulee tarpeelliseksi, jos halutaan käyttää eri parametrejä kuin valmismallissa on käytetty. Uudelleenkoulutus on myös aiheellista kun nykyinen aineisto alkaa olla vanhentunutta. Esimerkiksi jos opiskelijoiden kurssikäyttäytyminen, ei-valmistuvien osuus, kurssien läpäisyaste tai arviointi muuttuu rajusti.

Koulutusaineiston tulee olla riittävän laaja: kerää aineistoa vähintään 800 opiskelijasta ja varmista, että "tuoreimmat" opiskelijat ovat ehtineet opiskella vähintään 15 kuukautta (muuten opiskelijoita ei voi koulutusta varten leimata pudokkaiksi lainkaan).

Mallin koulutus tapahtuu valitsemalla ohjelmassa "T". Ohjelma kysyy parametrit, joita halutaan käyttää. Lisää aineistot ```data_in/training/``` kansioon ja käynnistä koulutus.

Esimerkki kouluttamisen käyttöliittymästä:
![Käyttöliittymä](app/pictures/ui.png)
