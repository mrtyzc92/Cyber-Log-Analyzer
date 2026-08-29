# Cyber Log Analyzer

Cyber Log Analyzer, güvenlik loglarını okuyup ayrıştıran, başarısız giriş denemelerini analiz eden ve sonuçları okunabilir bir rapora dönüştüren öğretici bir Python projesidir.

Proje; profesyonel Python proje yapısını, sorumlulukların ayrılmasını, hata yönetimini, otomatik testleri ve Git/GitHub çalışma düzenini gerçek bir uygulama üzerinden öğrenmek amacıyla geliştirilmektedir.

## Projenin amacı

Bu projenin teknik hedefleri:

- Profesyonel Python proje mimarisini uygulamak
- Log dosyalarını güvenli şekilde okumak
- Ham log satırlarını yapılandırılmış Python nesnelerine dönüştürmek
- Güvenlik olaylarını kural tabanlı olarak analiz etmek
- Şüpheli başarısız giriş denemelerini tespit etmek
- Analiz sonuçlarını okunabilir metin raporlarına dönüştürmek
- Unit test ve integration test yazmak
- Git ve GitHub çalışma düzenini uygulamak

## Desteklenen log biçimi

Her log satırı beş alandan oluşur:

```text
timestamp | level | ip_address | event | username
```

Örnek:

```text
2026-08-18 09:12:42 | WARNING | 192.168.1.25 | LOGIN_FAILED | admin
```

Tarih ve saat biçimi:

```text
%Y-%m-%d %H:%M:%S
```

Örnek:

```text
2026-08-18 09:12:42
```

## Uygulama veri akışı

```text
Log dosyası
    |
    v
Reader
    |
    v
Parser
    |
    v
LogEntry modeli
    |
    v
Security Analyzer
    |
    v
Text Reporter
    |
    v
Okunabilir güvenlik raporu
```

Bileşenlerin sorumlulukları:

- `file_reader.py`: UTF-8 log dosyasını okur, boş satırları atlar.
- `log_parser.py`: Ham metin satırlarını `LogEntry` nesnelerine dönüştürür.
- `log_entry.py`: Tek bir log kaydının veri modelini tanımlar.
- `security_analyzer.py`: Başarısız girişleri IP adresine göre sayar ve eşik değerini aşanları bulur.
- `text_reporter.py`: Analiz sonucunu okunabilir metne dönüştürür.
- `main.py`: Bütün bileşenleri doğru sırayla çalıştırır.

## Proje yapısı

```text
Cyber-Log-Analyzer/
├── config/
├── data/
│   ├── processed/
│   └── raw/
│       └── sample.log
├── docs/
│   └── git-notlari.md
├── src/
│   └── cyber_log_analyzer/
│       ├── analyzers/
│       │   └── security_analyzer.py
│       ├── models/
│       │   └── log_entry.py
│       ├── parsers/
│       │   └── log_parser.py
│       ├── readers/
│       │   └── file_reader.py
│       ├── reporters/
│       │   └── text_reporter.py
│       └── main.py
├── tests/
│   ├── test_file_reader.py
│   ├── test_log_parser.py
│   ├── test_main.py
│   ├── test_security_analyzer.py
│   └── test_text_reporter.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Gereksinimler

- Python 3.13 veya daha yeni bir sürüm
- Git

## Kurulum

Projeyi klonlayın:

```powershell
git clone https://github.com/mrtyzc92/Cyber-Log-Analyzer.git
cd Cyber-Log-Analyzer
```

Python 3.13 ile sanal ortam oluşturun:

```powershell
py -3.13 -m venv .venv
```

PowerShell üzerinde sanal ortamı etkinleştirin:

```powershell
.\.venv\Scripts\Activate.ps1
```

Uygulamayı ve geliştirme bağımlılıklarını editable mode ile kurun:

```powershell
python -m pip install -e ".[dev]"
```

## Uygulamayı çalıştırma

Proje ana klasöründe:

```powershell
python -m cyber_log_analyzer.main
```

Örnek çıktı:

```text
Şüpheli giriş denemeleri:
- 192.168.1.25: 3 başarısız giriş
```

## Şüpheli giriş tespiti

Uygulama yalnızca `LOGIN_FAILED` olaylarını sayar.

Varsayılan eşik değeri:

```text
3
```

Bir IP adresinin başarısız giriş sayısı eşik değerine eşit veya eşikten büyükse IP şüpheli olarak raporlanır.

Örnek analiz sonucu:

```python
{
    "192.168.1.25": 3,
}
```

Eşiği geçen IP bulunmazsa:

```text
Şüpheli giriş denemesi bulunamadı.
```

## Testleri çalıştırma

Bütün testleri çalıştırmak için:

```powershell
python -m pytest -v
```

Test takımı şu bileşenleri kapsar:

- Dosya okuyucu
- Log ayrıştırıcı
- Veri modeli
- Güvenlik analiz kuralları
- Metin raporu
- Uçtan uca uygulama veri akışı
- Hatalı dosya yolu
- Hatalı alan sayısı
- Hatalı tarih biçimi

Mevcut test takımında 22 otomatik test bulunmaktadır.

## Hata yönetimi

Uygulama bazı hatalı durumları bilinçli olarak reddeder:

- Log dosyası bulunamazsa `FileNotFoundError`
- Log satırında beş alan yoksa `ValueError`
- Tarih biçimi beklenen biçime uymuyorsa `ValueError`

Bu davranışlar otomatik testlerle doğrulanmaktadır.

## Kullanılan temel kavramlar

- `pathlib.Path`
- Type hints
- Dataclasses
- Immutable data models
- List comprehensions
- Dictionary comprehensions
- `collections.Counter`
- Exception handling
- Unit testing
- Integration testing
- Editable installation
- Git staging, commit ve push akışı

## Proje durumu

Projenin temel çalışan sürümü tamamlanmıştır.

Mevcut uygulama:

- Log dosyasını okuyabiliyor
- Ham satırları `LogEntry` nesnelerine dönüştürebiliyor
- Başarısız girişleri IP adresine göre sayabiliyor
- Belirlenen eşiği geçen IP adreslerini tespit edebiliyor
- Sonucu okunabilir metin raporu olarak gösterebiliyor
- Temel hata durumlarını yönetebiliyor
- Otomatik testlerle doğrulanabiliyor

Proje şu anda komut satırından örnek log dosyasını ve varsayılan eşik değerini kullanarak çalışmaktadır.

## Flask web arayüzü

Proje, güvenlik loglarını tarayıcı üzerinden analiz etmek için Flask tabanlı bir web arayüzü içerir.

Web arayüzü şu işlemleri gerçekleştirir:

- `.log` ve `.txt` dosyalarını kabul eder.
- Kullanıcıdan şüpheli giriş denemesi eşik değerini alır.
- Yüklenen dosyayı geçici bir çalışma alanında işler.
- Mevcut log okuma, ayrıştırma, analiz ve raporlama bileşenlerini yeniden kullanır.
- Analiz sonucunu HTML sayfasında gösterir.
- Geçersiz dosya uzantısı, eksik dosya, hatalı eşik ve bozuk log içeriği için kontrollü hata mesajları üretir.
- En fazla 1 MB boyutunda dosya yüklenmesine izin verir.

### Geliştirme bağımlılıklarını kurma

Sanal ortam aktifken proje ana klasöründe:

```powershell
python -m pip install -e ".[dev]"