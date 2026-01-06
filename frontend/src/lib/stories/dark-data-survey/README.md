# Dark Data Survey - "A Taste for Privacy"

An interactive data story exploring how privacy preferences vary across demographics and institutional contexts, based on survey data from University of Vermont undergraduate students.

## Story Overview

**Title:** A Taste for Privacy
**Subtitle:** When do people give up their privacy?
**Authors:** Jonathan St-Onge, Juniper Lovato
**Date:** Aug 15, 2025

### Research Question

The story investigates how young people's willingness to share personally identifiable information (PII) varies across different institutions and relationships. It introduces the concept of **privacy construal** - the idea that comfort with sharing data depends on the perceived distance from oneself.

### Key Findings

From 416 survey responses collected in January 2023:

1. **Social Media Privacy Settings**: Most college students set their accounts to private, followed by mixed, then public. More social media use correlates with less private settings.

2. **Platform Trust Paradox**: Single-platform users are less trusting of institutions than average. Users of 4+ platforms trust social media companies with their PII more than police or even neighbors.

3. **Demographic Disparities**:
   - Sexual orientation significantly impacts institutional trust (e.g., bisexual respondents rate police trust almost one scale point lower than straight respondents)
   - Privacy preferences vary by gender, race, and other demographic factors

4. **Circles of Trust**: The story visualizes "circles of trust" showing relative comfort levels sharing PII with different institutions (relatives, government, police, social media platforms, etc.)

### Survey Questions

The story includes both inline survey questions and collected the following data points:

- Social media privacy settings (private/mixed/public)
- Social media platforms used (Twitter, Instagram, Facebook, TikTok, Other)
- Comfort sharing PII with:
  - Relatives (7-point Likert scale)
  - Government (7-point Likert scale)
  - Police (7-point Likert scale)
- Demographics: age, gender, sexual orientation, race

## Technical Implementation

This is an experimental project demonstrating:

1. **Participatory visual essays** - Survey responses dynamically update the data visualizations
2. **Working with sensitive data** - Privacy-conscious data collection and storage

### Architecture

**Frontend:**
- Browser fingerprinting for anonymous user identification (no PII required)
- Reactive survey forms using Svelte 5 runes (`$state`, `$derived`)
- Scrollytelling interface mixing narrative content with interactive questions
- Real-time data visualization updates

**Backend:**
- FastAPI endpoints for survey data persistence
- PostgreSQL database with SQLAlchemy ORM
- Rate limiting (30 requests/minute per IP) via slowapi
- Field validation for numeric ranges (Likert scales, demographics)
- Pydantic response models for API documentation

**Data Flow:**
1. User loads story → generates browser fingerprint
2. User answers questions → saves to backend via `/dark-data-survey/answer` or `/dark-data-survey/upsert`
3. Backend validates and stores responses in `dark_data_survey` table
4. Story visualizations query aggregate data to update circles of trust

### Reusable Survey Infrastructure

This story demonstrates reusable patterns now available in `$lib/components/survey/`:

- `SurveyScrolly.svelte` - Generic survey scrollytelling component
- `SurveyQuestion.svelte` - Question wrapper with answer persistence
- `SurveyQuestion.Radio.svelte` - Radio button questions
- `SurveyQuestion.Checkbox.svelte` - Multi-select checkbox questions

See the story's [Index.svelte](components/Index.svelte) for implementation details, particularly the `createSaveAnswerHandler` pattern for mapping survey fields to API calls.

## File Structure

```
dark-data-survey/
├── README.md                           # This file
├── components/
│   ├── Index.svelte                    # Main story component
│   ├── ConsentPopup.svelte            # Initial consent dialog
│   ├── Dashboard.svelte               # Data visualization dashboard
│   ├── TrustEvo.svelte               # "Circles of trust" visualization
│   └── Survey.DemographicsBox.svelte # Demographics collection form
├── data/
│   ├── copy.json                      # Story content and survey questions
│   └── data.remote.js                 # API client functions
└── lib/
    └── meta.js                        # Story metadata
```

## Database Schema

See [backend/app/models/dark_data_survey.py](../../../../backend/app/models/dark_data_survey.py) for the complete schema. Key fields:

- `fingerprint` (String, unique, indexed) - Browser fingerprint for anonymous identification
- Likert scale fields (Integer 1-7): `relativePreferences`, `govPreferences`, `polPreferences`
- Demographic fields (Integer): `gender_ord`, `orientation_ord`, `race_ord`
- Text fields: `platformMatters`, `age`
- `created_at` (DateTime) - Response timestamp

## Development Notes

### Adding New Survey Questions

1. Add question definition to [data/copy.json](data/copy.json)
2. Add field to `surveyAnswers` state in [components/Index.svelte](components/Index.svelte)
3. Add field mapping in `createSaveAnswerHandler` function
4. Add column to `DarkDataSurvey` model in backend
5. Add validation rules if needed in [backend/app/routers/dark_data_survey.py](../../../../backend/app/routers/dark_data_survey.py)

### Privacy Considerations

**GDPR/CCPA Compliance:**
- Browser fingerprint is **only generated after explicit user consent**
- If user declines consent, no fingerprinting occurs and no data is tracked
- Consent decision is recorded in the database for transparency

**Data Protection:**
- Uses browser fingerprinting instead of requiring login/email
- Fingerprints are hashed and not reversible to individual users
- No PII collected beyond what users explicitly provide in demographics

**Security Measures:**
- Rate limiting prevents abuse (30 requests/minute per IP)
- Backend validation prevents malicious data injection
- Numeric field range validation ensures data integrity
