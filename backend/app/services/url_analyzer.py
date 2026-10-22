"""
ScamShield AI - URL & Domain Safety Analyzer
Evaluates links for phishing indicators, deceptive subdomains, suspicious TLDs, IP hosts, and shorteners.
"""

import re
from urllib.parse import urlparse
import ipaddress

# Trusted official domains
OFFICIAL_TRUSTED_DOMAINS = {
    "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com", "axisbank.com",
    "paypal.com", "amazon.in", "amazon.com", "flipkart.com", "google.com",
    "apple.com", "microsoft.com", "whatsapp.com", "telegram.org", "pib.gov.in",
    "india.gov.in", "rbi.org.in", "incometax.gov.in", "uidai.gov.in"
}

# Suspicious Top-Level Domains (TLDs) frequently abused in fast-flux phishing campaigns
SUSPICIOUS_TLDS = {
    ".top", ".xyz", ".buzz", ".cc", ".pw", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".work", ".click", ".link", ".icu", ".monster", ".site", ".live", ".fit",
    ".club", ".biz", ".country", ".stream", ".download", ".racing", ".vip"
}

# URL Shorteners that conceal the actual destination
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "is.gd", "t.co", "cutt.ly", "rb.gy", "rebrand.ly",
    "ow.ly", "buff.ly", "shorturl.at", "tiny.cc", "soo.gd", "v.gd"
}

# Brands frequently targeted by spear-phishing & credential harvesters
TARGETED_BRANDS = [
    "sbi", "onlinesbi", "hdfc", "icici", "axis", "kotak", "pnb", "bob",
    "paytm", "phonepe", "gpay", "googlepay", "bhim",
    "amazon", "flipkart", "meesho", "myntra",
    "paypal", "netflix", "apple", "microsoft", "chase", "wellsfargo",
    "whatsapp", "telegram", "facebook", "instagram", "indiapost", "fedex", "dhl"
]

class URLAnalyzer:
    @staticmethod
    def is_ip_address(host: str) -> bool:
        """Checks if hostname is a raw IPv4 or IPv6 address."""
        if not host:
            return False
        # Strip port if present
        host_clean = host.split(":")[0]
        try:
            ipaddress.ip_address(host_clean)
            return True
        except ValueError:
            return False

    @staticmethod
    def analyze_single_url(url_str: str) -> dict:
        """Performs comprehensive multi-factor security evaluation of a single URL."""
        if not url_str.startswith(("http://", "https://")):
            url_str = "http://" + url_str
            
        parsed = urlparse(url_str)
        hostname = (parsed.hostname or "").lower()
        path = parsed.path.lower()
        full_url_lower = url_str.lower()
        
        indicators = []
        url_risk = 0.0
        is_safe = False
        
        # 1. Scheme Check
        is_https = parsed.scheme == "https"
        if not is_https:
            indicators.append("Insecure HTTP protocol (no SSL/TLS encryption)")
            url_risk += 15.0

        # 2. Raw IP address check (Major Red Flag)
        is_ip = URLAnalyzer.is_ip_address(hostname)
        if is_ip:
            indicators.append(f"Direct IP-based URL ({hostname}) instead of registered domain name")
            url_risk += 45.0

        # 3. Shortener check
        is_shortener = hostname in URL_SHORTENERS
        if is_shortener:
            indicators.append(f"URL shortener ({hostname}) masking true destination")
            url_risk += 25.0

        # 4. Suspicious TLD check
        has_suspicious_tld = any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS)
        if has_suspicious_tld:
            matched_tld = next(tld for tld in SUSPICIOUS_TLDS if hostname.endswith(tld))
            indicators.append(f"High-risk Top-Level Domain ({matched_tld}) commonly used in phishing")
            url_risk += 35.0

        # 5. Punycode / Homograph attack check (e.g. xn--)
        if "xn--" in hostname:
            indicators.append("Punycode / Internationalized domain (possible homograph character spoofing)")
            url_risk += 40.0

        # 6. Brand Spoofing / Typosquatting Analysis
        spoofed_brand = None
        for brand in TARGETED_BRANDS:
            if brand in hostname:
                # Check if it's on the verified official domain whitelist
                is_official = any(hostname == off or hostname.endswith("." + off) for off in OFFICIAL_TRUSTED_DOMAINS)
                if not is_official:
                    spoofed_brand = brand
                    indicators.append(f"Deceptive domain impersonating brand '{brand.upper()}' without official domain ownership")
                    url_risk += 50.0
                    break

        # 7. Structural Anomaly: Excessive hyphens in domain
        hyphen_count = hostname.count("-")
        if hyphen_count >= 2:
            indicators.append(f"Multiple hyphens ({hyphen_count}) in domain name, typical of phishing disguise")
            url_risk += 20.0

        # 8. Suspicious Keywords in Path or Query
        phish_keywords = ["login", "signin", "verify", "update-kyc", "claim-reward", "free-gift", "secure", "banking", "pan-update"]
        matched_path_keywords = [kw for kw in phish_keywords if kw in path or kw in parsed.query.lower()]
        if matched_path_keywords and not is_safe:
            indicators.append(f"Credential harvesting keywords in URL path: {', '.join(matched_path_keywords)}")
            url_risk += 20.0

        # 9. Whitelist check: If official trusted domain with HTTPS, reset risk
        for trusted in OFFICIAL_TRUSTED_DOMAINS:
            if (hostname == trusted or hostname.endswith("." + trusted)) and is_https:
                is_safe = True
                url_risk = 0.0
                indicators = [f"Verified official domain for {trusted}"]
                break

        # Clamp risk score to 0 - 100
        final_score = min(100.0, max(0.0, url_risk))
        
        # Risk classification
        if final_score >= 70:
            verdict = "High-Risk Phishing Link"
        elif final_score >= 40:
            verdict = "Suspicious URL"
        elif final_score >= 20:
            verdict = "Caution Advised"
        else:
            verdict = "Likely Safe URL"

        return {
            "url": url_str,
            "hostname": hostname,
            "is_https": is_https,
            "is_ip": is_ip,
            "is_shortener": is_shortener,
            "is_trusted": is_safe,
            "spoofed_brand": spoofed_brand,
            "risk_score": round(final_score, 1),
            "verdict": verdict,
            "indicators": indicators
        }

    @staticmethod
    def analyze_urls(urls: list[str]) -> dict:
        """Analyzes a collection of URLs and aggregates the highest risk metrics."""
        if not urls:
            return {
                "has_urls": False,
                "count": 0,
                "highest_risk_score": 0.0,
                "overall_verdict": "No URLs Present",
                "detailed_results": [],
                "all_indicators": []
            }

        detailed = [URLAnalyzer.analyze_single_url(u) for u in urls]
        highest_risk = max(item["risk_score"] for item in detailed)
        
        all_inds = []
        for item in detailed:
            all_inds.extend(item["indicators"])

        # Determine overall verdict
        if highest_risk >= 70:
            verdict = "High-Risk Phishing Link Detected"
        elif highest_risk >= 40:
            verdict = "Suspicious URL Detected"
        elif highest_risk >= 20:
            verdict = "Unverified Link Present"
        else:
            verdict = "Known/Safe Link"

        return {
            "has_urls": True,
            "count": len(urls),
            "highest_risk_score": highest_risk,
            "overall_verdict": verdict,
            "detailed_results": detailed,
            "all_indicators": list(dict.fromkeys(all_inds))
        }
