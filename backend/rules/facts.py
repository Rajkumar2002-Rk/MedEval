"""
ExtractedFacts: structured boolean facts the LLM extracts from the patient's
free-text complaint, plus the predicted resource list.

Every field referenced as `is_X` or `has_X` in esi_rules.yaml is declared here.
The Pydantic model is the contract: the LLM extraction prompt must produce a
dict that maps onto these fields exactly.

Default behavior:
- All booleans default to False (the LLM only sets True when it sees clear
  evidence in the complaint text).
- predicted_resources defaults to an empty list.
- EXCEPTION: `pregnancy_status_confirmed_negative` also defaults to False, but
  here False is the SAFE default for the ectopic-pregnancy rule (B25). Read
  the field as "have we confirmed pregnancy is absent?"  False = "no, not
  confirmed" = treat possible pregnancy as live.

Why default to False (not True or None):
- Defaulting to True would over-triage every patient to ESI 2 by default.
- Defaulting to None (unknown) would force every rule to handle missing data,
  bloating the engine.
- False = "no evidence seen" → rule won't fire → other rules may still catch
  the patient → safe under-trigger that we tune in Phase 2 against the eval
  dataset.
"""

from pydantic import BaseModel, Field

class ExtractedFacts(BaseModel):
    # Decision A -- Immediate Life-saving intervention (ESI 1)
    is_intubated: bool = False
    is_apneic: bool = False
    is_pulseless: bool = False
    has_severe_respiratory_distress: bool = False
    has_acute_mental_status_change: bool = False
    is_unresponsive: bool = False

    # Decision B - High risk / altered mental status / severe pain (ESI 2)
    # B-Q2: new onset altered mental status
    has_new_onset_confusion: bool = False
    has_new_onset_lethargy: bool = False
    has_new_onset_disorientation: bool = False
    has_altered_mental_status: bool = False

    # B-Q3: Severe pain / distress
    has_sickle_cell_pain_crisis: bool = False
    has_renal_colic: bool = False
    is_oncology_patient: bool = False
    has_significant_burn_requiring_pain_control: bool = False
    has_acute_urinary_retention: bool = False
    is_sexual_assault_victim_in_distress: bool = False
    is_combative_at_triage: bool = False
    has_acute_grief_reaction: bool = False
    is_domestic_violence_victim_in_distress: bool = False

    # B-Q1: cardiovascular high - risk
    has_chest_pain_or_equivalent: bool = False
    has_cardiac_risk_factor: bool = False
    has_sudden_palpitations: bool = False
    has_cold_extremity: bool = False
    has_absent_or_diminished_pulse: bool = False
    has_end_organ_symptoms: bool = False
    has_signs_of_aortic_dissection_or_aaa: bool = False

    # B-Q1: respiratory high-risk
    has_drooling: bool = False
    has_stridor: bool = False
    has_respiratory_distress: bool = False
    has_signs_of_spontaneous_pneumothorax: bool = False
    has_known_allergen_exposure: bool = False
    has_throat_or_tongue_swelling_or_wheeze: bool = False

    # B-Q1: neurological high-risk
    has_sudden_onset_speech_deficit: bool = False
    has_sudden_onset_motor_weakness: bool = False
    has_sudden_onset_facial_droop: bool = False
    has_sudden_severe_worst_headache_of_life: bool = False
    has_severe_headache: bool = False
    has_stiff_neck: bool = False
    has_rash: bool = False
    has_reported_seizure: bool = False
    has_recent_head_injury: bool = False
    is_vomiting: bool = False

    # B-Q1: abdominal / GI / Gu high-risk
    has_severe_abdominal_pain: bool = False
    is_vomiting_blood: bool = False
    has_significant_lower_gi_bleeding: bool = False
    has_lower_abdominal_pain: bool = False
    has_localized_abdominal_pain: bool = False
    has_sudden_severe_testicular_pain: bool = False

    # B-Q1: pregnancy / OB-GYN
    is_pregnant: bool = False
    is_of_childbearing_age_or_pregnant: bool = False
    # See module docstring: False means pregnancy has NOT been ruled out - the safe default. Set True only if a confirmed negative test exists.
    pregnancy_status_confirmed_negative: bool = False
    is_late_pregnancy: bool = False
    has_vaginal_bleeding: bool = False
    has_postpartum_heavy_vaginal_bleeding: bool = False

    # B-Q1: endocrine / metabolic
    has_known_diabetes: bool = False
    is_dialysis_patient: bool = False
    has_missed_dialysis: bool = False
    has_signs_of_dehydration: bool = False
    has_weakness_or_dizziness: bool = False
    has_persistent_vomiting: bool = False

    # B-Q1: toxicological / oncology / immune
    has_intentional_or_significant_overdose: bool = False
    is_immunocompromised: bool = False
    has_suspected_infection: bool = False

    # B-Q1: trauma / wounds
    has_high_risk_trauma_mechanism: bool = False
    has_penetrating_trauma_to_torso_neck_head_or_groin: bool = False
    has_signs_of_compartment_syndrome: bool = False
    has_extremity_neurovascular_compromise: bool = False
    has_partial_or_complete_amputation: bool = False
    has_uncontrolled_bleeding: bool = False
    has_arterial_bleeding: bool = False
    has_signs_of_trauma: bool = False
    has_aspiration_risk: bool = False

    # B-Q1: ocular
    has_chemical_eye_exposure: bool = False
    has_sudden_vision_loss: bool = False
    has_significant_eye_trauma: bool = False

    # B-Q1: mental health
    is_suicidal: bool = False
    is_homicidal: bool = False
    is_elopement_risk: bool = False
    is_acutely_psychotic: bool = False
    is_violent_at_triage: bool = False
    is_intoxicated: bool = False

    # B-Q1: environmental / transplant / pediatric
    has_smoke_or_chemical_inhalation: bool = False
    has_third_degree_burns: bool = False
    is_transplant_recipient: bool = False
    has_signs_of_rejection: bool = False
    has_suspected_abuse: bool = False

    # DECISION C -- Resource Prediction (drives ESI 3, 4, 5)
    # The LLM returns a list of resource type strings the patient will need.
    # Engine computes predicted_resource_count = len(predicted_resources).
    # Allowed values come from the resource catalog documented in esi_rules.yaml.
    predicted_resources: list[str] = Field(default_factory=list)

