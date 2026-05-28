from enum import Enum
from pydantic import BaseModel, Field

class PatientSex(str, Enum):
    male = "male"
    female = "female"   
    other = "other"

class TriageRequest(BaseModel):
    #Requried Fields
    complaint: str = Field(min_length=5, max_length=2000)
    patient_age: int = Field(ge=0, le=120)
    patient_sex: PatientSex
    severity: int = Field(ge=1, le=10)

    #Optional vital signs
    heart_rate: int | None = Field(default=None, ge=20, le=250)
    systolic_bp: int | None = Field(default=None, ge=50, le=300)
    diastolic_bp: int | None = Field(default=None, ge=30, le=200)
    respiratory_rate: int | None = Field(default=None, ge=5, le=60)
    oxygen_saturation: int | None = Field(default=None, ge=50, le=100)
    temperature_celsius: float | None = Field(default=None, ge=30.0, le=45.0)

    #Optional medical history
    medical_history: list[str] = Field(default_factory=list)