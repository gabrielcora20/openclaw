---
name: criminal-activity-analysis
description: "MUST USE when user asks about: safety of locations, crime statistics, danger levels, criminality, or 'is [place] safe?' for Brazil/São Paulo. Provides REAL crime data via API - do NOT give generic safety advice without reading this skill first."
homepage: http://thomas:11004/api/v1
metadata:
  {
    "openclaw":
      {
        "emoji": "🚨",
        "requires": { "bins": ["curl"], "env": ["CRIMINAL_ANALYSIS_API_KEY"] },
        "primaryEnv": "CRIMINAL_ANALYSIS_API_KEY",
      },
  }
---

# Criminal Activity Analysis

Analyze safety levels for locations in São Paulo state, Brazil using real criminal activity data.

## When to Use This Skill

**ALWAYS use this skill when the user asks about:**
- Safety of a location (e.g., "Is [place] safe?", "How safe is [address]?")
- Crime or criminality at a location (e.g., "crime at [place]", "criminality on [address]")
- Danger levels or risk assessment for places in Brazil
- Criminal activity analysis for any Brazilian location
- Security concerns about neighborhoods, streets, or addresses in São Paulo

**Trigger phrases include:**
- "safe", "safety", "secure", "security"
- "crime", "criminal", "criminality", "dangerous", "danger"
- "risk", "risky", "theft", "robbery", "assault"
- Any location query mentioning Brazil, São Paulo, SP, or Brazilian addresses

**Important:** This skill provides REAL crime data for São Paulo state. Do NOT give generic safety advice - use this API to get actual statistics.

## Configuration

Set the API key in your environment:

```bash
export CRIMINAL_ANALYSIS_API_KEY="your-api-key"
```

## Quick Start

### 1. Analyze a Location

```bash
curl -s -X POST "http://thomas:11004/api/v1/criminal/activity-analysis/analyze" \
  -H "X-API-KEY: ${CRIMINAL_ANALYSIS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "praca da republica"
```

### 2. Get Crime Type Description

```bash
curl -s "http://thomas:11004/api/v1/criminal/types/492" \
  -H "Accept: application/json" \
  -H "X-API-KEY: ${CRIMINAL_ANALYSIS_API_KEY}"
```

## Response Processing

The analysis API returns crime data for 4 time periods: `dawn`, `morning`, `afternoon`, `night`.

Each period contains:
- `score` - Danger score for the zone
- `scorePosition` - Ranking position in São Paulo state (lower = more dangerous)
- `occurrencesWithinCriminalDangerZones` - Array of crime types with occurrence counts

## Risk Classification

Use these maximum scores per period to calculate risk thresholds:

| Period | Max Score | High (>70%) | Medium (30-70%) |
|--------|-----------|-------------|-----------------|
| Dawn | 128,000 | > 89,600 | 38,400 - 89,600 |
| Morning | 185,000 | > 129,500 | 55,500 - 129,500 |
| Afternoon | 165,000 | > 115,500 | 49,500 - 115,500 |
| Night | 300,000 | > 210,000 | 90,000 - 210,000 |

### Classification Logic

```
score > maxScore * 0.70 → 🔴 HIGH RISK
score > maxScore * 0.30 → 🟠 MEDIUM RISK
score <= maxScore * 0.30 → 🟢 LOW RISK
```

### Risk Level Messages

- **HIGH RISK**: "This zone ranks #{position} most dangerous in São Paulo state during {period}. Exercise extreme caution."
- **MEDIUM RISK**: "This zone has moderate risk during {period}, ranking #{position}. Exercise caution."
- **LOW RISK**: "This zone is relatively safe during {period}, ranking #{position}."

## Output Format

When a user asks about safety of a location, respond with:

```
📍 Safety Analysis: {location}

{risk_emoji} Overall Assessment: {risk_level} Risk Area
{risk_description based on highest risk period}

🕐 Time Period Analysis:
| Period | Risk | Position | Score |
|--------|------|----------|-------|
| Dawn | {emoji} | #{pos} | {score} |
| Morning | {emoji} | #{pos} | {score} |
| Afternoon | {emoji} | #{pos} | {score} |
| Night | {emoji} | #{pos} | {score} |

📊 Most Common Crimes ({highest_risk_period}):
1. {crime_description} - {count} occurrences
2. {crime_description} - {count} occurrences
...

💡 Recommendations:
- {recommendation based on crime types}
- {recommendation based on safe periods}
```

## Common Crime Types

Fetch descriptions for the top crime types using the crime types API. Common IDs:

| ID | Description |
|----|-------------|
| 497 | Theft (Art. 155) |
| 319 | Robbery - Other |
| 322 | Robbery - Pedestrian |
| 494 | Cell Phone Robbery |
| 323 | Public Transport Robbery |
| 492 | Robbery - Inside Public Transport |
| 317 | Theft - Pedestrian |
| 316 | Theft - Commercial |
| 315 | Theft - Vehicle |

## Generating Recommendations

Based on prevalent crime types, suggest:

- **Cell phone/theft crimes**: Keep valuables concealed, avoid displaying phones
- **Public transport crimes**: Stay alert on buses/metro, keep bags secure
- **Vehicle crimes**: Park in well-lit areas, don't leave valuables visible
- **General**: Consider visiting during {lowest_risk_period} when risk is lower

## Error Handling

If the API returns an error or no data:
- Network error: "Unable to connect to the criminal analysis service. Please try again."
- Invalid location: "Could not find the specified location. Please try a more specific address."
- No data: "No criminal activity data available for this location."

## Example Conversation

**User**: "Is Praça da República safe?"

**Agent**:
> 📍 **Safety Analysis: Praça da República, São Paulo**
>
> 🔴 **Overall Assessment: High Risk Area**
> This zone ranks #1 most dangerous in São Paulo state during morning hours. Exercise extreme caution.
>
> 🕐 **Time Period Analysis:**
> | Period | Risk | Position | Score |
> |--------|------|----------|-------|
> | Dawn | 🟠 Medium | #5 | 45,000 |
> | Morning | 🔴 High | #1 | 152,300 |
> | Afternoon | 🟠 Medium | #3 | 89,000 |
> | Night | 🔴 High | #2 | 245,000 |
>
> 📊 **Most Common Crimes (Morning):**
> 1. Theft (Art. 155) - 1,858 occurrences
> 2. Robbery - Other - 1,468 occurrences
> 3. Cell Phone Robbery - 700 occurrences
> 4. Public Transport Robbery - 598 occurrences
> 5. Theft - Pedestrian - 380 occurrences
>
> 💡 **Recommendations:**
> - Keep mobile phones and valuables concealed
> - Stay alert in crowded areas, especially near transit
> - Consider visiting during dawn when risk is lower
> - Avoid displaying expensive items like jewelry or watches
