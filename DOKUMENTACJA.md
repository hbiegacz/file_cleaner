# File Cleaner

Narzędzie wiersza poleceń do organizowania dużych kolekcji plików rozproszonych w wielu katalogach.
Znajduje duplikaty, brakujące pliki, puste/tymczasowe pliki, konflikty nazw oraz problemy z uprawnieniami,  a następnie sugeruje lub stosuje odpowiednią poprawkę.

# Testowane na komputerze laboratoryjnym z pythonem 3.8.10

## Użycie

```bash
python src/main.py -b <BAZA> <ŹRÓDŁO> [ŹRÓDŁO ...] [opcje]
```

`BAZA` to główny katalog, w którym docelowo powinny znaleźć się wszystkie pliki.
`ŹRÓDŁO` to jeden lub więcej katalogów do przeskanowania wraz z bazą.

## Opcje

| Flaga | Skrót | Opis |
|---|---|---|
| `--help` | `-h` |**Wyświetl w terminalu listę opcji, flag programu** |
| `--all` | `-a` | Uruchom wszystkie sprawdzenia |
| `--remove-duplicates` | `-d` | Usuń zduplikowane pliki, zachowując najstarszy |
| `--remove-empty` | `-e` | Usuń puste pliki (0 bajtów) |
| `--remove-temporary` | `-t` | Usuń pliki tymczasowe (*.tmp, *~, *.bak) |
| `--copy-missing` | `-c` | Skopiuj pliki, których brakuje w BAZIE |
| `--move-missing` | `-m` | Przenieś pliki, których brakuje w BAZIE |
| `--resolve-conflicts` | `-r` | Interaktywnie rozwiązuj konflikty plików o tej samej nazwie |
| `--fix-permissions` | `-p` | Napraw pliki z błędnymi uprawnieniami |
| `--fix-suspicious-names` | `-s` | Zmień nazwy plików z problematycznymi znakami |
| `--dry-run` | `-dr` | Podgląd akcji bez wprowadzania jakichkolwiek zmian |
| `--warnings` | `-w` | Pokaż ostrzeżenia dla niedostępnych plików |

## Przykładowe komendy

```bash
# wyświetl opis programu i flag konfigurujących jego działanie
python src/main.py --help

# podgląd wszystkich sprawdzeń bez zmieniania czegokolwiek
python src/main.py -b ~/dokumenty ~/kopia1 ~/kopia2 ~/kopia3 --all --dry-run

# usuń duplikaty i puste pliki
python src/main.py -b ../jakis_wyzszy_katalog/dokumenty ~/kopia1 --remove-duplicates --remove-empty --warnings

# skopiuj brakujące pliki i napraw uprawnienia
python src/main.py -b ~/dokumenty ~/kopia1 ~/kopia2 -c -p 
```

> UWAGA <br/>
> Wywołanie programu bez jakichkolwiek flag będzie skutkowało pominięciem każdej z funkcjonalności. Aby dana czynność została wykonana należy ją **wskazać**, np. bezpośrednio `--remove-duplicates --copy-missing --fix-suspicious-names ...` lub po prostu wywołując wszystkie możliwe czynności `--all`.

## Konfiguracja

Ustawienia są ładowane z pliku `.clean_files` w katalogu projektu. DOKŁADNĄ ŚCIEŻKĘ DO TEGO PLIKU MOŻEMY ZMIENIĆ NA GÓRZE PLIKU `src/settings.py`.
Jeśli plik nie istnieje, używane są wartości domyślne.

```json
{
  "TARGET_PERMISSIONS": "rw-r--r--",
  "SUSPICIOUS_CHARS": [" ", "'", "\"", ",", ";", "*", "?", "$", "#", "&", "|", "\\"],
  "SUSPICIOUS_CHAR_SUBSTITUTE": "_",
  "TEMP_FILE_PATTERNS": ["*.tmp", "*~", "*.bak"],
  "DRY_RUN": true,
  "KEEP_DUPLICATE_STRATEGY": "oldest",
  "IGNORED_DIRS": [".git", "__pycache__", ".DS_Store", "node_modules", ".idea"]
}
```

## Dane testowe

Aby wygenerować zestaw katalogów testowych  możemy skorzystać ze skryptu w pliku `create_test_dirs.sh`:

```bash
$ bash create_test_dirs.sh

$ tree test_data/

    test_data
    ├── base
    │   ├── documents
    │   │   ├── notes.txt
    │   │   ├── report.txt
    │   │   └── report.txt~
    │   ├── misc
    │   │   ├── config.cfg
    │   │   ├── empty_file.txt
    │   │   ├── restricted.txt
    │   │   └── session.tmp
    │   └── photos
    │       ├── my photo 2024.jpg
    │       └── scan;final.pdf
    ├── source1
    │   ├── docs
    │   │   ├── also_empty.txt
    │   │   ├── executable_doc.txt
    │   │   ├── old
    │   │   │   ├── archived
    │   │   │   │   └── notes.bak
    │   │   │   ├── notes.txt
    │   │   │   └── report_copy.txt
    │   │   └── only_in_source1.txt
    │   └── media
    │       └── photos
    │           └── holiday photo #1.jpg
    └── source2
        ├── backup
        │   ├── another_missing.txt
        │   └── report_backup.txt
        └── super
            └── deep
                └── dir
                    └── structure
                        ├── config.cfg
                        ├── deep_file.txt
                        └── file with spaces & symbols.txt

    17 directories, 21 files
```

## Zawartość plików

```bash
src/
├── .clean_files
├── arg_parser.py
├── executor.py
├── inspector.py
├── main.py
├── scanner.py
└── settings.py

1 directory, 7 files
```
Aplikacja jest podzielona na kilka głównych modułów, gdzie znajduje się odpowiednia logika:

* **`src/main.py`** – Główny punkt wejściowy. Organizuje cały przepływ pracy: wczytuje ustawienia, inicjuje skanowanie plików i wywołuje kolejne kroki inspekcji/naprawy na podstawie flag użytkownika.
* **`src/arg_parser.py`** – Moduł obsługujący wszystkie argumenty i flagi wiersza poleceń, udostępniając je w wygodnej formie reszcie aplikacji.
* **`src/settings.py`** – Służy do zarządzania konfiguracją. Wczytuje i parsuje ustawienia z pliku `.clean_files` (lub stosuje domyślne).
* **`src/scanner.py`** – Odpowiada za przeszukiwanie wskazanych katalogów i generowanie początkowych list plików, automatycznie pomijając zdefiniowane foldery wykluczone.
* **`src/inspector.py`** – Logika decyzyjna/analityczna. Zawiera funkcje wyszukujące konkretne anomalie (duplikaty, podejrzane nazwy, puste lub tymczasowe pliki, braki w bazie itp.), niczego nie modyfikując.
* **`src/executor.py`** – Logika wykonawcza. To tu odbywają się faktyczne modyfikacje na systemie plików (kopiowanie, usuwanie, zmiany uprawnień/nazw). W trybie `--dry-run` tylko wypisuje w terminalu planowane zmiany, symulując ich przebieg.
