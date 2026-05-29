import { useEffect, useState } from "react";
import {
  Stethoscope,
  Settings,
  User,
  UserCog,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Loader2,
  ChevronDown,
  Key,
  Send,
} from "lucide-react";
import type { TriageRequest, TriageResponse, PatientSex } from "./types";
import { triage, getApiKey, setApiKey, clearApiKey, ApiError } from "./api";

const ESI_DISPLAY: Record<
  number,
  { label: string; sub: string; gradient: string; ring: string }
> = {
  1: {
    label: "Level 1",
    sub: "Resuscitation",
    gradient: "from-red-600 to-rose-600",
    ring: "ring-red-200",
  },
  2: {
    label: "Level 2",
    sub: "Emergent",
    gradient: "from-orange-500 to-amber-500",
    ring: "ring-orange-200",
  },
  3: {
    label: "Level 3",
    sub: "Urgent",
    gradient: "from-yellow-500 to-amber-400",
    ring: "ring-yellow-200",
  },
  4: {
    label: "Level 4",
    sub: "Less Urgent",
    gradient: "from-emerald-600 to-green-600",
    ring: "ring-emerald-200",
  },
  5: {
    label: "Level 5",
    sub: "Non-Urgent",
    gradient: "from-sky-500 to-blue-600",
    ring: "ring-sky-200",
  },
};

export default function App() {
  const [apiKey, setApiKeyState] = useState<string | null>(getApiKey());
  const [showSettings, setShowSettings] = useState<boolean>(!getApiKey());
  const [apiKeyInput, setApiKeyInput] = useState<string>("");
  const [view, setView] = useState<"patient" | "doctor">("patient");
  const [complaint, setComplaint] = useState("");
  const [age, setAge] = useState<number | "">("");
  const [sex, setSex] = useState<PatientSex | "">("");
  const [severity, setSeverity] = useState<number | "">("");
  const [heartRate, setHeartRate] = useState<number | "">("");
  const [systolicBp, setSystolicBp] = useState<number | "">("");
  const [diastolicBp, setDiastolicBp] = useState<number | "">("");
  const [respiratoryRate, setRespiratoryRate] = useState<number | "">("");
  const [oxygenSat, setOxygenSat] = useState<number | "">("");
  const [tempC, setTempC] = useState<number | "">("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TriageResponse | null>(null);

  useEffect(() => {
    setApiKeyState(getApiKey());
  }, []);

  function handleSaveKey() {
    setApiKey(apiKeyInput.trim());
    setApiKeyState(apiKeyInput.trim());
    setApiKeyInput("");
    setShowSettings(false);
  }

  function handleClearKey() {
    clearApiKey();
    setApiKeyState(null);
    setShowSettings(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const request: TriageRequest = {
      complaint: complaint.trim(),
      patient_age: Number(age),
      patient_sex: sex as PatientSex,
      severity: Number(severity),
      heart_rate: heartRate === "" ? null : Number(heartRate),
      systolic_bp: systolicBp === "" ? null : Number(systolicBp),
      diastolic_bp: diastolicBp === "" ? null : Number(diastolicBp),
      respiratory_rate: respiratoryRate === "" ? null : Number(respiratoryRate),
      oxygen_saturation: oxygenSat === "" ? null : Number(oxygenSat),
      temperature_celsius: tempC === "" ? null : Number(tempC),
    };

    try {
      const response = await triage(request);
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("Network error. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 text-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 shadow-sm">
              <Stethoscope className="h-5 w-5 text-white" strokeWidth={2.25} />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">MedEval</h1>
              <p className="-mt-0.5 text-[11px] font-medium text-slate-500">
                AI Triage Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <div className="flex rounded-lg border border-slate-200 bg-slate-50 p-0.5">
              <button
                onClick={() => setView("patient")}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition ${
                  view === "patient"
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                <User className="h-3.5 w-3.5" />
                Patient
              </button>
              <button
                onClick={() => setView("doctor")}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition ${
                  view === "doctor"
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                <UserCog className="h-3.5 w-3.5" />
                Doctor
              </button>
            </div>
            <button
              onClick={() => setShowSettings((s) => !s)}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              title="Settings"
            >
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8">
        {/* Hero */}
        <div className="mb-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Triage in seconds,{" "}
            <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
              grounded in evidence
            </span>
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-sm text-slate-600">
            Python rules decide urgency. The LLM only writes the explanation.
            Grounded in the AHRQ ESI Handbook v4.
          </p>
        </div>

        {/* Settings */}
        {showSettings && (
          <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Key className="h-4 w-4 text-indigo-600" />
              <h3 className="text-sm font-semibold">API Key</h3>
            </div>
            <p className="mb-3 text-xs leading-relaxed text-slate-600">
              Stored only in your browser's local storage. Sent as the
              <code className="mx-1 rounded bg-slate-100 px-1 py-0.5 text-[11px]">
                X-API-Key
              </code>
              header with every request.
            </p>
            <div className="flex gap-2">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder={apiKey ? "Replace stored key…" : "Paste your key"}
                className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              />
              <button
                onClick={handleSaveKey}
                disabled={!apiKeyInput.trim()}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                Save
              </button>
              {apiKey && (
                <button
                  onClick={handleClearKey}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Clear
                </button>
              )}
            </div>
            {apiKey && (
              <p className="mt-2 text-[11px] text-slate-500">
                Stored: {apiKey.slice(0, 6)}…{apiKey.slice(-4)}
              </p>
            )}
          </div>
        )}

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div className="mb-4 flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-600" />
            <h3 className="text-sm font-semibold">Patient details</h3>
          </div>

          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-600">
            Chief complaint
          </label>
          <textarea
            value={complaint}
            onChange={(e) => setComplaint(e.target.value)}
            required
            minLength={5}
            rows={4}
            placeholder="Describe symptoms in plain language…"
            className="mb-5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          />

          <div className="mb-5 grid grid-cols-3 gap-3">
            <Field label="Age (years)">
              <input
                type="number"
                value={age}
                onChange={(e) =>
                  setAge(e.target.value === "" ? "" : Number(e.target.value))
                }
                required
                min={0}
                max={120}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              />
            </Field>
            <Field label="Sex">
             <select
               value={sex}
               onChange={(e) => setSex(e.target.value as PatientSex | "")}
               required
               className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              >
              <option value="" disabled>Select…</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
             </select>
            </Field>
            <Field label="Severity (1–10)">
              <input
                type="number"
                value={severity}
                onChange={(e) =>
                  setSeverity(e.target.value === "" ? "" : Number(e.target.value))
                }
                required
                min={1}
                max={10}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              />
            </Field>
          </div>

          <details className="mb-5 group">
            <summary className="flex cursor-pointer items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-600 hover:text-slate-900">
              <ChevronDown className="h-3.5 w-3.5 transition group-open:rotate-180" />
              Optional vital signs
            </summary>
            <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
              <VitalInput label="Heart rate (bpm)" value={heartRate} setValue={setHeartRate} />
              <VitalInput label="Systolic BP" value={systolicBp} setValue={setSystolicBp} />
              <VitalInput label="Diastolic BP" value={diastolicBp} setValue={setDiastolicBp} />
              <VitalInput label="Respiratory rate" value={respiratoryRate} setValue={setRespiratoryRate} />
              <VitalInput label="SpO₂ (%)" value={oxygenSat} setValue={setOxygenSat} />
              <VitalInput label="Temperature (°C)" value={tempC} setValue={setTempC} step={0.1} />
            </div>
          </details>

          <button
            type="submit"
            disabled={loading || !apiKey}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:from-indigo-700 hover:to-violet-700 disabled:cursor-not-allowed disabled:from-slate-300 disabled:to-slate-300"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Running pipeline…
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Triage patient
              </>
            )}
          </button>
          {!apiKey && (
            <p className="mt-2 text-xs text-rose-600">
              No API key configured. Open Settings (⚙) above.
            </p>
          )}
        </form>

        {/* Error */}
        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-6 animate-slide-up overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            {/* Big ESI banner */}
            <div
              className={`bg-gradient-to-br p-6 text-white ${ESI_DISPLAY[result.esi_level].gradient}`}
            >
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest opacity-80">
                    Triage Assessment
                  </p>
                  <h3 className="mt-1 text-3xl font-bold tracking-tight">
                    {ESI_DISPLAY[result.esi_level].label}
                  </h3>
                  <p className="mt-0.5 text-sm font-medium opacity-90">
                    {ESI_DISPLAY[result.esi_level].sub}
                  </p>
                </div>
                <CheckCircle2 className="h-10 w-10 opacity-80" />
              </div>
            </div>

            <div className="p-6">
              <h4 className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
                <User className="h-3.5 w-3.5" /> For the patient
              </h4>
              <p className="text-sm leading-relaxed text-slate-800">
                {result.explanation}
              </p>

              {view === "doctor" && (
                <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <h4 className="mb-3 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <UserCog className="h-3.5 w-3.5" /> Clinician details
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-semibold text-slate-700">
                        Decision path:
                      </span>{" "}
                      <code className="rounded bg-white px-1.5 py-0.5 text-xs ring-1 ring-slate-200">
                        {result.decision_path}
                      </code>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-700">
                        Rules fired:
                      </span>
                      <ul className="mt-1.5 space-y-1">
                        {result.rules_fired.map((r) => (
                          <li
                            key={r}
                            className="flex items-center gap-1.5 text-slate-700"
                          >
                            <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
                            <code className="rounded bg-white px-1.5 py-0.5 text-xs ring-1 ring-slate-200">
                              {r}
                            </code>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <p className="mt-12 text-center text-xs text-slate-400">
          Portfolio project · Not a medical device · Not for clinical use
        </p>
      </main>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-600">
        {label}
      </label>
      {children}
    </div>
  );
}

function VitalInput({
  label,
  value,
  setValue,
  step,
}: {
  label: string;
  value: number | "";
  setValue: (v: number | "") => void;
  step?: number;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-[11px] font-medium text-slate-600">{label}</label>
      <input
        type="number"
        step={step}
        value={value}
        onChange={(e) => setValue(e.target.value === "" ? "" : Number(e.target.value))}
        className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
      />
    </div>
  );
}