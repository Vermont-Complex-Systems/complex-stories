from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ..core.database import Base


class AcademicResearchGroups(Base):
    __tablename__ = "academic_research_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payroll_name = Column(String(255), nullable=False)
    payroll_year = Column(Integer, nullable=False)
    position = Column(String(255), nullable=True)
    oa_display_name = Column(String(255), nullable=True)
    is_prof = Column(Boolean, nullable=True)
    perceived_as_male = Column(Boolean, nullable=True)
    host_dept = Column(String(255), nullable=True)
    has_research_group = Column(Boolean, nullable=True)
    group_size = Column(Integer, nullable=True)
    oa_uid = Column(String(255), nullable=True)
    group_url = Column(String(500), nullable=True)
    first_pub_year = Column(Integer, nullable=True)
    inst_ipeds_id = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    college = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<AcademicResearchGroups(id={self.id}, payroll_name='{self.payroll_name}', payroll_year={self.payroll_year})>"