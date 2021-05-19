# NVDA Check Input Gestures (Sprawdź zdarzenia wejścia)

* Autor: Oleksandr Gryshchenko
* Wersja: 1.0
* Zgodność z wersjami NVDA: 2019.3 i nowsze
* Pobierz [wersja stabilna][1]
* Pobierz [wersja rozwojowa][2]

Znajdź i napraw konflikty zdarzeń wejścia w NVDA i dodatkach. Ogólny termin "zdarzenia wejścia" obejmuje polecenia klawiszowe, polecenia wprowadzone przez klawiatury brajlowskie i zdarzenia wejścia ekranów dotykowych.  
Każdy z zainstalowanych dodatków może wprowadzać zmiany w konfiguracji NVDA poprzez dodawanie lub ponowne przypisywanie istniejących zdarzeń wejścia. Jeśli te same zdarzenia wejścia są powiązane z kilkoma funkcjami, wywołanie niektórych z nich będzie niemożliwe.  

## Szukaj zduplikowanych zdarzeń wejścia
Aby wykryć zduplikowane zdarzenia wejścia, wywołaj menu NVDA, przejdź do podmenu "Narzędzia", następnie - "Check Input Gestures (Sprawdź zdarzenia wejścia)" i aktywuj element menu "Wyszukaj zduplikowane zdarzenia wejścia...".  
Po tym, wszystkie zdarzenia wejścia używane w NVDA zostaną sprawdzone w następującej kolejności:  

1. globalCommands (polecenia NVDA);  
2. globalPlugins (polecenia zainstalowanych dodatków).  

Jeśli zostaną wykryte te same zdarzenia wejścia, które są przypisane do różnych funkcji, ich lista zostanie wyświetlona w osobnym oknie dialogowym.  
Po naciśnięciu klawisza Enter na wybranej pozycji listy, odpowiednia funkcja NVDA zostanie wybrana i otwarta w standardowym oknie dialogowym "Zdarzenia wejścia...", gdzie można usunąć lub zmienić przypisanie skojarzonego zdarzenia wejścia.  

Uwaga: Jak wiesz, funkcje, które nie mają opisu tekstowego, nie pojawiają się w oknie dialogowym "Zdarzenia wejścia...". Dlatego po aktywowaniu takiego elementu zostanie wyświetlone odpowiednie ostrzeżenie.

## Zdarzenia wejścia bez opisu
Aby wyświetlić listę zdarzeń wejścia powiązanych z funkcjami bez opisu tekstowego, jeśli znajdują się one w Twojej konfiguracji NVDA, potrzebujesz wywołać menu NVDA, przejść do podmenu "Narzędzia", następnie - "Zdarzenia wejścia bez opisu...".  
Takie funkcje nie pojawiają się w standardowym oknie dialogowym NVDA "Zdarzenia wejścia...", więc nie jest jeszcze możliwe usunięcie lub ponowne przypisanie skojarzonych zdarzeń wejścia.

## Pomoc
Jednym ze sposobów przeglądania tej strony pomocy jest wywołanie menu NVDA, przejście do podmenu "Narzędzia", następnie - "Check Input Gestures (Sprawdź zdarzenia wejścia)", i aktywowanie "Pomoc".

Uwaga: Wszystkie funkcje dodatku mają swoją reprezentację w oknie NVDA "Zdarzenia Wejścia" i możesz przypisać własne skróty klawiszowe do każdego z nich.

## Wkład
Jesteśmy bardzo wdzięczni wszystkim, którzy dołożyli starań, aby opracować, przetłumaczyć i utrzymać ten dodatek:

* Wafiqtaher - tłumaczenie arabskie;
* Angelo Miguel Abrantes - tłumaczenie portugalskie;
* Cagri Dogan - tłumaczenie tureckie.

## Lista zmian

### Wersja 1.0
* zaimplementowano wyszukiwanie dla zduplikowanych zdarzeń wejścia;
* zaimplementowano wyszukiwanie dla zdarzeń wejścia powiązanych z funkcjami bez opisu tekstowego.

## Zmiany w kodzie źródłowym dodatku
Możesz sklonować to repozytorium, aby wprowadzić zmiany w NVDA Check Input Gestures.

### Zewnętrzne zależności
Można je zainstalować za pomocą pip:

- markdown
- scons
- python-gettext

### Aby spakować dodatek do dystrybucji:
1. Otwórz wiersz poleceń, przejdź do katalogu głównego tego repozytorium
2. Uruchom polecenie **scons**. Utworzony dodatek, jeśli nie było błędów, jest umieszczony w bieżącym katalogu.

[1]: https://github.com/grisov/checkGestures/releases/download/latest/checkGestures-1.0.nvda-addon
[2]: https://github.com/grisov/checkGestures/releases/download/latest/checkGestures-1.0.1-dev.nvda-addon
