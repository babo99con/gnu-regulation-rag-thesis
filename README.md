# Design and Evaluation of a Time-Aware RAG Question-Answering System for Evolving University Academic Regulations

## A Case Study of Graduate-School Regulations at Gyeongsang National University

## Abstract

Generative artificial intelligence and large language models (LLMs) are increasingly being adopted as assistants in educational and administrative work. University academic regulations, however, are distributed across university rules, graduate-school regulations, degree-conferral regulations, departmental bylaws, implementation guidelines, and official notices. In addition, the regulation applicable to a particular student may differ according to admission year, department, degree program, and reference date. An LLM used without external evidence may generate nonexistent provisions or rely on knowledge that predates the latest amendment. A conventional retrieval-augmented generation (RAG) system can reduce this problem, but it can still retrieve an obsolete provision when current and previous versions coexist in the same vector database.

This study proposes a time-aware RAG question-answering system for graduate-school regulations at Gyeongsang National University. The system manages regulation titles, article identifiers, promulgation dates, effective periods, revision status, applicable organizations, admission-year conditions, and official source URLs as structured metadata. It detects changes in source documents, incrementally re-embeds modified provisions, and preserves previous versions for historical questions. At query time, the system extracts temporal and organizational conditions from the user's question and retrieves evidence by considering both semantic relevance and temporal validity. When evidence is insufficient or conflicting, the system abstains from providing a definitive answer and instead presents the relevant provisions and official sources.

The proposed method will be evaluated against an LLM-only baseline, a conventional RAG system, and a metadata-filtered RAG system. Evaluation criteria will include retrieval accuracy, answer correctness, temporal applicability accuracy, citation correctness, hallucination rate, appropriate abstention rate, and update efficiency. The expected contribution is a reproducible method for providing evidence-grounded and temporally valid answers in a university regulatory environment where documents continually evolve.

**Keywords:** Large Language Model, Retrieval-Augmented Generation, Academic Regulations, Temporal Retrieval, Version-Aware RAG, Vector Database, Hallucination, Question Answering

---

# Chapter 1. Introduction

## 1.1 Background and Motivation

The use of LLM-based assistants is expanding in education and administrative work because users can obtain information through natural-language questions instead of manually searching multiple websites and documents. This capability is particularly valuable for university academic administration, where relevant information is often dispersed across many regulations and notices.

Gyeongsang National University announced a phased plan to establish an AI-focused college beginning in the 2027 academic year. Such organizational restructuring may lead to the integration of departments, the introduction of new curricula, and the enactment or amendment of related academic regulations. As the number of rules and their revision histories increase, students and university staff may find it more difficult to identify the latest provision applicable to a specific case.

Academic regulations differ from general knowledge because both correctness and temporal applicability are essential. Requirements relating to course registration, graduation, scholarships, leaves of absence, degree theses, and degree conferral may vary by department, program, admission year, and transitional provision. An incorrect answer can therefore cause practical administrative confusion rather than merely produce an inaccurate factual statement.

An LLM used alone may not know regulations issued after its training cutoff and may hallucinate provisions that do not exist. RAG can mitigate this limitation by retrieving external documents and supplying relevant passages to the model. Nevertheless, semantic similarity alone does not guarantee that a retrieved provision is currently valid. When obsolete and current regulations coexist in a vector database, conventional RAG may retrieve the obsolete version because its wording is highly similar to the question.

For reliable regulatory question answering, the system must determine not only whether a passage is relevant but also whether it was effective on the date referenced by the question, whether it applies to the user's organization and program, and whether it has been superseded. This study therefore proposes and evaluates a time-aware RAG system that incorporates amendment history and applicability conditions directly into retrieval and answer generation.

## 1.2 Research Objectives

This study has the following objectives:

1. Construct a structured corpus of graduate-school regulations from official Gyeongsang National University sources.
2. Design a metadata model containing regulation title, provision identifier, promulgation date, effective period, revision status, applicable organization, admission-year condition, and official source.
3. Implement a change-detection and incremental-indexing pipeline that re-embeds only added or modified provisions while preserving previous versions.
4. Propose a time-aware retrieval method that considers semantic relevance, temporal validity, and applicability conditions.
5. Compare the proposed method with LLM-only and conventional RAG baselines through quantitative and qualitative evaluation.

## 1.3 Research Questions

- **RQ1.** To what extent does conventional RAG improve the correctness and hallucination rate of university-regulation question answering compared with an LLM-only approach?
- **RQ2.** Does time-aware RAG improve applicability accuracy when current and obsolete versions of a regulation coexist in the knowledge base?
- **RQ3.** How do metadata filters for organization, degree program, admission year, and reference date affect retrieval and citation accuracy?
- **RQ4.** Can incremental indexing reduce update time and embedding workload while maintaining retrieval performance compared with complete re-indexing?
- **RQ5.** Can an evidence-based abstention policy reduce unsupported definitive answers in cases involving insufficient or conflicting evidence?

## 1.4 Scope and Method

The initial scope is limited to graduate-school graduation and degree-thesis regulations. Candidate documents include university rules, graduate-school academic regulations, degree-conferral regulations, thesis submission and examination guidelines, research-ethics rules, master's thesis-replacement requirements, departmental bylaws, and related official notices.

Documents will be collected only from official university sources. Each answer in the evaluation dataset will be paired with a verified provision and source. Where a question requires administrative interpretation beyond the written rule, the gold-standard answer will indicate that confirmation by the responsible university office is required.

The system will consist of a local LLM, an embedding model, persistent relational and vector storage, a hybrid retriever, a metadata and temporal filtering layer, a reranker, and an API service. The proposed method will be evaluated against multiple baselines using a shared set of questions.

## 1.5 Thesis Organization

Chapter 1 introduces the research problem, objectives, questions, and scope. Chapter 2 reviews LLM hallucination, RAG, vector databases, regulatory question answering, and temporal retrieval. Chapter 3 analyzes the academic-regulation corpus and presents the proposed system design. Chapter 4 describes implementation details. Chapter 5 reports the experimental design, results, and error analysis. Chapter 6 summarizes the findings, contributions, limitations, and future work.

---

# Chapter 2. Background and Related Work

## 2.1 Large Language Models and Hallucination

This section will cover:

- The basic mechanism by which LLMs generate responses.
- Limitations arising from training-data cutoff dates.
- The definition and types of hallucination.
- Risks of unsupported answers in academic, legal, and administrative domains.

## 2.2 Retrieval-Augmented Generation

This section will cover:

- The motivation for RAG.
- The roles of retrieval, augmentation, and generation.
- Document loading, chunking, embedding, retrieval, and answer generation.
- Differences among RAG, prompt engineering, and fine-tuning.

## 2.3 Embeddings and Vector Databases

This section will cover:

- Representation of natural language as high-dimensional vectors.
- Semantic similarity and cosine distance.
- The distinction between an in-memory vector store and a persistent vector database.
- The role of metadata filtering.
- The fact that a vector database stores and retrieves data but does not independently determine whether a regulation is current or legally applicable.

## 2.4 Question Answering over Regulatory Documents

Regulatory documents have structural and semantic characteristics that differ from ordinary unstructured text. Provisions are organized into articles, paragraphs, items, appendices, and supplementary provisions. A correct answer may require evidence from more than one regulation, and a relevant passage may not be applicable to every user. Regulatory QA must therefore evaluate evidence completeness, authority, applicability, and traceability in addition to semantic relevance.

## 2.5 Temporal and Version-Aware RAG

This section will examine:

- Interference caused by obsolete information in a RAG knowledge base.
- Promulgation, effective, amendment, and repeal dates.
- Temporal alignment between a query and a document version.
- Preservation of historical versions for retrospective questions.
- Incremental indexing and change tracking.

## 2.6 Research Gap and Distinction of This Study

Conventional RAG primarily ranks passages according to semantic relevance. In university-regulation QA, however, the most semantically similar passage may be an obsolete version or may apply to a different department, degree program, or admission cohort. This study explicitly models temporal validity and applicability during retrieval. It also integrates document-change detection, version preservation, incremental indexing, citation generation, and abstention into a single reproducible pipeline.

---

# Chapter 3. Corpus Analysis and System Design

## 3.1 Target Regulation Corpus

The corpus should not indiscriminately include every university regulation. Adding unrelated regulations increases retrieval noise and makes the experimental scope difficult to reproduce. Documents are therefore divided into a primary corpus, a conditional corpus, and operational evidence.

### 3.1.1 Primary Corpus

The following documents are required for the first experiment.

| Priority | Document | Why It Is Required | Confirmed Official Source |
|---:|---|---|---|
| 1 | Gyeongsang National University Rules | Defines the university organization, degree programs, enrollment status, and the authority delegated to subordinate regulations | [Current university rules, effective February 27, 2026](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000153007) |
| 2 | Graduate School Academic Operation Regulations | Defines admission, registration, curricula, credit recognition, transfers, foreign-language examinations, and comprehensive examinations | [Current version, effective February 27, 2026](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000153021) |
| 3 | Graduate School Degree Conferral Regulations | Defines thesis eligibility, submission, examination, degree conferral, research-student registration, and thesis submission deadlines | [Current version, effective February 27, 2026](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000153023) |
| 4 | Graduate School Curriculum Operation Guidelines | Provides detailed rules for curriculum organization, course operation, and exceptions | [Version effective January 16, 2024](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000124943) |
| 5 | General Graduate School Thesis Qualification Examination Guidelines | Provides detailed procedures and exemption conditions for foreign-language and comprehensive examinations | [Version effective November 23, 2021](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000096213) |
| 6 | Research Ethics Regulations | Defines research-integrity obligations applicable to graduate students and thesis-related research | [Version effective February 28, 2025](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000139977) |
| 7 | Thesis Writing Guidelines and Templates | Defines the permitted thesis structure, formatting, forms, and submission conventions | [Graduate School guidelines and templates, June 13, 2025](https://www.gnu.ac.kr/graduate/na/ntt/selectNttInfo.do?bbsId=1215&mi=2382&nttSn=2326423) |
| 8 | Current Thesis Examination and Master's Alternative-Achievement Notices | Provides semester-specific dates, required forms, review procedures, and implementation details that may not appear in regulations | [Graduate School notices](https://www.gnu.ac.kr/graduate/na/ntt/selectNttList.do?bbsId=1212) |
| 9 | Department-Specific Graduation and Thesis Bylaws | Contains additional publication, authorship, language, presentation, and graduation requirements | Individual department websites or documents; a complete inventory must be created after the target department is selected |
| 10 | Historical Versions, Amendment Texts, and Supplementary Provisions | Enables version-sensitive questions, temporal conflict experiments, and provision-level change tracking | The history, amendment, comparison, and attachment tabs associated with each National Law Information Center regulation page |

The URL initially provided for this project is the Graduate School Academic Operation Regulations **effective January 16, 2024**, not the current 2026 version. It should be preserved as historical evidence rather than labeled as current:

- [Graduate School Academic Operation Regulations, effective January 16, 2024](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000124859)

This coexistence of a 2024 version and a 2026 version is an appropriate pilot case for evaluating whether a conventional RAG system retrieves an obsolete but semantically similar provision.

### 3.1.2 Additional Documents Required by Specific Questions

The following documents should be indexed only when their corresponding question types are included in the evaluation dataset.

| Conditional Document | Inclusion Condition | Official Source Example |
|---|---|---|
| Bachelor's-Master's and Bachelor's-Master's-Doctoral Integrated Program Regulations | Questions from students in an integrated degree program | [Integrated program regulations](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000130859) |
| Double Master's and Doctoral Degree Regulations | Questions involving jointly operated or international double-degree programs | [Double-degree regulations](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000091727) |
| Graduate Microdegree Guidelines | Questions involving graduate microdegrees and credit recognition | [Microdegree guidelines](https://www.law.go.kr/LSW/schlPubRulInfoP.do?schlPubRulSeq=2200000153039) |
| Full-Time Scholarship Conditions and Performance Obligations | Questions involving thesis eligibility restrictions for scholarship recipients | Graduate School scholarship notices and attached obligation forms |
| Completed-Student or Research-Student Registration Guidelines | Questions submitted after the ordinary thesis-submission period or after program completion | General graduate-school rules and any separately published implementation guidelines |
| Special Graduate School Academic Regulations | The research scope includes the education, public health, convergence, entrepreneurship, or another special graduate school | The applicable graduate school's regulation page; special-graduate-school rules must not be mixed with general-graduate-school rules without an organization filter |
| Research Integrity Committee Regulations | Questions require procedures for investigating research misconduct rather than general ethical duties | Official university or National Law Information Center regulation page when located and verified |
| Admission Guides by Academic Year | Admission-cohort applicability or program-entry conditions form part of the question | [Graduate School admission notices](https://www.gnu.ac.kr/graduate/na/ntt/selectNttList.do?bbsId=1206&mi=2314) |

### 3.1.3 Operational Evidence

Regulations define normative requirements, whereas notices describe how those requirements are implemented in a particular semester. The two types must be stored separately.

- Semester thesis-examination schedules.
- Application windows for thesis and alternative achievements.
- Foreign-language and comprehensive examination schedules.
- Required application forms and system-submission instructions.
- Department announcements that restate or supplement university-wide requirements.
- Contact information for the responsible administrative office.

Operational notices must include a publication date, target semester, responsible organization, and expiration or archival status. A notice must not override a higher-level regulation unless the regulation explicitly delegates the relevant detail.

### 3.1.4 Initial Exclusions

The following materials should be excluded from the first experiment unless a research question explicitly requires them:

- Regulations for unrelated undergraduate academic matters.
- Committee-operation regulations that do not affect student eligibility or procedures.
- Regulations belonging exclusively to a special graduate school outside the selected scope.
- News articles, unofficial blog posts, and student-community explanations as answer evidence.
- Draft amendments that have not been promulgated, except in a separately labeled amendment-analysis dataset.

### 3.1.5 Source Authority and Conflict Policy

Each collected item must be assigned both a `document_type` and an `authority_level`.

```text
Promulgated university rules
    -> promulgated university regulations
    -> officially issued guidelines
    -> department bylaws
    -> semester-specific official notices
    -> forms and explanatory material
```

When two sources conflict, the system must not resolve the conflict by vector similarity alone. It must compare authority, organization, promulgation status, effective period, and transitional provisions. Draft amendments and unofficial explanations may be used for analysis but must never be presented as current binding rules.

The final corpus scope must be fixed before evaluation so that the system is not tested against documents it was not designed to cover.

## 3.2 Data Collection and Preprocessing

```text
Official source discovery
    -> PDF, HWP, and HTML acquisition
    -> text and table extraction
    -> structural normalization
    -> article/paragraph/item segmentation
    -> appendix and supplementary-provision linking
    -> metadata generation
    -> embedding and indexing
```

Preprocessing must address the following questions:

- Should a chunk correspond to an article, paragraph, or semantic subsection?
- How should appendices and supplementary provisions be linked to the main body?
- How should multiple versions of the same regulation be identified?
- How should OCR and document-conversion errors be detected and corrected?

## 3.3 Metadata Model

```json
{
  "regulation_id": "GRAD-DEGREE-001",
  "regulation_name": "Graduate School Degree Conferral Regulations",
  "article": "Article 12",
  "paragraph": "Paragraph 2",
  "revision": 4,
  "promulgated_at": "2026-03-01",
  "effective_from": "2026-03-01",
  "effective_to": null,
  "status": "CURRENT",
  "organization": "Graduate School",
  "degree_type": "MASTER",
  "admission_year_from": 2026,
  "admission_year_to": null,
  "source_url": "https://official-source.example/regulation"
}
```

The relational layer should maintain document identity, version relationships, effective periods, and source provenance. The vector layer should store embeddings and searchable chunk metadata. Separating these responsibilities makes temporal validation explicit and auditable.

## 3.4 Change Detection and Incremental Update

```text
Scheduled source inspection
    -> source hash comparison
    -> new, modified, or removed document detection
    -> provision-level diff
    -> re-embedding of changed provisions
    -> effective_to update for superseded provisions
    -> registration of the new current version
    -> validation and update logging
```

The update interval alone does not guarantee freshness. Freshness depends on whether source changes are correctly detected, reviewed, versioned, embedded, and made available to the retriever. The study will therefore measure both update latency and update correctness.

## 3.5 Time-Aware Retrieval Method

```text
User question
    -> intent and applicability analysis
    -> extraction of organization, program, admission year, and reference date
    -> lexical and vector retrieval
    -> applicability and effective-period filtering
    -> relevance and recency reranking
    -> evidence-sufficiency and conflict assessment
    -> grounded answer generation or abstention
```

The retrieval score may be modeled as a weighted combination of semantic relevance, lexical relevance, temporal validity, organizational applicability, and source authority. Temporal validity should operate as a hard filter when the question provides an explicit reference date and as a ranked preference when the date is absent and the current rule is assumed.

## 3.6 Answer Policy

1. When evidence is sufficient, provide an answer together with the regulation title, provision, effective date, and official URL.
2. When several regulations are jointly required, identify the role of each source.
3. When current and previous versions conflict, state the respective effective periods and the applicable transitional provision.
4. When department, degree program, or admission year is required but missing, request the missing information.
5. When written evidence is insufficient, abstain rather than infer an unsupported administrative decision.

## 3.7 Proposed Architecture

```text
Client or Postman
        |
Spring Boot API Gateway
        |
FastAPI RAG Service
        |
Query Analysis and LCEL Pipeline
        |
Hybrid Retriever -------- Persistent Vector Database
        |                            ^
Temporal/Metadata Filter            |
        |                  Collection and Update Pipeline
Reranker and Evidence Validator
        |
Ollama Local LLM
        |
Answer, Applicable Provision, Effective Date, and Source
```

---

# Chapter 4. Implementation

## 4.1 Candidate Technology Stack

| Component | Candidate Technology |
|---|---|
| API gateway | Spring Boot |
| RAG API service | FastAPI |
| Pipeline composition | LangChain and LCEL |
| Local model runtime | Ollama |
| Answer-generation model | `qwen3:8b` or a model selected through preliminary testing |
| Embedding model | `nomic-embed-text` or a model selected through Korean retrieval evaluation |
| Vector database | pgvector, Qdrant, or Chroma |
| Regulation and version metadata | PostgreSQL |
| Evaluation and visualization | Python, pandas, and matplotlib |

The final technology choices should be based on reproducibility and experimental requirements. The use of a particular framework is not itself a research contribution.

## 4.2 Document Collector

The collector will:

- Discover and record official document URLs.
- Download source files and extract text and tables.
- Store collection time, source hash, and content type.
- Parse article-level structure.
- Produce a review queue for documents with extraction errors.

## 4.3 Indexing and Storage

The indexing pipeline will:

- Create one or more document chunks for each provision.
- Generate embeddings.
- Store vectors with searchable metadata.
- Link current and historical versions.
- Incrementally update only changed provisions.

## 4.4 Retriever and RAG Pipeline

The retrieval implementation will include:

- Lexical retrieval using BM25 or an equivalent method.
- Dense vector retrieval.
- Reciprocal-rank or weighted result fusion.
- Metadata and effective-period filtering.
- Reranking of the remaining candidates.
- Prompt construction using only validated evidence.

## 4.5 Citation and Abstention

Example successful response:

```json
{
  "answer": "The thesis submission requirement applicable to this student is ...",
  "confidence": 0.91,
  "applicable_date": "2026-03-01",
  "citations": [
    {
      "regulation": "Graduate School Degree Conferral Regulations",
      "article": "Article 12, Paragraph 2",
      "effective_from": "2026-03-01",
      "source_url": "https://official-source.example/regulation"
    }
  ],
  "abstained": false
}
```

Example abstention response:

```json
{
  "answer": "The applicable regulation cannot be determined without the admission year and department.",
  "citations": [],
  "abstained": true,
  "required_information": ["admission_year", "department"]
}
```

---

# Chapter 5. Experiment and Evaluation

## 5.1 Experimental Objectives

The experiments will determine whether the proposed system improves retrieval and answer reliability when regulations change over time. Retrieval and generation will be evaluated separately so that a correct answer produced from incorrect evidence is not counted as a fully successful result.

## 5.2 Compared Systems

| System | Description |
|---|---|
| Baseline A | Local LLM without retrieval |
| Baseline B | Conventional dense-vector RAG |
| Baseline C | RAG with organization, admission-year, and effective-date filters |
| Proposed | Version-aware RAG with change tracking, hybrid retrieval, reranking, citations, and abstention |

## 5.3 Evaluation Dataset

The target dataset size is 150 to 300 questions, subject to corpus size and expert-review capacity.

| Question Type | Example | Suggested Share |
|---|---|---:|
| Single-provision question | What are the thesis submission qualifications? | 25% |
| Multi-regulation question | What conditions jointly apply to graduation and thesis replacement? | 20% |
| Temporal or admission-cohort question | Which rule applies to a student admitted in 2025? | 20% |
| Current/obsolete conflict question | How did the requirement change after the amendment? | 15% |
| Department-specific question | Does this department impose an additional requirement? | 10% |
| Unanswerable question | A question unsupported by the collected regulations | 10% |

Each item should contain a question identifier, question type, reference date, applicable organization, degree program, admission cohort, gold answer, gold provision, and official source URL.

## 5.4 Evaluation Metrics

### Retrieval Metrics

- Recall@K
- Precision@K
- Mean Reciprocal Rank (MRR)
- Rate of retrieving the applicable current provision
- Rate of incorrectly retrieving an obsolete provision

### Answer Metrics

- Answer correctness
- Faithfulness to retrieved evidence
- Provision and citation correctness
- Temporal applicability accuracy
- Hallucination rate
- Appropriate abstention rate

### Update Metrics

- Change-detection accuracy
- Complete re-indexing time
- Incremental update time
- Number of regenerated embeddings
- Retrieval-performance change after update

### Optional Usability Metrics

- Answer comprehensibility
- Ease of verifying evidence
- Perceived trustworthiness
- Time saved compared with manual website search
- Differences between student and administrative-staff evaluations

## 5.5 Experimental Procedure

1. Construct gold answers and provisions with review by a person familiar with the regulations.
2. Submit the same question set to every compared system.
3. Store retrieved passages separately from generated answers.
4. Conduct automatic and human evaluation.
5. Analyze results by question category.
6. Perform focused error analysis for obsolete evidence, missing evidence, and cross-regulation questions.

## 5.6 Results Table Template

| System | Answer Accuracy | Temporal Accuracy | Citation Accuracy | Hallucination Rate | Abstention Accuracy |
|---|---:|---:|---:|---:|---:|
| LLM only | - | - | - | - | - |
| Conventional RAG | - | - | - | - | - |
| Metadata-filtered RAG | - | - | - | - | - |
| Proposed system | - | - | - | - | - |

## 5.7 Error Analysis Plan

- Failure to detect an explicit or implicit reference date.
- Retrieval of an obsolete provision with high semantic similarity.
- Failure to retrieve a supplementary or transitional provision.
- Confusion between university-wide and department-specific rules.
- Correct retrieval followed by an answer inconsistent with the evidence.
- Generation of an answer despite insufficient evidence.

---

# Chapter 6. Conclusion

## 6.1 Summary of Findings

This section will summarize the result of each research question after the experiments have been completed.

## 6.2 Expected Contributions

### Academic Contributions

- Define university-regulation QA as a retrieval problem involving continuously evolving documents.
- Propose retrieval that jointly considers semantic relevance and temporal applicability.
- Construct an evaluation dataset containing amendment history and applicability conditions.

### Practical Contributions

- Allow students and staff to verify answers through official provisions and source documents.
- Reduce update workload by reprocessing only changed provisions.
- Reduce unsupported administrative guidance through evidence-based abstention.

## 6.3 Limitations

- The initial corpus may cover only a subset of graduate-school regulations at one university.
- Written regulations cannot replace administrative interpretation by the responsible office.
- Gold-answer construction requires time from reviewers familiar with the regulations.
- The reasoning ability of a small local LLM may affect end-to-end performance.
- PDF, HWP, table, and OCR extraction errors may not be completely eliminated.

## 6.4 Future Work

- Expand the corpus to undergraduate and university-wide regulations.
- Test generalization on regulations from other universities.
- Add administrator review and regulation-change notifications.
- Provide personalized applicability checks using student-authorized academic attributes.
- Model authority and dependency relationships among regulations with a knowledge graph.
- Extend the system to multi-turn questions while preserving temporal and organizational context.

---

# Candidate References

The citation style and bibliographic details must be revised according to the graduate school's official thesis guidelines.

1. Gyeongnam Ilbo. "Gyeongsang National University Pursues Establishment of an AI College for the 2027 Academic Year." May 27, 2026.  
   https://www.gnnews.co.kr/news/articleView.html?idxno=637783
2. Lewis, P., et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *Advances in Neural Information Processing Systems*, 2020.  
   https://arxiv.org/abs/2005.11401
3. Ouyang, J., et al. "HoH: A Dynamic Benchmark for Evaluating the Impact of Outdated Information on Retrieval-Augmented Generation." *ACL*, 2025.  
   https://aclanthology.org/2025.acl-long.301/
4. Aushev, I., et al. "RAGulator: Effective RAG for Regulatory Question Answering." *RegNLP*, 2025.  
   https://aclanthology.org/2025.regnlp-1.18/
5. Quinn, D., et al. "Regulatory Question-Answering using Generative AI." *RegNLP*, 2025.  
   https://aclanthology.org/2025.regnlp-1.16/
6. Huwiler, D., Stockinger, K., and Furst, J. "VersionRAG: Version-Aware Retrieval-Augmented Generation for Evolving Documents." arXiv, 2025.  
   https://arxiv.org/abs/2510.08109

---

# Planned Appendices

## Appendix A. Evaluation Questions

Question ID, question type, reference date, applicability conditions, gold answer, gold provision, and source URL.

## Appendix B. Regulation Metadata Specification

Field name, data type, required status, definition, and example.

## Appendix C. Prompts

Prompts used for query analysis, grounded answer generation, conflict detection, citation formatting, and abstention.

## Appendix D. Reproducibility Information

Model versions, embedding model, vector-database configuration, retrieval parameters, software dependencies, and experimental hardware.

---

# Next Steps

- [ ] Confirm the final title and degree-program context with the advisor.
- [x] Verify the official Gyeongsang National University thesis template.
- [x] Create the pilot inventory of target regulations and official source URLs.
- [x] Confirm the availability of the 2024 and 2026 Academic Operation Regulation versions.
- [ ] Define copyright-compliant storage and redistribution rules for source files.
- [ ] Finalize research questions, baselines, and evaluation metrics.
- [ ] Recruit a reviewer familiar with graduate-school regulations.
- [ ] Select the persistent vector database after preliminary comparison.
- [ ] Create 30 pilot evaluation questions.
- [ ] Run a pilot comparison between conventional and time-aware RAG.
- [ ] Determine whether a usability study requires research-ethics or IRB review.

## Executable Corpus Notebooks

The original all-in-one validation notebook is divided into four small, ordered notebooks. They contain saved outputs and can be opened individually for inspection. No LLM, API key, or paid token is required.

1. [`notebooks/00_download_sources.ipynb`](notebooks/00_download_sources.ipynb) downloads missing documents from the official URLs in the manifest and verifies them immediately.
2. [`notebooks/01_validate_sources.ipynb`](notebooks/01_validate_sources.ipynb) checks the presence, byte size, SHA-256 digest, and file signature of all 16 documents.
3. [`notebooks/02_extract_source_text.ipynb`](notebooks/02_extract_source_text.ipynb) extracts HTML, PDF, DOCX, and HWPX text and displays short previews. It also identifies the legacy HWP file that requires a converter.
4. [`notebooks/03_compare_regulation_versions.ipynb`](notebooks/03_compare_regulation_versions.ipynb) confirms that the official 2024 and 2026 Graduate School Academic Operation Regulation texts are distinct.

Shared file and extraction functions are kept in [`src/pilot_corpus.py`](src/pilot_corpus.py), so each notebook contains only the code relevant to its own experiment.

Current saved result:

```text
Manifest entries: 16
Files present: 16
Size checks passed: 16
SHA-256 checks passed: 16
Text extraction succeeded: 15
Legacy HWP conversion required: 1
Extraction failures: 0
```

Install the notebook dependencies and execute the notebooks from the repository root:

```bash
python -m pip install -r requirements-notebook.txt
jupyter nbconvert --to notebook --execute --inplace notebooks/00_download_sources.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/01_validate_sources.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_extract_source_text.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_compare_regulation_versions.ipynb
```
