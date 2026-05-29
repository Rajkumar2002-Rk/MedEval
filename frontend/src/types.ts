// Mirrors the backend's models.PatientSex enum.
export type PatientSex = "male" | "female" | "other";

// Mirrors the backend's models.TriageRequest.
// Required fields are non-optional; optional vitals + history are nullable.
export interface TriageRequest {
  complaint: string;
  patient_age: number;
  patient_sex: PatientSex;
  severity: number;

  // Optional vitals
  patient_age_months?: number | null;
  heart_rate?: number | null;
  systolic_bp?: number | null;
  diastolic_bp?: number | null;
  respiratory_rate?: number | null;
  oxygen_saturation?: number | null;
  temperature_celsius?: number | null;
  medical_history?: string[];
}

// Mirrors the backend's main.TriageResponse.
export interface TriageResponse {
  esi_level: 1 | 2 | 3 | 4 | 5;
  decision_path: string;
  rules_fired: string[];
  explanation: string;
}