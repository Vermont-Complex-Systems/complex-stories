from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, Union
from ..core.database import Base


class DarkDataSurvey(Base):
    __tablename__ = "dark_data_survey"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fingerprint = Column(String(255), nullable=False)
    consent = Column(Integer)
    socialMediaPrivacy = Column(Integer)
    platformMatters = Column(String)
    institutionPreferences = Column(Integer)
    demographicsMatter = Column(Integer)
    relativePreferences = Column(Integer)
    govPreferences = Column(Integer)
    polPreferences = Column(Integer)
    age = Column(String)
    gender_ord = Column(Integer)
    orientation_ord = Column(Integer)
    race_ord = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Pydantic models for API requests/responses
class SurveyAnswerRequest(BaseModel):
    fingerprint: str
    field: str
    value: str


class SurveyUpsertRequest(BaseModel):
    fingerprint: str
    field: str
    value: Union[int, str]


class SurveyResponse(BaseModel):
    id: int
    fingerprint: str
    consent: Optional[str] = None
    socialMediaPrivacy: Optional[int] = None
    platformMatters: Optional[int] = None
    institutionPreferences: Optional[int] = None
    demographicsMatter: Optional[int] = None
    relativePreferences: Optional[int] = None
    govPreferences: Optional[int] = None
    polPreferences: Optional[int] = None
    age: Optional[str] = None
    gender_ord: Optional[int] = None
    orientation_ord: Optional[int] = None
    race_ord: Optional[int] = None

    class Config:
        from_attributes = True