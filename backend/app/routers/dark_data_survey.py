from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from ..core.database import get_db_session
from ..models.dark_data_survey import DarkDataSurvey, SurveyAnswerRequest, SurveyUpsertRequest, SurveyResponse

# Public router for survey responses
router = APIRouter()

# Admin router for administrative functions
admin_router = APIRouter()

# Value to ordinal mapping (same as frontend)
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
    valid_fields = [
        'consent', 'socialMediaPrivacy', 'platformMatters', 'institutionPreferences',
        'demographicsMatter', 'relativePreferences', 'govPreferences',
        'polPreferences', 'age', 'gender_ord', 'orientation_ord', 'race_ord'
    ]

    if request.field not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field: {request.field}")

    try:
        await upsert_answer(db, request.fingerprint, request.field, request.value)
        return {"message": f"Upserted {request.field}: {request.value}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error upserting answer: {str(e)}")


async def upsert_answer(db: AsyncSession, fingerprint: str, field: str, value):
    """Helper function to upsert a single answer."""

    # Check if record exists
    query = select(DarkDataSurvey).where(DarkDataSurvey.fingerprint == fingerprint)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing record
        update_stmt = (
            update(DarkDataSurvey)
            .where(DarkDataSurvey.fingerprint == fingerprint)
            .values(**{field: value})
        )
        await db.execute(update_stmt)
    else:
        # Insert new record
        insert_data = {'fingerprint': fingerprint, field: value}
        insert_stmt = insert(DarkDataSurvey).values(**insert_data)
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


@admin_router.put("/dark-data-survey/{fingerprint_id}")
async def update_dark_data_survey_by_fingerprint(
    fingerprint_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Update an academic research group entry by database ID."""

    query = select(DarkDataSurvey).where(DarkDataSurvey.fingerprint == fingerprint_id)
    result = await db.execute(query)

    pass