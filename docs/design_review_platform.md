# Design Review Platform Specification

## Vision
Create a digital workspace that empowers the Senior Design Manager (Owner's Representative) to rapidly review, annotate, and approve workplace fit-out design packages (PDF, DWG, IFC). The platform should combine automated compliance insights with human-centric workflows so every consultant submission is client-ready, code-compliant, and coordinated across disciplines.

## Target Persona
- **Role:** Senior Design Manager based in Saudi Arabia acting as the Owner's Representative.
- **Mandate:** Ensure architectural and MEP packages satisfy client standards, Saudi Building Code, Civil Defense, MOMRAH, SEC requirements, and workplace best practices before release.
- **Working Style:** Solution-oriented, expects actionable recommendations, leverages checklists, and tracks RFIs until closure.
- **Success Metrics:** Faster review cycles, fewer back-and-forth RFIs, higher compliance rate on first issue, and traceable audit trail.

## Core Jobs-to-Be-Done
1. **Ingest & Organize Submissions** – Receive PDFs or 3D models, version them, and map to relevant projects and disciplines.
2. **Automated Compliance Screening** – Run rules-based and AI-assisted checks against Saudi codes, client standards, and workplace guidelines.
3. **Manual Review & Annotation** – Overlay comments, markups, and suggested fixes directly on drawings.
4. **Issue Management & RFIs** – Categorize findings (Critical/Major/Minor), assign to consultants, and track responses.
5. **Stakeholder Reporting** – Summarize status for executives, highlight red flags, and export readiness reports.

## Platform Modules
| Module | Purpose | Key Capabilities |
| --- | --- | --- |
| Submission Intake | Centralizes consultant deliverables | Drag-and-drop upload, metadata capture (discipline, package stage, revision), auto file validation |
| Viewer & Annotation | Visual review of PDFs/DWGs | High-fidelity PDF viewer, layer toggling, comment pins, redlining, measurement tools, comparison overlay |
| Compliance Engine | Automates checks | Rule library for Saudi SBC, Civil Defense, MOMRAH, SEC; client guideline templates; AI-based anomaly detection |
| Checklist Workspace | Guides manual review | Discipline-specific smart checklists with pass/fail, auto-link to annotations, context tips |
| Issue Tracker | Manage RFIs | Severity tagging, impact description, proposed fix field, due dates, status updates, notification engine |
| Reporting & Dashboards | Executive visibility | Pre-submission readiness score, exportable summaries, trend charts for RFIs |
| Integration Layer | Connects ecosystem | API/webhooks for Procore, BIM360, SharePoint; Single Sign-On; audit logs |

## User Journeys
1. **New Package Submission**
   - Consultant uploads PDF set → system auto-parses sheet index → assigns to project → triggers compliance pre-check.
   - Reviewer receives notification with AI summary of potential issues.
2. **Focused Design Review**
   - Reviewer opens package in viewer → selects Architecture checklist → steps through items while annotating drawings.
   - Issues logged in Issue Tracker with severity and recommended fix.
   - Platform suggests reference to relevant Saudi code clause.
3. **RFI Resolution Loop**
   - Consultant responds to assigned issue → uploads revised sheet → system highlights delta regions → reviewer validates closure.
   - Status updates tracked, and unresolved critical items escalate automatically.
4. **Stakeholder Update**
   - Reviewer generates readiness report summarizing compliance score, outstanding RFIs, and decision (Approve / Approve with Comments / Reject).
   - Report shared with client executives and archived.

## Compliance & Standards Management
- Maintain centralized libraries for:
  - **Saudi Codes:** SBC (building/fire), Civil Defense, MOMRAH zoning, SEC electrical, accessibility requirements.
  - **Client Standards:** Configurable templates reflecting corporate workplace guidelines (branding, spatial standards, finishes).
  - **Best Practice Benchmarks:** Ergonomics, sustainability, smart workplace provisions.
- Rule editor enabling localization per project (e.g., Aramco vs NEOM).
- Version control for regulatory updates with effective dates.

## Automation Opportunities
- Auto-detection of egress path widths, fire compartmentation, and HVAC zoning using computer vision on PDFs/IFC.
- Natural language extraction of schedule data for verifying room program compliance.
- Severity scoring model using historical RFI closure times.
- Suggested fixes generated from knowledge base (e.g., "Increase fresh air rate to meet SBC 801.4 – 10 L/s per person").

## Security & Governance
- ISO 27001 aligned controls, role-based access (Owner, Consultant, Contractor), project-level permissions.
- Encrypted storage (at rest & in transit), watermarking, and activity logs.
- Saudi data residency compliant deployment option (e.g., AWS Mecca region).

## Technology Stack (Reference)
- **Frontend:** React (TypeScript), PDF.js with DWG support via WebAssembly viewer, TailwindCSS for rapid UI.
- **Backend:** Node.js (NestJS) or Python (FastAPI) microservices, orchestrated via Kubernetes.
- **Data Layer:** PostgreSQL for transactional data, Elasticsearch for full-text search, object storage (S3 compatible) for files.
- **AI/ML Services:** Python services with PyTorch, integrated with rule engine, using GPU-enabled nodes for model inference.
- **Integrations:** REST/GraphQL APIs, webhooks, SSO via Azure AD.

## Roadmap (High-Level)
1. **MVP (0-3 months)**
   - Submission intake, PDF viewer with annotation, manual checklists, basic issue log, exportable RFI report.
2. **Phase 2 (3-6 months)**
   - Automated compliance checks, Saudi code rule library, delta comparison, dashboarding.
3. **Phase 3 (6-12 months)**
   - AI-driven insights, predictive severity scoring, integrations with Procore/BIM360, localized data residency.

## Success Metrics
- Reduce review turnaround time by 40% compared to email-based workflow.
- Achieve >85% first-submission compliance after Phase 2.
- Maintain <5% overdue critical RFIs per project.
- User satisfaction (CSAT) >4.5/5 among Owner's Representative reviewers.

## Next Steps
1. Validate requirements with target Senior Design Managers and consultants.
2. Prototype viewer/annotation workflow using sample PDF set.
3. Define rule library structure with code consultants.
4. Prioritize integrations based on client ecosystem (e.g., Aramco vs PIF assets).

