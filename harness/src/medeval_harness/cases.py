from __future__ import annotations

import json
from importlib import resources
from typing import Literal

from pydantic import BaseModel, Field


PatientSex = Literal["male", "female", "other"]


class CaseInput(BaseModel):
    complaint: str = Field(min_length=5)
    patient_age: int = Field(ge=0, le=120)
    patient_sex: PatientSex
    severity: int = Field(ge=1, le=10)
    patient_age_months: int | None = Field(default=None, ge=0, le=60)
    heart_rate: int | None = Field(default=None, ge=20, le=250)
    systolic_bp: int | None = Field(default=None, ge=50, le=300)
    diastolic_bp: int | None = Field(default=None, ge=30, le=200)
    respiratory_rate: int | None = Field(default=None, ge=5, le=60)
    oxygen_saturation: int | None = Field(default=None, ge=50, le=100)
    temperature_celsius: float | None = Field(default=None, ge=30.0, le=45.0)
    medical_history: list[str] = Field(default_factory=list)


ESILevel = Literal[1, 2, 3, 4, 5]
DecisionPath = Literal["A", "B", "C", "C_upgraded_by_D"]


class CaseExpectation(BaseModel):
    esi_level: ESILevel
    decision_path: DecisionPath
    expected_rules_fired: list[str] = Field(
        default_factory=list,
        description=(
            "Rule IDs we expect the engine to fire (informational). "
            "Mismatches are flagged in the report but do not fail the case."
        ),
    )
    tolerance: int = Field(
        default=0,
        ge=0,
        le=4,
        description=(
            "Allowed difference between predicted and expected ESI level. "
            "Use 1 for handbook cases marked 'consider ESI X'."
        ),
    )


class Case(BaseModel):
    case_id: str = Field(pattern=r"^ESI-\d{3}$")
    title: str
    source: str = Field(description="Handbook page or section, e.g. 'Chapter 9, Case 3'")
    tags: list[str] = Field(default_factory=list)
    notes: str = ""

    input: CaseInput
    expected: CaseExpectation




def load_cases() -> list[Case]:
    data_resource = resources.files("medeval_harness.data") / "esi_cases.json"
    raw = json.loads(data_resource.read_text())
    return [Case.model_validate(item) for item in raw]