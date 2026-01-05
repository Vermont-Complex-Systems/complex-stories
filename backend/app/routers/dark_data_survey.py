from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..core.database import get_db_session
from ..models.dark_data_survey import DarkDataSurvey, SurveyAnswerRequest, SurveyUpsertRequest, SurveyResponse, SurveyAnswerResponse

# Public router for survey responses
router = APIRouter()

# Initialize limiter for this router
limiter = Limiter(key_func=get_remote_address)

# Value to ordinal mapping (same as frontend)
# Valid database fields mapping to prevent injection via column names
FIELD_MAPPING = {
    'consent': DarkDataSurvey.consent,
    'socialMediaPrivacy': DarkDataSurvey.socialMediaPrivacy,
    'platformMatters': DarkDataSurvey.platformMatters,
    'institutionPreferences': DarkDataSurvey.institutionPreferences,
    'demographicsMatter': DarkDataSurvey.demographicsMatter,
    'relativePreferences': DarkDataSurvey.relativePreferences,
    'govPreferences': DarkDataSurvey.govPreferences,
    'polPreferences': DarkDataSurvey.polPreferences,
    'age': DarkDataSurvey.age,
    'gender_ord': DarkDataSurvey.gender_ord,
    'orientation_ord': DarkDataSurvey.orientation_ord,
    'race_ord': DarkDataSurvey.race_ord
}

VALUE_TO_ORDINAL = {
    'consent': {'accepted': 1, 'declined': 0},
    'socialMediaPrivacy': {'private': 1, 'mixed': 2, 'public': 3},
    'platformMatters': {'no': 1, 'sometimes': 2, 'yes': 3},
    'institutionPreferences': {'mostly-same': 1, 'depends-context': 2, 'vary-greatly': 3},
    'demographicsMatter': {'no': 1, 'somewhat': 2, 'yes': 3}
}

# Numeric field validation ranges (inclusive)
NUMERIC_FIELD_RANGES = {
    'relativePreferences': (1, 7),  # 7-point Likert scale
    'govPreferences': (1, 7),       # 7-point Likert scale
    'polPreferences': (1, 7),       # 7-point Likert scale
    'gender_ord': (0, 1),           # 0=Women, 1=Men
    'orientation_ord': (0, 3),      # 0=Straight, 1=Bisexual, 2=Gay, 3=Other
    'race_ord': (0, 2)              # 0=White, 1=Mixed, 2=POC
}

@router.post("/dark-data-survey/answer", response_model=SurveyAnswerResponse)
@limiter.limit("30/minute")  # Allow 30 submissions per minute per IP
async def post_answer(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Post a survey answer with value-to-ordinal conversion.

    Rate limit: 30 requests per minute per IP address.
    """

    # Parse and validate request body
    body = await request.json()
    survey_request = SurveyAnswerRequest(**body)

    # Validate fingerprint
    if not survey_request.fingerprint or survey_request.fingerprint.strip() == '':
        raise HTTPException(status_code=400, detail="Fingerprint is required")

    # Validate field and get ordinal value
    if survey_request.field not in VALUE_TO_ORDINAL:
        raise HTTPException(status_code=400, detail=f"Invalid field: {survey_request.field}")

    field_mapping = VALUE_TO_ORDINAL[survey_request.field]
    if survey_request.value not in field_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid value '{survey_request.value}' for field '{survey_request.field}'")

    ordinal_value = field_mapping[survey_request.value]

    try:
        # Use upsert functionality
        await upsert_answer(db, survey_request.fingerprint, survey_request.field, ordinal_value)
        return SurveyAnswerResponse(
            message=f"Saved {survey_request.field}: {survey_request.value} (ordinal: {ordinal_value})"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving answer: {str(e)}")


@router.post("/dark-data-survey/upsert", response_model=SurveyAnswerResponse)
@limiter.limit("30/minute")  # Allow 30 submissions per minute per IP
async def upsert_survey_answer(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Upsert a single survey answer by field.

    Rate limit: 30 requests per minute per IP address.
    """

    # Parse and validate request body
    body = await request.json()
    survey_request = SurveyUpsertRequest(**body)

    # Validate fingerprint
    if not survey_request.fingerprint or survey_request.fingerprint.strip() == '':
        raise HTTPException(status_code=400, detail="Fingerprint is required")

    # Validate field exists in the model
    if survey_request.field not in FIELD_MAPPING:
        raise HTTPException(status_code=400, detail=f"Invalid field: {survey_request.field}")

    # Validate numeric field ranges
    if survey_request.field in NUMERIC_FIELD_RANGES:
        min_val, max_val = NUMERIC_FIELD_RANGES[survey_request.field]
        try:
            numeric_value = int(survey_request.value)
            if not (min_val <= numeric_value <= max_val):
                raise HTTPException(
                    status_code=400,
                    detail=f"Value for {survey_request.field} must be between {min_val} and {max_val}, got {numeric_value}"
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Value for {survey_request.field} must be a valid integer"
            )

    try:
        await upsert_answer(db, survey_request.fingerprint, survey_request.field, survey_request.value)
        return SurveyAnswerResponse(
            message=f"Upserted {survey_request.field}: {survey_request.value}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error upserting answer: {str(e)}")


async def upsert_answer(db: AsyncSession, fingerprint: str, field: str, value):
    """Helper function to upsert a single answer."""

    # Validate field against FIELD_MAPPING (defense in depth)
    if field not in FIELD_MAPPING:
        raise ValueError(f"Invalid field: {field}")

    # Check if record exists
    query = select(DarkDataSurvey).where(DarkDataSurvey.fingerprint == fingerprint)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing record - use string field name for values dict
        update_stmt = (
            update(DarkDataSurvey)
            .where(DarkDataSurvey.fingerprint == fingerprint)
            .values(**{field: value})
        )
        await db.execute(update_stmt)
    else:
        # Insert new record - use string field name for values dict
        insert_stmt = insert(DarkDataSurvey).values(fingerprint=fingerprint, **{field: value})
        await db.execute(insert_stmt)

    await db.commit()


@router.get("/dark-data-survey/{fingerprint}")
async def get_survey_response(
    fingerprint: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get survey response by fingerprint."""

    query = select(DarkDataSurvey).where(DarkDataSurvey.fingerprint == fingerprint)
    result = await db.execute(query)
    survey_response = result.scalar_one_or_none()

    if not survey_response:
        raise HTTPException(status_code=404, detail="Survey response not found")

    return SurveyResponse.model_validate(survey_response)