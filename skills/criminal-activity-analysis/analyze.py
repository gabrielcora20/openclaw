#!/usr/bin/env python3
"""
Criminal Activity Analysis Script

Analyzes criminal activity for locations in Sao Paulo state, Brazil.
Calls the Thomas API and returns structured results with crime type names.

Usage:
    python analyze.py "Praca da Republica Sao Paulo"
    python analyze.py --help

Environment:
    CRIMINAL_ANALYSIS_API_KEY - Required API key for authentication
    CRIMINAL_ANALYSIS_API_URL - Optional base URL (default: http://thomas:11004)
"""

import argparse
import json
import os
import sys
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# Configuration
DEFAULT_API_URL = "http://thomas:11004"
TOP_CRIMES_LIMIT = 10

# Period max scores for risk calculation
PERIOD_MAX_SCORES = {
    "dawn": 128000.0,
    "afternoon": 165000.0,
    "morning": 185000.0,
    "night": 300000.0
}

# Cache for crime types (avoid repeated API calls)
CRIME_TYPE_CACHE: dict[int, dict] = {}


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("CRIMINAL_ANALYSIS_API_KEY")
    if not key:
        raise EnvironmentError("CRIMINAL_ANALYSIS_API_KEY environment variable is required")
    return key


def get_base_url() -> str:
    """Get API base URL from environment or use default."""
    return os.environ.get("CRIMINAL_ANALYSIS_API_URL", DEFAULT_API_URL)


def classify_risk(score: float, period: str) -> str:
    """Classify risk level based on score and period thresholds."""
    max_score = PERIOD_MAX_SCORES.get(period, 200000.0)
    high_threshold = max_score * 0.70
    medium_threshold = max_score * 0.30
    
    if score > high_threshold:
        return "high"
    elif score > medium_threshold:
        return "medium"
    else:
        return "low"


def get_risk_label(risk_level: str) -> str:
    """Get label for risk level."""
    return {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}.get(risk_level, "UNKNOWN")


def fetch_json(url: str, method: str = "GET", data: Optional[bytes] = None, 
               headers: Optional[dict] = None) -> dict:
    """Make HTTP request and return JSON response."""
    req = Request(url, data=data, method=method)
    req.add_header("X-API-KEY", get_api_key())
    req.add_header("Accept", "application/json")
    
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"API error {e.code}: {error_body}")
    except URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON response: {e}")


def get_crime_type(crime_type_id: int) -> dict:
    """Fetch crime type details by ID (with caching)."""
    if crime_type_id in CRIME_TYPE_CACHE:
        return CRIME_TYPE_CACHE[crime_type_id]
    
    base_url = get_base_url()
    url = f"{base_url}/api/v1/criminal/types/{crime_type_id}"
    
    try:
        result = fetch_json(url)
        CRIME_TYPE_CACHE[crime_type_id] = result
        return result
    except Exception:
        # Return a fallback if crime type lookup fails
        return {
            "id": crime_type_id,
            "description": f"Crime Type #{crime_type_id}",
            "score": 1
        }


def analyze_location(address: str) -> dict:
    """
    Analyze criminal activity for a location.
    
    Returns a structured object with:
    - location info (coordinates, query)
    - period analysis (score, position, risk level)
    - top crimes with names (not just IDs)
    - overall risk assessment
    """
    base_url = get_base_url()
    url = f"{base_url}/api/v1/criminal/activity-analysis/analyze"
    
    # Call the analysis API
    response = fetch_json(
        url,
        method="POST",
        data=address.encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    # Extract location info
    location = response.get("location", {})
    content = response.get("content", {})
    
    # Process each time period
    periods = []
    all_crimes: dict[int, int] = {}  # crime_type_id -> total count
    highest_risk_period = None
    highest_risk_score = -1
    
    for period_name in ["dawn", "morning", "afternoon", "night"]:
        period_data = content.get(period_name, {})
        score = period_data.get("score", 0)
        position = period_data.get("scorePosition", 0)
        risk_level = classify_risk(score, period_name)
        
        periods.append({
            "period": period_name,
            "score": score,
            "position": position,
            "riskLevel": risk_level,
            "riskLabel": get_risk_label(risk_level)
        })
        
        # Track highest risk period
        if score > highest_risk_score:
            highest_risk_score = score
            highest_risk_period = period_name
        
        # Aggregate crime occurrences
        occurrences = period_data.get("occurrencesWithinCriminalDangerZones", [])
        for occ in occurrences:
            crime_type = occ.get("crimeType", 0)
            count = occ.get("count", 0)
            all_crimes[crime_type] = all_crimes.get(crime_type, 0) + count
    
    # Get top crimes with names
    sorted_crimes = sorted(all_crimes.items(), key=lambda x: x[1], reverse=True)
    top_crimes = []
    
    for crime_id, count in sorted_crimes[:TOP_CRIMES_LIMIT]:
        crime_info = get_crime_type(crime_id)
        top_crimes.append({
            "id": crime_id,
            "name": crime_info.get("description", f"Crime #{crime_id}"),
            "severity": crime_info.get("score", 1),
            "count": count
        })
    
    # Determine overall risk (based on highest risk period)
    overall_risk = classify_risk(highest_risk_score, highest_risk_period) if highest_risk_period else "low"
    
    return {
        "success": True,
        "location": {
            "query": address,
            "coordinates": location.get("coordinates", [None, None]),
            "latitude": location.get("y"),
            "longitude": location.get("x")
        },
        "analysis": {
            "overallRisk": overall_risk,
            "overallRiskLabel": get_risk_label(overall_risk),
            "highestRiskPeriod": highest_risk_period,
            "periods": periods
        },
        "topCrimes": top_crimes
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze criminal activity for locations in Sao Paulo, Brazil",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python analyze.py "Praca da Republica Sao Paulo"
    python analyze.py "Av. Paulista 1000"
    python analyze.py --pretty "Largo do Arouche"

Environment Variables:
    CRIMINAL_ANALYSIS_API_KEY  Required API key
    CRIMINAL_ANALYSIS_API_URL  Base URL (default: http://thomas:11004)
        """
    )
    parser.add_argument("address", help="Location to analyze (address, landmark, or neighborhood)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    try:
        result = analyze_location(args.address)
        
        if args.pretty:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False))
        
        return 0
    
    except EnvironmentError as e:
        error_result = {"success": False, "error": "configuration_error", "message": str(e)}
        print(json.dumps(error_result), file=sys.stderr)
        return 1
    
    except RuntimeError as e:
        error_result = {"success": False, "error": "api_error", "message": str(e)}
        print(json.dumps(error_result), file=sys.stderr)
        return 1
    
    except Exception as e:
        error_result = {"success": False, "error": "unexpected_error", "message": str(e)}
        print(json.dumps(error_result), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
