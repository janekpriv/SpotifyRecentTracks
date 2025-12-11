# 🎧 Spotify Lead Analyzer – Flask + Celery + Docker

Aplikacja została stworzona w celu zbudowania kompletnego systemu backendowego do obsługi logowania użytkowników przez **Spotify OAuth**, pobierania ich danych oraz asynchronicznego przetwarzania zadań w tle za pomocą **Celery**. Projekt ma charakter edukacyjno-praktyczny i służył do nauczenia się:

* pracy z Flask w środowisku produkcyjnym,
* integracji OAuth,
* obsługi kolejki zadań (Celery + Redis),
* konteneryzacji aplikacji (Docker, Docker Compose),
* wdrażania aplikacji na serwer VPS.

---

## 🚀 Funkcjonalności

* 🔐 Logowanie użytkownika przez **Spotify OAuth**
* 🎵 Pobieranie danych użytkownika (np. top songs, profile info)
* 🧵 Asynchroniczne zadania wykonywane przez **Celery Worker**
* 🗄️ Dane użytkowników zapisywane w lokalnej bazie **SQLite**
* 🐳 Uruchamianie całości w kontenerach **Docker**
* 🌐 Możliwość wdrożenia na serwer VPS i podpięcia domeny

---

## 📂 Struktura projektu

```
.
├── main.py
├── tasks.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── instance/
    └── User.db
└── static/css
    └── css files
└── templates/
    └── html files

```

---

## ⚙️ Wymagane usługi

* **Flask** – backend / API
* **Celery** – obsługa zadań w tle
* **Redis** – broker i backend Celery
* **SQLite** – lekka baza danych zapisywana lokalnie w katalogu `instance`

---

## 🐳 Uruchamianie projektu lokalnie (Docker)

1. Zbuduj i uruchom kontenery:

   ```bash
   docker-compose up --build
   ```

2. Aplikacja będzie dostępna pod:

   ```
   http://localhost:8000
   ```

3. Baza danych będzie tworzona automatycznie w katalogu:

   ```
   instance/User.db
   ```

---

## 🌍 Deployment na VPS

1. Sklonuj projekt na serwer:

   ```bash
   git clone <repo>
   cd <project>
   ```

2. Uruchom w tle:

   ```bash
   docker-compose up -d
   ```

3. Upewnij się, że port **8000** jest otwarty.

4. Wejdź na:

   ```
   http://IP_TWOJEGO_SERWERA:8000
   ```

5. Jeśli korzystasz z domeny — skonfiguruj Cloudflare / DNS → record A → IP VPS.

6. Do produkcyjnego HTTPS użyj:

   * Traefik
     lub
   * Nginx + certbot (reverse proxy)

---

## 🔧 Konfiguracja bazy danych

W projekcie użyto SQLite z lokalizacją:

```py
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/User.db"
```

Dzięki temu:

* baza działa zarówno lokalnie, jak i w Dockerze,
* katalog `instance/` jest montowany jako volume,
* dane nie znikają przy restarcie.

---

## 🔁 Celery

Worker uruchamiany jest w kontenerze:

```yaml
celery_worker:
  command: celery -A main.celery worker -l info --pool=solo
```

Wysyłanie zadań działa po stronie aplikacji, zapisując efekty do SQLite.


## 📜 Licencja

Projekt jest swobodnie modyfikowalny do użytku własnego.

