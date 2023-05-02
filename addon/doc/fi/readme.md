# Tarkista näppäinkomennot

* Tekijä: Oleksandr Gryshchenko
* Versio: 1.0
* Yhteensopivuus: NVDA 2020.3 ja uudemmat
* Lataa [vakaa versio][1]

Etsi ja korjaa NVDA:n ja lisäosien näppäinkomentojen ristiriidat. Yleistermi \"näppäinkomennot\" sisältää näppäinkomennot, pistekirjoitusnäppäimistöltä annetut komennot sekä kosketusnäyttöeleet.

Jokainen asennettu lisäosa voi tehdä muutoksia NVDA:n asetuksiin lisäämällä tai uudelleenmäärittämällä olemassa olevia näppäinkomentoja. Mikäli samoja näppäinkomentoja on liitetty useampiin toimintoihin, joitakin niistä ei voi käyttää.

## Etsi päällekkäiset näppäinkomennot
Etsi päällekkäiset näppäinkomennot avaamalla NVDA-valikko, menemällä Työkalut-alivalikkoon ja valitsemalla "Tarkista näppäinkomennot" ja sitten "Etsi päällekkäiset näppäinkomennot...".

Tämän jälkeen kaikki NVDA:ssa käytettävät näppäinkomennot tarkistetaan seuraavassa järjestyksessä:

1. Yleiset komennot
2. Yleisliitännäiset

Mikäli sama näppäinkomento on määritetty useaan eri toimintoon, niiden luettelo näytetään erillisessä valintaikkunassa.

Kun olet painanut Enter-näppäintä valitun luettelokohteen kohdalla, vastaava NVDA-toiminto valitaan ja avataan tavallisessa "Näppäinkomennot"-valintaikkunassa, jossa voit poistaa tai uudelleenmäärittää siihen liitetyn näppäinkomennon.

Huom: Toiminnot, joilla ei ole kuvausta, eivät näy Näppäinkomennot-valintaikkunassa. Siksi tällaisen kohteen valitsemisen jälkeen näytetään asiasta kertova varoitus.

## Näppäinkomennot ilman kuvausta
Jos haluat tarkastella toimintoihin määritettyjen, ilman kuvausta olevien näppäinkomentojen luetteloa (mikäli sellaisia on), avaa NVDA-valikko, siirry Työkalut-alivalikkoon ja valitse sitten "Näppäinkomennot ilman kuvausta...".

Tällaiset toiminnot eivät näy NVDA:n tavallisessa Näppäinkomennot-valintaikkunassa, joten niihin liitettyjä näppäinkomentoja ei ole vielä mahdollista poistaa tai uudelleenmäärittää.

## Ohje
Yksi tapa tarkastella tätä ohjesivua on avata NVDA-valikko, siirtyä Työkalut-alivalikkoon, avata Tarkista näppäinkomennot -alivalikko ja valita sitten "Ohje".

Huom: Kaikki lisäosan ominaisuudet näkyvät NVDA:n Näppäinkomennot-valintaikkunassa, jossa voit määrittää kullekin toiminnolle oman pikanäppäimen.

## Osallistujat
Olemme erittäin kiitollisia kaikille, jotka ovat nähneet vaivaa tämän lisäosan kehittämiseen, eri kielille kääntämiseen ja ylläpitämiseen:

* Wafiqtaher - arabiankielinen käännös
* Angelo Miguel Abrantes - portugalinkielinen käännös
* Cagri Dogan - turkinkielinen käännös
* Cary Rowen - yksinkertaistetun kiinan käännös

## Muutosloki

### Versio 1.0.4
* Lisäosan yhteensopivuus NVDA 2023.1:n kanssa on testattu.

### Versio 1.0.3
* Lisäosan yhteensopivuus NVDA 2022.1:n kanssa on testattu
* Toteutettu päällekkäisten näppäinkomentojen etsintä
* Toteutettu ilman kuvausta oleviin toimintoihin liitettyjen näppäinkomentojen etsintä

## Lisäosan lähdekoodin muuttaminen
Voit kloonata tämän koodivaraston tehdäksesi muutoksia Tarkista näppäinkomennot -lisäosaan.

### Kolmannen osapuolen riippuvuudet
Nämä voidaan asentaa pip:llä:

- markdown
- scons
- python-gettext

### Lisäosan pakkaaminen jakelua varten
1. Avaa komentokehote ja vaihda hakemistoksi tämän koodivaraston juuri
2. Suorita **scons**-komento. Jos virheitä ei ollut, luotu lisäosa sijoitetaan nykyiseen hakemistoon.

[1]: https://www.nvaccess.org/addonStore/legacy?file=cig
