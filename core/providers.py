PROVIDERS = {
    "Gemini": {
        "key_field": "gemini_key",
        "label": "Google Gemini",
        "placeholder": "AIza...",
        "endpoint": None,
        "models": [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemma-4-26b-a4b-it",
            "gemma-4-31b-it",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash-image",
            "gemini-3.1-flash-lite",
            "gemini-3-pro-image",
            "gemini-3.1-flash-image",
            "gemini-3.1-flash-lite-image",
            "gemini-nano-banana-2.1",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-omni-flash-preview",
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-3.8-flash",
            "gemini-4-argon",
            "gemini-4-carbon",
            "gemini-4-hydrogen",
            "gemini-4-neon",
            "antigravity-preview-05-2026",
            "antigravity-preview-09-2026",
            "antigravity-preview-latest",
            "deep-research-max-preview-04-2026",
            "deep-research-preview-04-2026",
        ],
    },
    "OpenRouter": {
        "key_field": "openrouter_key",
        "label": "OpenRouter",
        "placeholder": "sk-or-...",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "models": [
            "inclusionai/ling-3.2-flash:free",
            "baidu/ernie-5.5-flash-preview:free",
            "liquid/lfm-3-1.7b:free",
            "particle-ai/particle-1:free",
            "recursive/flint-v1.0:free",
            "nvidia/nemotron-3.5-super-vl:free",
            "nvidia/nemotron-3.5-lightning:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "google/gemma-4-26b-a4b-it:free",
            "google/gemma-4-31b-it:free",
        ],
    },
    "Groq": {
        "key_field": "groq_key",
        "label": "Groq",
        "placeholder": "gsk_...",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "models": [
            "meta-llama/llama-prompt-guard-2-86m",
            "canopylabs/orpheus-arabic-saudi",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "allam-2-7b",
            "whisper-large-v3-turbo",
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-safeguard-20b",
            "canopylabs/orpheus-v1-english",
            "meta-llama/llama-prompt-guard-2-22m",
            "whisper-large-v3",
        ],
    },
    "Cerebras": {
        "key_field": "cerebras_key",
        "label": "Cerebras",
        "placeholder": "csk-...",
        "endpoint": "https://api.cerebras.ai/v1/chat/completions",
        "models": [
            "gpt-oss-120b",
            "qwen-3.8-27b",
        ],
    },
    "SambaNova": {
        "key_field": "sambanova_key",
        "label": "SambaNova Cloud",
        "placeholder": "SambaNova API Key...",
        "endpoint": "https://api.sambanova.ai/v1/chat/completions",
        "models": [
            "GLM-5.3",
            "MiniMax-M3.1-Flash",
            "gemma-4-31B-it",
            "gpt-oss-120b",
        ],
    },
    "NVIDIA NIM": {
        "key_field": "nvidia_key",
        "label": "NVIDIA NIM",
        "placeholder": "nvapi-...",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "models": [
            "bigcode/starcoder2-15b",
            "fastino/gliner2-pii",
            "google/gemma-3-12b-it",
            "google/gemma-3-4b-it",
            "google/gemma-4-31b-it",
            "meta/muse-glimmer-30b",
            "minimaxai/minimax-m3.1-flash",
            "mistralai/mistral-large-4-1t-a52b",
            "moonshotai/kimi-k3.1-pro",
            "nvidia/ai-synthetic-video-detector",
            "nvidia/cosmos-reason2-8b",
            "nvidia/embed-qa-4",
            "nvidia/ising-calibration-1.5-31b",
            "nvidia/llama-3.1-nemoguard-8b-topic-control",
            "nvidia/llama-3.1-nemotron-safety-guard-8b-v3",
            "nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1",
            "nvidia/llama-3.2-nv-embedqa-1b-v1",
            "nvidia/nemotron-3-embed-1b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3.5-bolt-e4b",
            "nvidia/nemotron-3.5-content-safety",
            "nvidia/nemotron-3.5-embed-1b",
            "nvidia/nemotron-3.5-embed-8b",
            "nvidia/nemotron-3.5-lightning-30b-a3b",
        ],
    },
}

THINKING_BUDGETS = {
    "off": 0,
    "low": 1024,
    "medium": 4096,
    "high": 8192,
    "max": 24576,
}

def get_model_info(model_id: str, lang: str = "en") -> str:
    m = model_id.lower()
    is_tr = (lang == "tr")

    if "whisper" in m:
        return "Ses-metin (STT) modeli. Standart metin sohbeti için uygun değil." if is_tr else "Speech-to-text (STT) model. Not for text chat."
    if "orpheus" in m:
        return "Metin-ses (TTS) modeli. Standart metin sohbeti için uygun değil." if is_tr else "Text-to-speech (TTS) model. Not for text chat."
    if "embed" in m or "retriever" in m:
        return "Vektör/embedding modeli (arama ve RAG için). Sohbet yanıtı üretmez." if is_tr else "Embedding model for search and RAG. Does not generate chat replies."
    if any(k in m for k in ("guard", "safety", "pii", "detector", "calibration")):
        return "Güvenlik filtresi veya sınıflandırma modeli. Genel sohbet için değil." if is_tr else "Safety filter or specialized classifier. Not for general chat."
    if "image" in m or "nano-banana" in m:
        return "Görsel üretim ve düzenleme odaklı model." if is_tr else "Built for image generation and editing."
    if "deep-research" in m:
        return "Uzun soluklu araştırma, kaynak sentezi ve detaylı raporlama." if is_tr else "Long-form research, synthesis, and detailed reports."
    if "starcoder" in m:
        return "Kod tamamlama ve yazılım geliştirme odaklı model." if is_tr else "Focused on code completion and programming."
    if "reasoning" in m or "reason" in m:
        return "Adım adım mantık yürütme, matematik ve karmaşık problem çözme." if is_tr else "Step-by-step reasoning, math, and complex problem solving."
    if "vl" in m or "omni" in m:
        return "Çok modlu (metin + görsel) anlama ve genel asistanlık." if is_tr else "Multimodal (text + vision) understanding and general tasks."
    if any(k in m for k in ("ultra", "large", "pro", "120b", "argon", "carbon")):
        return "Yüksek kapasiteli model. Karmaşık kodlama, mimari ve derin analiz için." if is_tr else "High-capacity model for complex coding, architecture, and deep analysis."
    if any(k in m for k in ("lite", "flash", "lightning", "bolt", "1.7b", "4b", "7b", "8b")):
        return "Hızlı ve düşük gecikmeli model. Günlük sohbet ve hızlı kod düzenlemeleri için." if is_tr else "Fast, low-latency model for everyday chat and quick edits."
    return "Genel amaçlı sohbet, metin yazımı ve kodlama modeli." if is_tr else "General-purpose chat, writing, and coding model."