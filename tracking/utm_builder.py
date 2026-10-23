"""
UTM Builder Module.
Standardizes campaign attribution across all channels, personas, and experiments.
Feeds data back into the statistical feedback loop in Supabase.
"""

from datetime import datetime
import urllib.parse

def build_tracked_url(base_url: str, channel: str, persona_name: str, topic_slug: str = "") -> dict:
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    slug_part = f"_{topic_slug[:15]}" if topic_slug else ""
    utm_tag = f"{channel}_{stamp}{slug_part}"
    
    params = {
        "utm_source": channel,
        "utm_medium": "agent_autonomous",
        "utm_campaign": utm_tag,
        "persona": persona_name
    }
    
    delimiter = "&" if "?" in base_url else "?"
    full_url = f"{base_url}{delimiter}{urllib.parse.urlencode(params)}"
    
    return {
        "tracked_url": full_url,
        "utm_tag": utm_tag,
        "params": params
    }

if __name__ == "__main__":
    t = build_tracked_url("https://twoja-domena.pl/artykul", "x", "analityk_danych", "ai-agents")
    print("Wygenerowany link UTM:")
    print(t["tracked_url"])
