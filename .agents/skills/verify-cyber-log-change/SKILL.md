---
name: verify-cyber-log-change
description: Cyber Log Analyzer projesindeki Python kodu veya testler değiştiğinde, değişiklikleri commit öncesinde test etmek ve Git durumunu doğrulamak için kullanılır.
---

# Cyber Log Analyzer Değişikliklerini Doğrula

Kod üzerinde değişiklik yapma. Yalnızca mevcut değişikliklerin doğruluğunu kontrol et.

## Doğrulama Akışı

1. Değişen dosyaları ve etkilenen davranışı belirle.
2. Önce değişiklikle doğrudan ilgili testleri çalıştır.
3. İlgili testler başarılı olursa `python -m pytest -q` komutuyla bütün testleri çalıştır.
4. `git diff --check` komutuyla commit edilmemiş değişikliklerde boşluk ve biçim hatalarını kontrol et.
5. `git diff --cached --check` komutuyla staging alanındaki değişikliklerde boşluk ve biçim hatalarını kontrol et.
6. `git status --short` komutuyla çalışma alanının Git durumunu kontrol et.

## Sonuç Raporu

Kullanıcıya şu bilgileri kısa ve açık biçimde bildir:

- ilgili testlerin sonucu,
- bütün testlerin sonucu,
- boşluk ve biçim kontrollerinin sonucu,
- değişen dosyalar,
- değişikliklerin commit için hazır olup olmadığı.

Bir komut başarısız olursa dur ve sonraki adıma geçmeden önce hatayı açıkla.

Kullanıcı açıkça istemedikçe:

- dosyaları değiştirme,
- commit oluşturma,
- uzak depoya push yapma.