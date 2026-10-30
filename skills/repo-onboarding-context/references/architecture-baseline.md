# Architecture Baseline

**Version:** 1.0 — Draft
**Purpose:** Guide architecture mapping, review, and implementation across software projects.
**Audience:** Human developers and AI coding agents.

## 1. Scope and precedence

This document provides an **architecture baseline**, not a mandatory technology stack or directory template.

Apply it when mapping an existing repository, preparing or reviewing a software slice, implementing new capabilities, or assessing architectural boundaries and technical debt.

Follow this precedence:

1. Explicit user instructions and approved project decisions.
2. Project-specific architecture documents, ADRs, constraints, and accepted slice specifications.
3. This architecture baseline.
4. General framework conventions.

When instructions conflict, identify the conflict and its evidence. Do not silently replace an approved project decision with this baseline.

### Rule levels

- **MUST:** A requirement applicable when its stated conditions are met.
- **SHOULD:** The preferred approach; a documented, reasonable exception is acceptable.
- **MAY:** An option to consider when justified.
- **PROJECT-SPECIFIC:** Apply only when adopted by the project.
- **UNKNOWN:** Insufficient evidence; investigate or report uncertainty.

This standard does not retroactively declare all existing deviations defects. Evaluate their impact and the applicable project decisions first.

## 2. Architecture selection

### 2.1 Choose the simplest architecture that fits the problem

A project MAY use:

- **Clean Architecture / DDD:** Appropriate for complex, evolving business domains and long-lived products.
- **Modular monolith:** Appropriate when domain modules need clear boundaries but do not yet require independent deployment.
- **N-tier:** Appropriate for CRUD-heavy applications, outsourcing work, limited domain knowledge, or tight delivery timelines.
- **Hybrid:** Different services or modules MAY use different approaches when the boundaries and reasons are documented.
- **CLI, worker, or lightweight service:** Appropriate for focused tools and experiments.

Do not introduce microservices, message brokers, databases, enterprise identity, Kubernetes, or other infrastructure solely because they appear in another project.

### 2.2 Platform and vertical products

Where a project uses an ERP/platform model:

- Shared platform capabilities MUST remain reusable and domain-agnostic.
- Industry-specific modules MAY depend on platform capabilities.
- The platform MUST NOT depend on a specific vertical module.
- Each module SHOULD own its business rules and data boundaries.
- Cross-module communication SHOULD use explicit contracts, application APIs, or events according to the project's architecture.

A module boundary does not automatically imply a separate deployable service.

## 3. Repository discovery and mapping

Before categorizing a repository, inspect evidence such as:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, and applicable skill instructions.
- Project-specific architecture documents, ADRs, constraints, and delivery artifacts.
- `.sln`, `.slnx`, `.csproj`, project references, package references, and dependency registrations.
- Source files, namespaces, entry points, routes, and runtime configuration.
- `package.json`, Angular configuration, Python packaging files, Docker/Compose files, and test projects.
- CI configuration and deployment documentation.

Directory names are **hints**, not proof. For example, the same logical layer may appear as:

```text
src/Modules/Sales/Domain/
src/Sales/Sales.Domain/
src/Product.Domain/
src/Core/
```

A `Core` project may contain Domain, Application, or both. Identify its actual responsibilities and dependencies before assigning a category.

### Mapping output

| Field | Description |
|---|---|
| Component | Project, module, application, or service name |
| Path | Actual repository path |
| Responsibility | What the code demonstrably does |
| Logical layer | Domain, Application, Infrastructure, API/UI, worker, shared, or other |
| Runtime boundary | Whether it is independently deployed or hosted with others |
| Dependencies | Important project, package, service, and data dependencies |
| Evidence | File paths and relevant declarations |
| Confidence | Confirmed, inferred, or unknown |
| Applicable decisions | Relevant ADRs, constraints, or approved exceptions |

Do not invent missing components or treat an absent technology as a violation.

## 4. Backend: .NET

### 4.1 Clean Architecture profile

Apply the following dependency rules **when the project has adopted Clean Architecture**, unless an approved project decision specifies otherwise.

| Layer | Primary responsibilities | Expected dependencies |
|---|---|---|
| **Domain** | Business entities, value objects, domain rules, domain events, and domain-specific abstractions | Independent of Application, Infrastructure, and presentation |
| **Application** | Use cases, orchestration, commands/queries, validation, DTOs, and ports needed by use cases | Domain and appropriate abstractions; not Infrastructure implementations |
| **Infrastructure** | Persistence, external services, identity integrations, messaging, file/object storage, and implementation of ports | Application and/or Domain as required |
| **Presentation / API** | HTTP endpoints, request/response mapping, authentication/authorization integration, composition root | Application contracts and the dependencies needed to configure the host |
| **Worker / CLI** | Background or command-line entry points and composition | Application contracts and host configuration |

The API or host MAY reference Infrastructure **for dependency registration and composition**. Business behavior should still flow through the appropriate application or domain boundaries.

### 4.2 Dependency violations

For a project using Clean Architecture:

- Domain MUST NOT depend on Infrastructure, Application, API, a database provider, EF Core persistence, or concrete HTTP clients.
- Application MUST NOT depend on Infrastructure implementations.
- Infrastructure MUST NOT contain the only copy of essential business rules that belong to Domain or Application.
- Domain and Application MUST NOT require ASP.NET request/response types to express their business behavior.
- Circular project dependencies MUST be reported.

A confirmed Domain dependency on EF Core, a PostgreSQL provider, persistence-specific SQL, or an HTTP client/framework is normally a **high-severity finding**. Confirm it from project/package references and actual use; do not infer it from a filename alone.

Distinguish database-independent business concepts from database-specific code. A SQL string in a comment, documentation, or a test fixture is not by itself proof of a Domain dependency.

Severity depends on actual impact and project context. Report the evidence, dependency direction, consequences, and any approved exception.

### 4.3 Implementation guidance

- Keep API endpoints thin: validate and map transport input, invoke use cases, and map responses.
- Define external capabilities as ports in the appropriate inner layer; implement them at the infrastructure boundary.
- Use CQRS where it improves clarity. A specific mediator library is **not required**.
- Follow the project's approved transaction, validation, error-handling, and API contract conventions.
- When using DDD aggregates, modify aggregate children through their aggregate root where the project's domain model requires it.
- Avoid copying business rules into controllers, database access code, and frontend components.
- Prefer built-in .NET dependency injection unless the project has a justified need for another container.

### 4.4 N-tier profile

When the project has adopted N-tier, map its actual flow, commonly:

```text
Controller / Endpoint → Service → Repository / Data Access → Database
```

Check that controllers do not accumulate significant business and persistence logic; services own application/business operations; data access responsibilities are identifiable and testable; dependencies and error handling are consistent with project decisions; and the implementation remains refactorable.

Do not report the absence of Domain/Application projects as a Clean Architecture violation when N-tier is the approved architecture.

## 5. Frontend

### 5.1 Angular profile

Use the project's actual Angular version, workspace structure, component model, and state-management conventions. The following are common categories, not required paths:

| Category | Typical responsibility |
|---|---|
| `core/` | Application-wide services, authentication integration, guards, interceptors, and application configuration |
| `shared/` | Reusable presentation components, directives, pipes, and utilities |
| `features/` | Business features, feature routes, containers, feature services, and feature-specific state |
| API/data access | Typed API clients, request/response models, and data-access services |

A repository MAY use `apps/*/src/app/`, `src/app/`, Nx libraries, standalone components, or another documented layout.

- Keep feature boundaries understandable.
- Use typed contracts where practical.
- Do not rely on frontend guards as the sole authorization control.
- Avoid duplicating authoritative backend business rules in the UI.
- Use Angular signals, reactive forms, and other framework features according to the project's version and established conventions.

### 5.2 Other frontend technologies

React, Next.js, browser extensions, or other frontends MAY be used when selected by the project. Apply equivalent separation of concerns without forcing Angular paths or conventions onto them.

## 6. Identity, authorization, and multi-tenancy

### 6.1 Identity

Keycloak is a common IdP direction for systems in scope, but an existing project's approved identity design takes precedence.

When a project uses Keycloak:

- Use the project's approved realm and client configuration.
- Treat one realm per project as the current working convention where applicable.
- Do not assume that every tenant needs a separate realm.
- Browser applications SHOULD use the project-approved OIDC authorization flow, commonly Authorization Code with PKCE.
- APIs MUST validate access tokens and enforce authorization server-side.
- Issuer, audience, token lifetime, signing keys, and other validation settings MUST follow the project's security design.
- Do not place client secrets in browser applications.

### 6.2 Authorization

Where the project adopts application-managed permissions:

- Keycloak authenticates users and issues tokens.
- The application enforces its own roles, permissions, and resource-level access according to its approved model.
- UI visibility and route guards improve usability but do not replace API authorization.
- User provisioning and synchronization follow the project's explicit design.

### 6.3 Tenant isolation

When a system is multi-tenant:

- Document how tenant identity is established, propagated, and verified.
- Enforce tenant boundaries in backend operations and data access.
- Do not trust an unvalidated tenant ID supplied by the client.
- Define tenant isolation for database records, files, background jobs, caches, and events where those components exist.
- Test cross-tenant access failures and resource ownership.

A realm, an identity provider, an organization, and a tenant are different concepts. Their relationship is a **project-specific architectural decision**.

## 7. Data, messaging, and document storage

### 7.1 Persistence

PostgreSQL and EF Core are common choices in many projects, but are not mandatory for every repository.

When used:

- Keep persistence implementation in the appropriate data-access boundary.
- Use the project's migration and database provisioning process.
- Make transaction boundaries explicit for important operations.
- Protect tenant-scoped data and enforce relevant constraints.
- Treat schemas, ownership, and cross-module access as project-specific decisions.
- Do not assume that production migrations always run automatically at API startup.

Development exceptions, including a single privileged database account, MUST remain scoped to the approved environment and MUST NOT automatically become a production standard.

### 7.2 Messaging and background work

When using RabbitMQ, Kafka, workers, or other asynchronous processing:

- Document the producer, consumer, message contract, and ownership.
- Define failure handling, retry behavior, and idempotency where needed.
- Include tenant and correlation context when applicable and safe.
- Avoid coupling domain logic directly to a specific message broker.
- Use a queue only when asynchronous processing or decoupling is justified.

### 7.3 Document Platform

Where a project integrates with the Document Platform:

- Treat document ownership, metadata, binary storage, and versioning according to the approved service contract.
- Keep storage-provider details behind the appropriate boundary.
- Apply authorization and tenant checks to upload, download, and document operations.
- Handle file limits, validation, callback processing, and version changes according to the project specification.
- Do not assume every application stores document binaries in its own database.

MinIO, ONLYOFFICE, and PostgreSQL are existing project technologies; they are not mandatory for all document-related solutions.

## 8. Python and AI services

When a project includes Python or AI components:

- Separate API/transport, processing logic, provider integrations, and configuration according to the project's complexity.
- Keep AI provider and model choices configurable or replaceable where justified.
- Define input/output contracts between the AI service and business applications.
- Validate AI outputs before using them in business operations.
- Handle timeouts, errors, retries, and processing status according to the workflow.
- Do not log secrets or sensitive document content unnecessarily.
- Apply tenant and authorization controls where data crosses service boundaries.
- Record model/provider, input provenance, or processing version when required for traceability.
- Prefer deterministic processing where it meets the requirement; use AI where it adds value.

FastAPI, OCR, embeddings, pgvector, and external LLM APIs are options, not universal requirements.

## 9. Configuration, secrets, and infrastructure

### 9.1 Configuration and secrets

- Secrets MUST NOT be committed to source control.
- Local development MAY use ignored `.env` files, .NET user secrets, environment variables, or another approved mechanism.
- A committed `.env.example` MAY document required variable names using safe placeholder values only.
- Production secrets MUST use an appropriate deployment secret mechanism.
- Do not put credentials, tokens, or private keys into logs, evidence files, screenshots, or documentation.
- If a committed secret is discovered, report it as a security finding and follow the project's incident and credential-rotation process.

### 9.2 CI/CD

- For **GitHub Actions**, workflow files belong under `.github/workflows/`.
- Other CI systems MAY use their own configuration locations.
- Do not flag a repository merely because it does not use GitHub Actions.
- Pipelines SHOULD run checks appropriate to the project and protect credentials.
- Deployment configuration and release procedures follow the project's approved workflow.

### 9.3 Local development and production

- Windows, WSL2, Docker, and native services MAY coexist according to the project's documented setup.
- Do not assume every API or dependency must run in WSL2.
- Document required services, ports, startup commands, and configuration without exposing secrets.
- Production topology, reverse proxy, backups, monitoring, and recovery are project-specific decisions.
- Dockerized PostgreSQL, Keycloak, Redis, or RabbitMQ MAY be used when justified; none is mandatory solely because another project uses it.

## 10. Quality, observability, and delivery

### 10.1 Tests and verification

- Test important business behavior and boundary conditions.
- Use integration tests when behavior depends on persistence, service contracts, authorization, or infrastructure integration.
- Include tenant isolation and authorization tests when those controls are applicable.
- Run the checks required by the project and the current work item.
- Do not claim a test passed without execution evidence.

### 10.2 Observability

Where appropriate, provide structured logs with useful context; correlation or trace identifiers across relevant operations; health checks for operationally significant components; metrics and tracing according to the project's needs; and redaction of secrets and sensitive data.

OpenTelemetry, Jaeger, and specific logging products are optional unless the project has adopted them.

### 10.3 Delivery-First / DSK

When a repository uses DSK:

- Follow its existing commands, workflows, acceptance criteria, and autonomy policy.
- Preserve project-specific slice evidence and decision records.
- Separate implementation completion, review, verification, human acceptance, and release status as defined by that project.
- Do not invent a new delivery command or impose additional governance.
- Document architectural changes or exceptions in the project's existing decision mechanism.

## 11. Architecture review findings

Each finding SHOULD include:

1. **ID and severity.**
2. **Applicable rule or approved decision.**
3. **Evidence:** exact files, references, configuration, or behavior.
4. **Observed condition.**
5. **Impact:** why it matters in this project.
6. **Recommended action.**
7. **Confidence and verification limits.**
8. **Existing exception or decision**, if applicable.

Suggested severity:

| Severity | Typical meaning |
|---|---|
| **Critical** | Confirmed, immediate risk of serious security impact, data loss, or comparable production harm |
| **High** | Material boundary or security failure with significant impact |
| **Medium** | Meaningful maintainability, reliability, or consistency risk |
| **Low** | Localized issue with limited impact |
| **Observation** | Potential improvement or question without sufficient evidence of a defect |

Assign severity from actual impact and evidence. A convention mismatch alone is not automatically a security or critical finding.

Do not label a missing component as defective when the project does not require it.

## 12. Project examples and known exceptions

These are orientation examples. **Verify the current repository and project documents before relying on them.**

| Project | Relevant context |
|---|---|
| **SME ERP** | Modular monolith, domain modules, Clean Architecture/DDD, PostgreSQL, and tenant/permission concepts have been discussed. Apply its approved module and data boundaries. |
| **LawFirm_App** | .NET, Angular, PostgreSQL, Keycloak, application-managed permissions, and Document Platform integration. Its local PostgreSQL may run as a Windows service while Keycloak runs in WSL Docker. |
| **Document Platform** | Document/version metadata, object storage, ONLYOFFICE integration, and asynchronous document processing are project-specific concerns. |
| **Content_Collector** | .NET CLI and admin UI with delivery slices and evidence. Do not assume its architecture or dependencies match the ERP. |
| **Repo R&D Scout** | .NET CLI with PostgreSQL and approved runner boundaries. The single-role database decision is scoped to its stated environment. |
| **CPU-AI-Lab / Agent Engineering Labs** | Learning and experimental scope. Prefer minimal dependencies and respect CPU-only or lab-specific constraints. |
| **S4U Landing** | Frontend deployment and a separately planned backend form receiver. Do not infer that a backend exists or is deployed without evidence. |
