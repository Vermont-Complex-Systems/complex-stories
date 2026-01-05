from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from ..core.database import get_db_session
from ..models.dark_data_survey import DarkDataSurvey, SurveyAnswerRequest, SurveyUpsertRequest, SurveyResponse

# Public router for survey responses
router = APIRouter()

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

@router.post("/dark-data-survey/answer")
async def post_answer(
    request: SurveyAnswerRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Post a survey answer with value-to-ordinal conversion."""

    # Validate fingerprint
    if not request.fingerprint or request.fingerprint.strip() == '':
        raise HTTPException(status_code=400, detail="Fingerprint is required")

    # Validate field and get ordinal value
    if request.field not in VALUE_TO_ORDINAL:
        raise HTTPException(status_code=400, detail=f"Invalid field: {request.field}")

    field_mapping = VALUE_TO_ORDINAL[request.field]
    if request.value not in field_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid value '{request.value}' for field '{request.field}'")

    ordinal_value = field_mapping[request.value]

    try:
        # Use upsert functionality
        await upsert_answer(db, request.fingerprint, request.field, ordinal_value)
        return {"message": f"Saved {request.field}: {request.value} (ordinal: {ordinal_value})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving answer: {str(e)}")


@router.post("/dark-data-survey/upsert")
async def upsert_survey_answer(
    request: SurveyUpsertRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Upsert a single survey answer by field."""

    # Validate fingerprint
    if not request.fingerprint or request.fingerprint.strip() == '':
        raise HTTPException(status_code=400, detail="Fingerprint is required")

    # Validate field exists in the model
    if request.field not in FIELD_MAPPING:
        raise HTTPException(status_code=400, detail=f"Invalid field: {request.field}")

    try:
        await upsert_answer(db, request.fingerprint, request.field, request.value)
        return {"message": f"Upserted {request.field}: {request.value}"}
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