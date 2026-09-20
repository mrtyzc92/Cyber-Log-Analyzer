# Agent Mimarisi

Bu belge Cyber Log Analyzer 2.0 içindeki agent bileşenlerinin neden ayrı
tutulduğunu ve birlikte nasıl çalıştığını açıklar.

## Temel ilke

Bir language model karar önerebilir; yetkiyi elinde tutmamalıdır.

Bu nedenle sistem üç sorumluluğu birbirinden ayırır:

1. `DecisionMaker` bir sonraki action'ı seçer.
2. `ToolSelector` yalnızca registry içindeki tool'u çözer.
3. `AgentLoop` state geçişlerini, tool çalıştırmayı ve stop condition'ları
   yönetir.

Model çıktısının doğrudan fonksiyon çağrısına dönüşmesine izin verilmez.

## Veri akışı

```text
AgentState
    |
    v
DecisionMaker.decide(state)
    |
    v
AgentDecision
    |
    +--> COMPLETE --> state.complete(...)
    |
    +--> FAIL ------> state.fail(...)
    |
    +--> USE_TOOL
            |
            v
       ToolSelector
            |
            v
        AgentTool.run
            |
            v
        ToolResult
            |
            +--> success --> observation --> yeni karar
            |
            +--> failure --> state.fail(...)
```

## Structured Output sınırı

`LLMDecisionMaker`, `LanguageModel.generate()` metodundan ham metin alır.
`parse_agent_decision()` bu metni aşağıdaki sırayla doğrular:

1. Metin geçerli JSON mu?
2. JSON kökü object mi?
3. Yalnızca izin verilen alanlar mı var?
4. `action` desteklenen değerlerden biri mi?
5. `reason` boş olmayan string mi?
6. `use_tool` kararı gerekli tool alanlarını içeriyor mu?
7. Final kararlar gereksiz tool alanlarından arındırılmış mı?

Ardından `LLMDecisionMaker`, seçilen tool adını kendi allowlist'iyle
karşılaştırır. Parser şemayı, allowlist ise yetkiyi kontrol eder. Bunlar aynı
şey değildir.

## Prompt güvenliği

Prompt içinde goal, observations, memory ve tool adları JSON context olarak
verilir. Modele bu değerleri talimat değil veri olarak değerlendirmesi
söylenir. Bu tek başına prompt injection'ı çözmez; asıl güvenlik sınırı model
sonrasında çalışan parser, allowlist, registry ve step limit katmanlarıdır.

## State ve stop condition'lar

`AgentState` aşağıdaki durumları taşır:

- `READY`
- `RUNNING`
- `COMPLETED`
- `FAILED`

`AgentLoop` şu durumlarda durur:

- decision `COMPLETE` döndürür,
- decision `FAIL` döndürür,
- tool yapılandırılmış başarısız sonuç döndürür,
- tool seçimi veya çalışması hata verir,
- `max_steps` sınırı aşılır.

Bu sınırlar sonsuz döngüyü ve kontrolsüz tool kullanımını engeller.

## Memory

`AgentState.observations`, tek run sırasında tool'lardan dönen çalışma
belleğidir. `AgentMemory` ise terminal state'lerin snapshot'larını saklar.

Snapshot kullanılmasının nedeni, geçmişe canlı ve daha sonra değiştirilebilen
bir `AgentState` referansı koymamaktır. Bellek kapasitesi dolunca en eski kayıt
çıkarılır.

Bu uygulama belleği bilinçli olarak process içi ve geçicidir. Kalıcı memory veya
RAG gerektiğinde ayrı bir storage adapter tasarlanmalıdır.

## Evals

`evaluate_decision_maker()` her vaka için yeni bir `AgentState` üretir ve
beklenen davranışla gerçek kararı karşılaştırır.

Temel metrikler:

- action doğruluğu,
- tool selection doğruluğu,
- karar üretiminin exception atmadan tamamlanması.

`reason` metni birebir eşitlikle puanlanmaz. Aynı doğru gerekçe farklı
kelimelerle ifade edilebilir; eval davranışı ölçer.

## Web neden deterministik?

Web arayüzünün görevi bellidir: yüklenen dosyayı `log_analyzer` tool'una verip
sonucu göstermek. Bu seçim için LLM kullanmak maliyet ve belirsizlik ekler,
fakat değer katmaz.

Bu nedenle web akışı `SecurityLogDecisionMaker` kullanır. `LLMDecisionMaker`
ayrı bir entegrasyon sınırı olarak hazırdır ve belirsiz doğal dil hedeflerinin
yorumlanması gereken daha sonraki kullanım senaryolarında enjekte edilebilir.

## Sağlayıcı adapter'ı eklemek

Haricî bir LLM bağlamak için gereken minimum sözleşme:

```python
class ProviderModel:
    def generate(self, prompt: str) -> str:
        # Sağlayıcı çağrısını yap ve yalnızca model metnini döndür.
        ...
```

Adapter; timeout, authentication ve sağlayıcıya özgü hataları kendi sınırında
yönetmelidir. API anahtarları source code'a veya Git geçmişine yazılmamalıdır.

## Tasarımın bilinçli sınırları

Bu sürümde şunlar yoktur:

- kalıcı database memory,
- vector search veya RAG,
- model sağlayıcısına gömülü bağımlılık,
- otonom shell veya filesystem tool'u,
- multi-agent koordinasyonu.

Bu eksiklik değil, kapsam kontrolüdür. Amaç güvenli ve anlaşılabilir bir agent
çekirdeğini tamamlamaktır.
