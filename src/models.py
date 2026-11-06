from enum import StrEnum
from pydantic import BaseModel, Field


class PermissionTier(StrEnum):
    READ_ONLY = "read_only"
    SANDBOX_WRITE = "sandbox_write"
    PROD_MUTATE = "prod_mutate"


class ReadinessPillar(BaseModel):
    name: str
    score: int
    max_score: int = 25
    passed: bool
    details: str
    recommendations: list[str] = Field(default_factory=list)


class ReadinessReport(BaseModel):
    repo_name: str
    score_before: int
    score_after: int
    grade: str = "Unprepared"
    detected_stack: list[str] = Field(default_factory=list)
    discovered_sensitive_paths: list[str] = Field(default_factory=list)
    pillars: list[ReadinessPillar] = Field(default_factory=list)
    missing_safeguards: list[str] = Field(default_factory=list)
    generated_policy_yaml: str = ""
    generated_agents_md: str = ""
    scan_duration_ms: float = 0.0

