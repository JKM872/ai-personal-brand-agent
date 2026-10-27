// Pure lead validation (same rules as crm/validation.py). No dependencies.
export const SERVICES = ["audyt", "wdrozenie", "abonament", "inne"];
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const CTRL_RE = /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g;

const clean = (v) => (v === undefined || v === null ? "" : String(v).replace(CTRL_RE, "").trim());

// Returns {spam: reason} | {errors: {field: code}} | {lead: {...}}
export function validateLead(body, now) {
  if (!body || typeof body !== "object" || Array.isArray(body)) return { errors: { _: "invalid_json" } };
  if (clean(body.website)) return { spam: "honeypot" };
  const ts = Number(body.ts);
  if (body.ts === undefined || body.ts === null || body.ts === "" || !Number.isFinite(ts)) return { spam: "no_ts" };
  if (now - ts < 3000) return { spam: "too_fast" };

  const errors = {};
  const name = clean(body.name);
  const email = clean(body.email).toLowerCase();
  const company = clean(body.company);
  const message = clean(body.message);
  const service = clean(body.service);

  if (!name) errors.name = "required"; else if (name.length > 100) errors.name = "too_long";
  if (!email) errors.email = "required"; else if (email.length > 254 || !EMAIL_RE.test(email)) errors.email = "invalid";
  if (company.length > 150) errors.company = "too_long";
  if (message.length > 2000) errors.message = "too_long";
  if (service && !SERVICES.includes(service)) errors.service = "invalid";
  if (body.consent !== true) errors.consent = "required";

  const utm = [];
  for (const k of ["utm_source", "utm_medium", "utm_campaign"]) {
    const v = clean(body[k]);
    if (v.length > 100) errors[k] = "too_long"; else if (v) utm.push(`${k}=${v}`);
  }
  if (Object.keys(errors).length) return { errors };

  return {
    lead: {
      name, email, company, service_interest: service, message,
      source_utm: utm.join("&"),
      consent_at: new Date(now).toISOString(),
      consent_text_version: "v1",
      status: "new",
    },
  };
}
