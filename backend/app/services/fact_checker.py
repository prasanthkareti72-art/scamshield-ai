"""
ScamShield AI - Fact-Checking Verification Service
Integrates accredited debunking repositories (PIB Fact Check, Snopes, BoomLive, AltNews)
and Google Fact Check Tools API. Strictly distinguishes ML estimates from verified facts.
"""

import requests
import re
from datetime import datetime

# Curated reference database of verified debunks by accredited fact-checking organizations
VERIFIED_FACT_CHECK_ARCHIVE = [
    {
        "claim": "UNESCO declared the Indian national anthem as the best in the world",
        "keywords": ["unesco", "national anthem", "best anthem"],
        "verdict": "FALSE (Recurrent Hoax)",
        "source": "PIB Fact Check & BoomLive",
        "reference_url": "https://www.boomlive.in/unesco-declared-jana-gana-mana-best-national-anthem-fact-check",
        "summary": "UNESCO never declared any national anthem as the 'best in the world'. This is a persistent viral fabrication circulating since 2008."
    },
    {
        "claim": "NASA confirmed Earth will plunge into 6 days of darkness due to solar storm",
        "keywords": ["nasa", "earth", "darkness", "solar storm", "candles"],
        "verdict": "FALSE (Viral Hoax)",
        "source": "Snopes & NASA Science",
        "reference_url": "https://www.snopes.com/fact-check/solar-storm-blackout/",
        "summary": "NASA has repeatedly confirmed no solar storm can block all sunlight to cause multi-day worldwide darkness. Originates from a satirical news site."
    },
    {
        "claim": "RBI has decided to withdraw or invalidate all 500 rupee currency notes",
        "keywords": ["rbi", "500", "notes", "invalidate", "demonetization"],
        "verdict": "FALSE",
        "source": "PIB Fact Check",
        "reference_url": "https://twitter.com/PIBFactCheck",
        "summary": "The Reserve Bank of India has not issued any notification withdrawing ₹500 currency notes. The viral circular is forged."
    },
    {
        "claim": "WhatsApp will become paid unless you forward this message to contacts",
        "keywords": ["whatsapp", "become paid", "forward to 10", "forward to 20", "whatsapp gold"],
        "verdict": "FALSE (Viral Forward Scam)",
        "source": "AltNews & WhatsApp Official",
        "reference_url": "https://www.altnews.in/whatsapp-gold-message-hoax/",
        "summary": "WhatsApp is completely free. WhatsApp does not track forwarded chain messages to determine active users. Forwarding will not change account status."
    },
    {
        "claim": "Drinking boiled garlic and lemon water cures all respiratory viruses and covid",
        "keywords": ["boiled garlic", "lemon water", "cure", "respiratory", "immune"],
        "verdict": "FALSE (Dangerous Medical Misinformation)",
        "source": "World Health Organization (WHO) Mythbusters",
        "reference_url": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters",
        "summary": "While garlic is a healthy food, there is zero clinical evidence that eating or boiling garlic cures respiratory infections or viral diseases."
    },
    {
        "claim": "Government distributing free laptops and solar panels to all students via survey link",
        "keywords": ["free laptops", "solar panels", "students", "subsidy", "survey form"],
        "verdict": "FALSE (Phishing Scam)",
        "source": "PIB Fact Check",
        "reference_url": "https://pib.gov.in/FactcheckDetails.aspx",
        "summary": "The central government does not run any such scheme distributing free laptops via unofficial third-party survey forms. Links are credential phishing."
    },
    {
        "claim": "Drinking cold water after meals causes immediate cancer by solidifying oil",
        "keywords": ["cold water", "cancer", "solidifies", "sludge", "intestines"],
        "verdict": "FALSE (Medical Hoax)",
        "source": "Health Journal & Snopes",
        "reference_url": "https://www.snopes.com/fact-check/cold-water-cancer/",
        "summary": "Water ingested quickly reaches body temperature. There is no physiological or biological mechanism connecting cold drinking water to intestine cancer."
    }
]

class FactChecker:
    @staticmethod
    def query_live_google_fact_check(query_text: str, api_key: str) -> dict | None:
        """Queries Google ClaimReview Fact Check Tools API if an API key is provided."""
        if not api_key or not query_text:
            return None
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "query": query_text[:200],
                "key": api_key,
                "languageCode": "en"
            }
            resp = requests.get(url, params=params, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                claims = data.get("claims", [])
                if claims:
                    first = claims[0]
                    reviews = first.get("claimReview", [{}])[0]
                    return {
                        "verified_match": True,
                        "source": reviews.get("publisher", {}).get("name", "Google Fact Check"),
                        "verdict": reviews.get("textualRating", "Unverified"),
                        "claim_reviewed": first.get("text", query_text),
                        "reference_url": reviews.get("url", ""),
                        "summary": f"Reviewed by {reviews.get('publisher', {}).get('name')}: {reviews.get('textualRating')}"
                    }
        except Exception:
            pass
        return None

    @staticmethod
    def match_verified_database(text: str) -> dict | None:
        """Checks for keyword similarity against known debunked viral stories."""
        if not text:
            return None
        text_lower = text.lower()

        for item in VERIFIED_FACT_CHECK_ARCHIVE:
            # Check how many keywords match
            matches = [kw for kw in item["keywords"] if kw in text_lower]
            # If at least 2 distinct keywords match (or all keywords if only 2 exist)
            if len(matches) >= 2 or (len(item["keywords"]) == 1 and len(matches) == 1):
                return {
                    "verified_match": True,
                    "source": item["source"],
                    "verdict": item["verdict"],
                    "claim_reviewed": item["claim"],
                    "reference_url": item["reference_url"],
                    "summary": item["summary"]
                }
        return None

    @staticmethod
    def verify_claim(text: str, api_key: str = "") -> dict:
        """
        Conducts factual verification.
        Returns verifiable findings or a clear, transparent 'No Verified Match' statement.
        """
        # 1. Check live Google Fact Check API if configured
        if api_key:
            live_result = FactChecker.query_live_google_fact_check(text, api_key)
            if live_result:
                return live_result

        # 2. Check local curated verified archive
        local_result = FactChecker.match_verified_database(text)
        if local_result:
            return local_result

        # 3. Transparent Fallback: No verified match found
        return {
            "verified_match": False,
            "source": "None",
            "verdict": "Unverified via Fact-Check Databases",
            "claim_reviewed": None,
            "reference_url": None,
            "summary": "No matching record found in accredited fact-checking databases. Assessment relies solely on machine learning linguistic models and rule-based scam indicators."
        }
