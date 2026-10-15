# Product concepts and simulation assumptions

This project loosely reflects metadata-driven document systems. It does not implement M-Files, reproduce its schema, call proprietary APIs or claim these fixtures describe an actual vault.

## Limited product behaviour confirmed in documentation

Consulted the official M-Files user guide on 2026-10-15:

- Object metadata includes properties such as class, name and creation date, and helps users find objects. [Object metadata](https://www.userguide.m-files.com/user-guide/latest/eng/object_metadata.html).
- Workflows model document lifecycles, and an object can have a workflow and workflow state. [Workflows](https://www.userguide.m-files.com/user-guide/latest/eng/using_workflows.html).
- Object permissions include read access and can be influenced by multiple sources. The effective result can restrict access beyond the object's own permission settings. [Object permissions](https://www.userguide.m-files.com/user-guide/latest/eng/object_permissions.html).

These facts motivate checking metadata, lifecycle and access independently. They do not validate the particular incident, fixture fields, permission algorithm or retrieval semantics below. The linked `latest` documentation may change.

## Deliberate fictional rules

| Area | This demonstration assumes |
| --- | --- |
| Business environment | One invented housing organisation with stable property, apartment and agreement identifiers. No tenant or real company data. |
| Candidate discovery | An investigator's pre-exported evidence can be searched by a shared agreement ID independently of the apartment filter. ID mapping is declared, not externally verified. |
| Retrieval | The requester's view asks for rental agreements attached to the requested apartment, in the approved state, with read access. This is one fictional view, not a claim about all searches. |
| Typed metadata | Local class declarations validate the small set of fixture values. These declarations are our own JSON format. |
| Access | Explicit role denial takes precedence over role allowance; no allowance means no access. This small rule does not implement M-Files effective permissions, ACL inheritance or production authorisation. |
| Investigator scope | The evidence export has already been authorised for the fictional investigator. The program does not authenticate users, elevate privileges or obtain protected records. Reports are for that investigator, not the requester. |
| Workflow | An approval event and current state are recorded observations in a frozen snapshot. No cryptographic signature or independent approval verification is claimed. |
| ERP comparison | ERP is nominated as a comparison reference for the first case, requiring human verification. For the authority control, neither source is nominated. Neither choice permits automated correction. |
| Content | Small text files demonstrate that content bytes exist. They are not signed agreements and intentionally do not independently establish the correct apartment. |
| Time | Fixed snapshot dates describe a reproducible scenario, not current live truth. There is no polling or synchronisation. |
| Provenance | Source IDs, locators and hashes let a reader trace each observation to preserved synthetic bytes. Authenticity of a real external source remains outside scope. |

## Interpretation limits

A relationship disagreement is confirmed when two corresponding snapshot records differ. Its cause remains unknown: a document selection error, stale ERP data, an incorrect cross-system mapping or an unrecorded amendment may explain it. The demonstration cannot establish which event happened, who caused it or when.

The first case's observed approval and requester access eliminate two blockers in the simulated view. They do not prove legal validity, complete metadata accuracy or entitlement to change the document. A human must verify authority and supporting evidence through the organisation's existing process.
