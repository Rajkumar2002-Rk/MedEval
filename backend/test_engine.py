"""
Quick exploration script to test the rules engine with hand-built patient cases.
Not a real test suite. This is just to confirm the engine works end-to-end.

"""

from models import TriageRequest, PatientSex
from rules.facts import ExtractedFacts
from rules.engine import triage


def run_case(name: str, request: TriageRequest, facts: ExtractedFacts) -> None:
    "Run one case and print the result nicely."
    result = triage(request, facts)
    print(f"\n{'=' * 70}")
    print(f"CASE: {name}")
    print(f"{'=' * 70}")
    print(f"  ESI Level:     {result.esi_level}")
    print(f"  Decision path: {result.decision_path}")
    print(f"  Rules fired:   {result.rules_fired}")
    print(f"  Rationales:")
    for r in result.rationales:
        print(f"    - {r}")


# CASE 1: Intubated patient → expect ESI 1 (rule A1) 
case_1_request = TriageRequest(
    complaint="Brought in by EMS, intubated for respiratory failure",
    patient_age=68,
    patient_sex=PatientSex.male,
    severity=10,
)
case_1_facts = ExtractedFacts(is_intubated=True)
run_case("Intubated 68yo male", case_1_request, case_1_facts)


# CASE 2: 55yo with chest pain → expect ESI 2 (rule B8) 
case_2_request = TriageRequest(
    complaint="Crushing chest pain for the last 30 minutes",
    patient_age=55,
    patient_sex=PatientSex.male,
    severity=8,
    heart_rate=95,
)
case_2_facts = ExtractedFacts(has_chest_pain_or_equivalent=True)
run_case("55yo male with chest pain", case_2_request, case_2_facts)


# CASE 3: Ankle sprain → expect ESI 4 (rule C2 — 1 resource: x-ray) 
case_3_request = TriageRequest(
    complaint="Twisted my ankle playing soccer this morning, swollen and painful",
    patient_age=22,
    patient_sex=PatientSex.female,
    severity=6,
)
case_3_facts = ExtractedFacts(predicted_resources=["xray"])
run_case("22yo with ankle sprain", case_3_request, case_3_facts)


# CASE 4: Prescription refill → expect ESI 5 (rule C3 — 0 resources) 
case_4_request = TriageRequest(
    complaint="Need a refill on my blood pressure medication",
    patient_age=60,
    patient_sex=PatientSex.male,
    severity=1,
)
case_4_facts = ExtractedFacts(predicted_resources=[])
run_case("Prescription refill", case_4_request, case_4_facts)


# CASE 5: Pneumonia with bad vitals → expect ESI 2 (rule D1 upgrades C1) 
case_5_request = TriageRequest(
    complaint="Cough and fever for 4 days, getting worse, very short of breath",
    patient_age=57,
    patient_sex=PatientSex.female,
    severity=6,
    heart_rate=110,
    respiratory_rate=28,
    oxygen_saturation=90,
    temperature_celsius=38.5,
)
case_5_facts = ExtractedFacts(
    predicted_resources=["labs", "xray", "iv_fluids", "iv_or_im_medications"],
)
run_case("57yo with pneumonia + bad vitals", case_5_request, case_5_facts)