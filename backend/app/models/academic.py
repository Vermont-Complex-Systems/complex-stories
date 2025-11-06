"""
SQLAlchemy models for academic data API endpoints.

These models exactly match the export structures from the Dagster pipeline.
"""
from sqlalchemy import Column, String, Integer, Date, Float, Text, Boolean, DateTime
from datetime import date
from ..core.database import Base


class Paper(Base):
    """Papers table - exact structure from paper.py export"""
    __tablename__ = "papers"

    # Composite primary key (paper ID + ego author)
    id = Column(String, primary_key=True)
    ego_author_id = Column(String, primary_key=True)

    # Author info
    ego_display_name = Column(String)

    # Publication info
    title = Column(Text)
    publication_year = Column(Integer)
    publication_date = Column(Date)
    cited_by_count = Column(Integer)
    work_type = Column(String)  # Note: called 'type' in frontend, 'work_type' in export
    language = Column(String)
    doi = Column(String)

    # Author-specific info
    author_position = Column(String)
    is_corresponding = Column(Boolean)

    # Publication details
    is_open_access = Column(Boolean)
    landing_page_url = Column(String)
    pdf_url = Column(String)
    license = Column(String)
    journal_name = Column(String)
    source_type = Column(String)

    oa_status = Column(String)
    oa_url = Column(String)

    topic_id = Column(String)
    topic_name = Column(String)
    topic_score = Column(Float)

    volume = Column(String)
    issue = Column(String)
    first_page = Column(String)
    last_page = Column(String)

    fwci = Column(Float)
    has_fulltext = Column(Boolean)
    fulltext_origin = Column(String)
    is_retracted = Column(Boolean)
    countries_distinct_count = Column(Integer)
    institutions_distinct_count = Column(Integer)
    locations_count = Column(Integer)
    referenced_works_count = Column(Integer)

    updated_date = Column(DateTime)
    created_date = Column(Date)

    # Collaboration metrics (from pandas processing)
    nb_coauthors_raw = Column(Integer)
    nb_coauthors = Column(Integer)  # Calculated number of coauthors
    coauthor_names = Column(Text)   # Semicolon-separated list

    # Citation analysis (from pandas processing)
    citation_percentile = Column(Float)
    citation_category = Column(String)  # uncited, low_impact, medium_impact, high_impact, very_high_impact

    # UMAP embeddings
    umap_1 = Column(Float)
    umap_2 = Column(Float)
    abstract = Column(Text)
    s2FieldsOfStudy = Column(Text)  # Semantic Scholar fields
    fieldsOfStudy = Column(Text)    # OpenAlex fields

    def __repr__(self):
        return f"<Paper(id='{self.id}', author='{self.ego_display_name}', title='{self.title[:50]}...')>"


class Coauthor(Base):
    """Coauthors table - exact structure from coauthor.py export"""
    __tablename__ = "coauthors"

    # Create a composite primary key since there's no natural single ID
    id = Column(String, primary_key=True)  # We'll generate this as ego_author_id + coauthor_id + publication_year

    # UVM professor information
    ego_author_id = Column(String)
    ego_display_name = Column(String)
    ego_department = Column(String)
    publication_year = Column(Integer)
    nb_coauthors = Column(Integer)

    # Publication info with jittered date
    publication_date = Column(Date)

    # Ego author information
    ego_first_pub_year = Column(Integer)
    ego_age = Column(Integer)

    # Coauthor information
    coauthor_id = Column(String)
    coauthor_display_name = Column(String)
    coauthor_age = Column(Integer)
    coauthor_first_pub_year = Column(Integer)

    # Age analysis
    age_diff = Column(Integer)  # ego_age - coauthor_age
    age_category = Column(String)  # younger, older, same, unknown

    # Collaboration metrics
    yearly_collabo = Column(Integer)     # Collaborations in this year
    all_times_collabo = Column(Integer)  # Cumulative collaborations

    # Institution information
    primary_institution = Column(String)      # Ego author's institution
    coauthor_institution = Column(String)     # Coauthor's institution
    shared_institutions = Column(String)      # Institution if both share it, else NULL

    def __repr__(self):
        return f"<Coauthor(ego='{self.ego_display_name}', coauthor='{self.coauthor_display_name}', year={self.publication_year})>"


class Training(Base):
    """Training data table - processed collaboration data for research analysis"""
    __tablename__ = "training"

    # Composite primary key
    aid = Column(String, primary_key=True)  # Author ID
    pub_year = Column(Integer, primary_key=True)  # Publication year

    # Author info
    name = Column(String)

    # Age category collaboration counts
    older = Column(Integer)  # Collaborations with older researchers
    same = Column(Integer)   # Collaborations with same-age researchers
    younger = Column(Integer)  # Collaborations with younger researchers

    # Author metadata
    author_age = Column(Integer)
    institution = Column(String)

    # Collaboration patterns
    existing_collab = Column(Integer)  # Existing collaborations (continued)
    new_collab = Column(Integer)      # New collaborations (first time)
    age_category = Column(String)     # Age category for this record
    shared_institutions = Column(String)

    # Calculated metrics
    counts = Column(Integer)          # Total collaborations
    prop_younger = Column(Float)      # Proportion of younger collaborators
    total_coauth = Column(Integer)    # Total coauthorships
    nb_papers = Column(Integer)       # Number of papers published
    density = Column(Float)           # Network density

    # Professor metadata
    is_prof = Column(Boolean)
    group_size = Column(Integer)
    perceived_as_male = Column(Boolean)
    host_dept = Column(String)
    college = Column(String)
    has_research_group = Column(Boolean)
    oa_uid = Column(String)           # OpenAlex author ID
    group_url = Column(String)
    first_pub_year = Column(Integer)
    payroll_name = Column(String)
    position = Column(String)
    changing_rate = Column(Float)     # Collaboration pattern change rate

    def __repr__(self):
        return f"<Training(name='{self.name}', year={self.pub_year}, collaborations={self.counts})>"