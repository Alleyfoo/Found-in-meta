# Found in Meta

**The document exists. So why can't anyone find it?**

### The problem

Modern document management systems don't necessarily organise files into folders. Instead, documents are connected to business objects through metadata: customers, properties, contracts, projects and workflows.

This makes information easier to organise and retrieve, but introduces a different kind of problem.

A document can exist, have valid metadata, be approved and still be missing from the user's view.

What happens when the file isn't lost, but the relationship used to retrieve it doesn't match the expected one?

### The investigation

Found in Meta explores this problem using a fictional housing organisation and a metadata-driven document repository.

A property manager reports that an approved rental agreement for Apartment A14 cannot be found.

The investigation examines the document, its relationships, its workflow state, the requester's access permissions and the corresponding ERP record.

**The findings:**

- The agreement exists in the document repository.
- Its workflow state is approved.
- The requester has read permission.
- The agreement is linked to Apartment A41.
- The ERP record associates the agreement with Apartment A14.
- The apartment-based document view therefore excludes the agreement.

The document isn't missing. The available records disagree about where it belongs.

But identifying the discrepancy doesn't establish which system contains the correct information.

### Testing different explanations

The project also includes controlled cases to distinguish between different causes of an apparently missing document.

| Scenario | Investigation result |
| --- | --- |
| Relationship mismatch | Document excluded from the expected view. |
| Access permission problem | Correct document exists but requester cannot read it |
| Conflicting source records | Correct relationship cannot be established |
| Correct configuration | Document is retrieved successfully |

The investigation checks each explanation independently rather than treating every missing document as a metadata error.

### Evidence before correction

Each investigation produces a readable report and a portable JSON evidence bundle.

The evidence includes the original complaint, source identifiers, observed metadata, relationship checks, workflow state, permission checks, confirmed findings and unresolved questions.

Source files are preserved with SHA-256 hashes so that the investigation can be reproduced.

**The investigator does not modify the document.**

Instead, it identifies what has been established, what remains uncertain and which decision requires an authorised person.

This matters because correcting the wrong relationship could create new problems with document visibility, access rights or business records.

### Implementation

Found in Meta is a small, read-only Python project with deterministic synthetic data.

- Four investigation scenarios
- 34 passing automated tests
- Reproducible evidence and reports
- No external services or AI model dependency
- No automatic changes to source systems

The project is inspired by metadata-driven document management concepts, including those used by M-Files. It does not connect to M-Files or reproduce its internal implementation.

### What this demonstrates

The experiment illustrates a fundamental difference between storing information and being able to retrieve the correct information.

A document can pass metadata validation while its business relationships remain disputed.

Metadata is therefore not merely descriptive information. In a metadata-driven system, it can influence navigation, retrieval, permissions and workflows.

Reliable document management requires more than checking whether files exist. It requires understanding the relationships that make those files meaningful.

**Found in Meta investigates those relationships, preserves the evidence and leaves the decision to the people responsible for the data.**

---

**Repository:** [Alleyfoo/Found-in-meta](https://github.com/Alleyfoo/Found-in-meta)

*Independent synthetic case study. Not affiliated with M-Files or any housing organisation.*
