# Semester 2 Research & Dissertation Backlog

Semester 2 transitions the frozen v1.0 prototype into a formal experimental study and thesis publication.

---

## 🎯 Semester 2 Research Tasks

### 1. Controlled Experimental Sweeps (Weeks 1–6)
- [ ] **Confidence Threshold Sweep**: Sweep decision threshold from $0.50$ to $0.95$ in steps of $0.05$ to plot the **Automation Rate vs. Error Cost Trade-off Curve**.
- [ ] **Multi-Model Family Comparison**: Benchmark TF-IDF + Logistic Regression against Linear SVM, Random Forest, and lightweight Transformer / DistilBERT embeddings.
- [ ] **Ablation Studies**:
  - *Ablation 1*: Workflow without deterministic policy layer (Pure AI).
  - *Ablation 2*: Workflow without confidence-gated human escalation.
  - *Ablation 3*: Workflow without field-level extraction confidence.

### 2. Deep Robustness & Error Taxonomy (Weeks 7–10)
- [ ] **Distribution Shift Testing**: Evaluate system performance under unseen terminology, foreign currency formats, and multilingual invoices.
- [ ] **Statistical Significance Testing**: Perform paired McNemar's tests and calculate 95% bootstrap confidence intervals for classification accuracy and latency.
- [ ] **Human Review Workload Modeling**: Calculate operator resolution time and model queue congestion under varying burst workloads ($N=500, 1000, 5000$).

### 3. Thesis Writing & Defense Preparation (Weeks 11–16)
- [ ] Chapter 1: Introduction & Research Problem Formulation
- [ ] Chapter 2: Systematic Literature Review (RPA, IPA, Document Intelligence, HITL)
- [ ] Chapter 3: Methodology & Experimental Design
- [ ] Chapter 4: Architecture & Hybrid State Machine Design
- [ ] Chapter 5: Implementation Details & Technical Infrastructure
- [ ] Chapter 6: Experimental Results, Baseline Comparisons, and Ablation Findings
- [ ] Chapter 7: Discussion, Threats to Validity, and Operational Limitations
- [ ] Chapter 8: Conclusion & Future Research Directions
- [ ] Viva Presentation Slides & Reproducibility Archive Package
