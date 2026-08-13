# Cyber Log Analyzer

Cyber Log Analyzer, güvenlik loglarını okuyup ayrıştırmak, şüpheli olayları tespit etmek ve sonuçları raporlamak amacıyla geliştirilen öğretici bir Python projesidir.

## Projenin amacı

Bu projenin teknik hedefleri:

- Profesyonel Python proje mimarisini öğrenmek
- Log okuma ve ayrıştırma süreçlerini uygulamak
- Güvenlik olaylarını kural tabanlı olarak analiz etmek
- Test, debugging, Git ve GitHub çalışma düzenini öğrenmek
- Sorumlulukları ayrılmış, geliştirilebilir bir uygulama oluşturmak

## Proje durumu

Proje geliştirme aşamasındadır. Şu anda temel klasör mimarisi ve geliştirme ortamı hazırlanmaktadır.

## Temel veri akışı

```text
Log dosyası
    ↓
Reader
    ↓
Parser
    ↓
Model
    ↓
Analyzer
    ↓
Reporter