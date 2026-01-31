---
name: criminal-activity-analysis
description: "MUST USE when user asks about: safety of locations, crime statistics, danger levels, criminality, or 'is [place] safe?' for Brazil/Sao Paulo. Provides REAL crime data via API."
homepage: http://thomas:11004/api/v1
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"], "env": ["CRIMINAL_ANALYSIS_API_KEY"] },
        "primaryEnv": "CRIMINAL_ANALYSIS_API_KEY",
      },
  }
---

# Criminal Activity Analysis

Analyze safety levels for locations in Sao Paulo state, Brazil using real criminal activity data.

## When to Use This Skill

**ALWAYS use this skill when the user asks about:**
- Safety of a location (e.g., "Is [place] safe?", "How safe is [address]?")
- Crime or criminality at a location
- Danger levels or risk assessment for places in Brazil
- Criminal activity analysis for any Brazilian location

## Quick Start

Run the analysis script with the location:

```bash
python3 /app/skills/criminal-activity-analysis/analyze.py "LOCATION_HERE"
```

### Example

```bash
python3 /app/skills/criminal-activity-analysis/analyze.py "Praca da Republica Sao Paulo"
```

## Output Format

The script returns JSON with this structure:

```json
{
  "success": true,
  "location": {
    "query": "Praca da Republica Sao Paulo",
    "coordinates": [-46.6429, -23.5432],
    "latitude": -23.5432,
    "longitude": -46.6429
  },
  "analysis": {
    "overallRisk": "high",
    "overallRiskLabel": "HIGH",
    "highestRiskPeriod": "morning",
    "periods": [
      {"period": "dawn", "score": 45000, "position": 5, "riskLevel": "medium", "riskLabel": "MEDIUM"},
      {"period": "morning", "score": 152300, "position": 1, "riskLevel": "high", "riskLabel": "HIGH"},
      {"period": "afternoon", "score": 89000, "position": 3, "riskLevel": "medium", "riskLabel": "MEDIUM"},
      {"period": "night", "score": 245000, "position": 2, "riskLevel": "high", "riskLabel": "HIGH"}
    ]
  },
  "topCrimes": [
    {"id": 497, "name": "Furto - Loss", "severity": 5, "count": 1858},
    {"id": 319, "name": "Roubo - Outros", "severity": 8, "count": 1468}
  ],
  "recommendations": [
    "Keep mobile phones and valuables concealed",
    "Stay alert on public transportation"
  ]
}
```

## Presenting Results

Format the JSON response for the user like this:

```
Safety Analysis: {location.query}

Overall Assessment: {analysis.overallRiskLabel} Risk Area
Highest risk during {analysis.highestRiskPeriod} period.

Time Period Analysis:
| Period | Risk | Position | Score |
|--------|------|----------|-------|
| Dawn | {riskLabel} | #{position} | {score} |
| Morning | {riskLabel} | #{position} | {score} |
| Afternoon | {riskLabel} | #{position} | {score} |
| Night | {riskLabel} | #{position} | {score} |

Most Common Crimes:
1. {name} - {count} occurrences
2. {name} - {count} occurrences
...

Recommendations:
- {recommendation}
- {recommendation}
```

## Error Handling

If the script fails, the output will be:
```json
{"success": false, "error": "error_type", "message": "error description"}
```

Handle errors appropriately:
- configuration_error: API key not set
- api_error: Network or API issue
- unexpected_error: Other errors
