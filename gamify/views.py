# gamify/views.py
import os
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import requests

@require_http_methods(["GET"])
def chatbot_api(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"reply":"Ask something."})

    # If you provided OPENAI_API_KEY in settings, proxy request
    OPENAI_KEY = getattr(settings, "OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
    if OPENAI_KEY:
        try:
            # Lightweight OpenAI chat completion using v1/chat/completions
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role":"user","content": q}],
                "max_tokens": 600,
                "temperature": 0.2
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            data = resp.json()
            # safely extract
            reply = data.get("choices",[{}])[0].get("message",{}).get("content")
            if not reply:
                reply = data.get("error", {}).get("message", "No reply")
            return JsonResponse({"reply": reply})
        except Exception as e:
            # fallback to offline
            pass

    # Offline fallback: search local terms from content (very basic)
    qlow = q.lower()
    # simple rule-based responses
    if "hello" in qlow or "hi" in qlow:
        return JsonResponse({"reply":"Hello! Ask about a subject, lesson or topic. Example: 'explain topic capacitor'."})
    if qlow.startswith("translate to "):
        # example: translate to hi book
        parts = qlow.split()
        if len(parts) >= 3:
            lang = parts[2]
            word = " ".join(parts[3:])
            # very small offline dictionary:
            DICT = {
                "book": {"hi": "पुस्तक", "od":"ପୁସ୍ତକ", "mr":"पुस्तक"}
            }
            entry = DICT.get(word, {})
            return JsonResponse({"reply": entry.get(lang, f"No offline translation for '{word}' to {lang}")})
    # try to answer about electricity/capacitor from a small hardcoded set
    if "electricity" in qlow:
        return JsonResponse({"reply": "Electricity is the set of physical phenomena associated with presence and motion of electric charge. (offline fallback summary)"})
    if "capacitor" in qlow:
        return JsonResponse({"reply": "A capacitor stores electrical energy in an electric field, typically two conductors separated by an insulator."})

    return JsonResponse({"reply":"I couldn't find an exact match offline. Try: 'explain topic <name>' or use online mode by setting OPENAI_API_KEY in settings."})
