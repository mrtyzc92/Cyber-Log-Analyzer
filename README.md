# Cyber Log Analyzer

Cyber Log Analyzer, güvenlik loglarını okuyup ayrıştıran, başarısız giriş
denemelerini analiz eden ve sonucu hem komut satırı hem Flask arayüzü üzerinden
sunan öğretici bir Python projesidir.

Sürüm 2.0 ile proje, klasik veri işleme hattının üzerine test edilmiş ve
guardrail'lerle sınırlandırılmış deterministik bir agent mimarisi ekler.

## Neler yapar?

- UTF-8 `.log` ve `.txt` dosyalarını okur.
- Log satırlarını immutable `LogEntry` nesnelerine dönüştürür.
- `LOGIN_FAILED` olaylarını IP adresine göre sayar.
- Belirlenen eşiğe ulaşan IP adreslerini raporlar.
- Aynı analiz hattını CLI, Flask ve agent tool üzerinden yeniden kullanır.
- Tool seçimini registry ve selector üzerinden sınırlar.
- Agent çalışmalarını adım limiti ve terminal durumlarla kontrol eder.
- Ham model JSON'unu doğrulanmış `AgentDecision` nesnesine dönüştürür.
- LLM kararlarını tool allowlist'i ile sınırlar ve hatalarda güvenli biçimde
  `FAIL` kararı üretir.
- Sınırlı in-memory geçmiş ve temel decision eval altyapısı sağlar.

## Desteklenen log biçimi

Her satır beş alandan oluşur:

```text
timestamp | level | ip_address | event | username
```

Örnek:

```text
2026-08-18 09:12:42 | WARNING | 192.168.1.25 | LOGIN_FAILED | admin
```

Tarih biçimi `%Y-%m-%d %H:%M:%S` olmalıdır.

## Mimari

Klasik analiz hattı:

```text
Log dosyası
    -> File Reader
    -> Log Parser
    -> LogEntry
    -> Security Analyzer
    -> Text Reporter
```

Web arayüzündeki agent hattı:

```text
Dosya yükleme
    -> SecurityLogDecisionMaker
    -> AgentLoop
    -> ToolRegistry / ToolSelector
    -> LogAnalyzerTool
    -> AgentState
    -> HTML sonucu
```

LLM karar sınırı:

```text
LanguageModel.generate(prompt)
    -> ham metin
    -> JSON şema doğrulaması
    -> tool allowlist kontrolü
    -> AgentDecision
    -> AgentLoop
```

Model hiçbir zaman registry veya tool nesnelerine doğrudan erişmez. Model
yalnızca karar metni üretir; yetki ve doğrulama uygulama tarafında kalır.

Ayrıntılı açıklama için
[`docs/agent-mimarisi.md`](docs/agent-mimarisi.md) dosyasına bakın.

## Structured Output sözleşmesi

Desteklenen action değerleri:

- `use_tool`: Kayıtlı bir tool çalıştırılmasını ister.
- `complete`: Çalışmayı başarıyla tamamlar.
- `fail`: Çalışmayı kontrollü biçimde başarısız sonlandırır.

Tool kararı örneği:

```json
{
  "action": "use_tool",
  "reason": "The security log must be analyzed",
  "tool_name": "log_analyzer",
  "tool_input": "security.log"
}
```

Parser; geçersiz JSON'u, bilinmeyen action değerini, eksik alanları,
beklenmeyen alanları ve action ile uyumsuz tool alanlarını reddeder.

## LLM entegrasyon sınırı

`LLMDecisionMaker`, sağlayıcıdan bağımsız bir `LanguageModel` protokolü kullanır:

```python
class LanguageModel(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

Projede bilinçli olarak haricî LLM SDK'sı, API anahtarı veya varsayılan ağ
istemcisi bulunmaz. Gerçek bir sağlayıcı kullanılacaksa bu protokolü uygulayan
adapter enjekte edilir. Böylece agent çekirdeği belirli bir sağlayıcıya
bağlanmaz ve testlerde sahte model kullanılabilir.

Flask arayüzü deterministik `SecurityLogDecisionMaker` kullanır. Dosya analizi
gibi kuralları belli bir iş için LLM çağrısı zorunlu değildir.

## Memory ve evals

İki farklı bellek türü ayrılmıştır:

- `AgentState.observations`: Tek çalışma içindeki kısa süreli çalışma belleği.
- `AgentMemory`: Tamamlanmış çalışmaların sabit kapasiteli özet geçmişi.

`AgentMemory` process belleğindedir; uygulama yeniden başladığında silinir.
Kalıcı veritabanı, embedding veya RAG bu eğitim projesinin kapsamına dahil
değildir.

Decision eval altyapısı action ve tool seçimini ölçer. Rapor; toplam vaka,
başarılı vaka, accuracy ve vaka bazlı hata açıklamalarını içerir.

## Proje yapısı

```text
src/cyber_log_analyzer/
├── agents/
│   ├── decision_parser.py
│   ├── decisions.py
│   ├── evals.py
│   ├── llm_decision_maker.py
│   ├── log_analyzer_tool.py
│   ├── loop.py
│   ├── memory.py
│   ├── registry.py
│   ├── security_log_agent.py
│   ├── security_log_workflow.py
│   ├── state.py
│   ├── tool_selector.py
│   └── tools.py
├── analyzers/
├── models/
├── parsers/
├── readers/
├── reporters/
├── web/
└── main.py
```

## Kurulum

Gereksinimler:

- Python 3.13 veya daha yeni bir sürüm
- Git

PowerShell:

```powershell
git clone https://github.com/mrtyzc92/Cyber-Log-Analyzer.git
cd Cyber-Log-Analyzer
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Çalıştırma

CLI:

```powershell
python -m cyber_log_analyzer.main
```

Flask web arayüzü:

```powershell
python -m flask --app cyber_log_analyzer.web:create_app run --debug
```

Ardından terminalde gösterilen yerel adresi tarayıcıda açın.

## Testler

Tüm test takımını çalıştırmak için:

```powershell
python -m pytest -q
```

Sürüm 2.0 kapanışında test takımı 83 test içerir. Kapsanan başlıca alanlar:

- dosya okuma, parsing, analiz ve raporlama,
- CLI ve Flask entegrasyonu,
- agent state ve terminal durumlar,
- tool sonucu, registry ve selector,
- multi-step loop ve adım limiti,
- structured output doğrulaması,
- LLM hata ve allowlist guardrail'leri,
- sınırlı memory,
- decision eval raporları,
- web arayüzünün agent loop entegrasyonu.

## Hata yönetimi ve guardrail'ler

Proje aşağıdaki durumları kontrollü biçimde ele alır:

- bulunamayan dosya,
- UTF-8 olmayan içerik,
- bozuk log satırı,
- geçersiz eşik,
- desteklenmeyen dosya uzantısı,
- 1 MB üzerindeki web yüklemesi,
- boş agent hedefi,
- geçersiz veya aşılmış adım limiti,
- kayıtlı olmayan tool seçimi,
- tool çalışma hatası,
- geçersiz model JSON'u,
- bilinmeyen model action'ı,
- allowlist dışında tool seçimi,
- model sağlayıcı hatası.

## Kapsam sınırı

Cyber Log Analyzer bir eğitim projesidir. Temel agent mimarisini, güvenli tool
çalıştırmayı, structured output'u, memory ve eval prensiplerini öğretmek için
tasarlanmıştır. İleri RAG, kalıcı vektör bellek, gerçek multi-agent koordinasyonu
ve geniş ölçekli OSINT otomasyonu ayrı bitirme projesinin konularıdır.

## Sürüm durumu

`2.0.0` kapsamı aşağıdaki öğrenme aşamalarını tek bir çalışan sistemde
birleştirir:

- modüler Python ve Flask mimarisi,
- test odaklı geliştirme,
- deterministik agent çekirdeği,
- tool registry ve selection,
- multi-step loop ve stop conditions,
- structured output,
- kontrollü LLM decision maker,
- temel memory ve evals,
- agent destekli web iş akışı.
