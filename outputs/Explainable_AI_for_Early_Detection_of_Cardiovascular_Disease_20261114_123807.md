## Research Proposal: Explainable AI for Early Detection of Cardiovascular Disease

### 1. Title
Explainable AI for Early Detection of Cardiovascular Disease: A Comparative and Clinical Validation Study

### 2. Abstract
Cardiovascular disease (CVD) remains a leading cause of mortality, with early detection critical for effective intervention. While AI models show promise in CVD prediction, their clinical utility is often limited by a lack of interpretability. Existing research primarily relies on a single Explainable AI (XAI) technique, SHAP, often applied to limited datasets and evaluated mainly on accuracy, without robust clinical validation. This proposed research aims to address these limitations by systematically comparing diverse XAI methods, evaluating their impact on clinician decision-making, and assessing model robustness across heterogeneous patient datasets and data modalities. The study will involve building machine learning and deep learning models, applying various XAI techniques, conducting a clinician-centric randomized controlled trial, and performing rigorous statistical analysis. Expected outcomes include identifying the most clinically actionable XAI methods, providing evidence of clinician benefit, and demonstrating enhanced model generalizability, thereby advancing the integration of trustworthy AI into clinical CVD detection pathways.

### 3. Introduction
Cardiovascular diseases (CVDs) pose a significant global health burden, necessitating accurate and timely diagnosis. Artificial Intelligence (AI) and machine learning (ML) models offer substantial potential for early CVD detection by identifying complex risk patterns from diverse data. However, the inherent "black-box" nature of many high-performing AI models hinders their adoption in clinical practice, where trust, transparency, and accountability are paramount. Explainable AI (XAI) seeks to bridge this gap by providing insights into model predictions, making them understandable to human experts. While initial studies have explored XAI for CVD, a comprehensive evaluation across different XAI techniques, varied datasets, and direct clinical impact remains underexplored. This proposal outlines a research plan to systematically investigate and validate XAI methods for early CVD detection, focusing on interpretability, clinical utility, and generalizability.

### 4. Literature Review
- *SHAP‑Based Explainable AI Model for Early Detection of Cardiovascular Disease* (Imran et al., 2025) proposes an ensemble ML framework with SHAP for CVD risk prediction. The study claims higher early‑detection accuracy and provides interpretable feature importance, leveraging a publicly available heart disease dataset. URL: <https://www.semanticscholar.org/paper/540b68818f48c4eed5968871a83acf126a69d451>
- *An Interpretable Approach with Explainable AI for the Detection of Cardiovascular Disease* (Sapra & Sapra, 2024) combines multiple classifiers with SHAP and other XAI tools. This work discusses model calibration, feature relevance, and the potential for XAI to support clinical decision-making. URL: <https://www.semanticscholar.org/paper/25c01730644742804e81fa99f2b8fd74880abbc9>

### 5. Problem Statement and Research Gap
Existing research in explainable AI for early CVD detection exhibits common themes and limitations. Both reviewed papers predominantly rely on SHAP for post-hoc explanations, showcasing limited methodological diversity in XAI techniques. They also share a dependence on a single public heart-disease dataset, with little discussion of data diversity or imbalance handling beyond ensemble strategies. Evaluation primarily focuses on accuracy-based metrics, with limited exploration of clinical utility metrics like sensitivity at low prevalence. The scope of validation is also confined to metadata verification, without confirmation of full-text accessibility or peer-review status.

Based on these observations, a **tentative research gap** is identified:
- **Limited methodological diversity:** There is a lack of systematic comparison among alternative XAI methods (e.g., LIME, Integrated Gradients) or deep learning-specific explanations.
- **Sparse clinical validation:** Few studies rigorously assess how explanations influence clinician decision-making or impact patient outcomes in a controlled setting.
- **Dataset heterogeneity:** Current works rely on a single dataset, leaving the generalizability of XAI models and their explanations untested across diverse populations and modalities (e.g., ECG, imaging).

### 6. Objectives
- **Objective 1:** Compare SHAP with other XAI techniques for interpretability and predictive performance in CVD risk models.
- **Objective 2:** Evaluate the impact of explanations on clinician workflow and decision quality.
- **Objective 3:** Assess model robustness across diverse datasets and patient demographics.

### 7. Research Questions
- **RQ1:** Which XAI method yields the most clinically actionable feature explanations?
- **RQ2:** Does providing model explanations improve diagnostic accuracy or reduce uncertainty among clinicians?
- **RQ3:** How do explanation fidelity and predictive performance vary with dataset heterogeneity?

### 8. Proposed Methodology
The proposed methodology involves several phases. First, data aggregation will combine publicly available CVD datasets (e.g., Framingham, MIMIC-III ECG, NHANES) and, if possible, obtain de-identified patient records under IRB approval. Second, model training will involve building baseline models, such as logistic regression, random forest, and XGBoost, alongside deep learning architectures like Convolutional Neural Networks (CNNs) for ECG data and Multilayer Perceptrons (MLPs) for tabular data. Third, XAI application will systematically apply SHAP, LIME, Integrated Gradients, and counterfactual explanations to each trained model. Fourth, a clinician study will be conducted as a randomized controlled trial, where cardiologists review cases with and without model explanations; their diagnostic decisions, confidence levels, and decision times will be recorded. Finally, statistical analysis will employ paired t-tests or Mann–Whitney U tests for accuracy differences, Cohen’s κ for inter-rater agreement among clinicians, and regression models to link explanation quality to observed improvements in clinical outcomes.

### 9. Dataset Plan
The primary source will be the public heart-disease dataset referenced in the two reviewed papers, serving as a baseline for comparison. Supplementary sources will include:
- **Framingham Heart Study (open access):** To incorporate demographic diversity and longitudinal data.
- **MIMIC-III (ECG signals):** To enable the evaluation of multimodal data inputs.
- **NHANES (National Health and Nutrition Examination Survey):** To integrate a broader range of laboratory and lifestyle variables.
Verification steps will confirm license terms, data quality, and target variable definitions for all selected datasets before use. No claim of download or validation has been made yet.

### 10. Evaluation Metrics
- **Predictive performance:** Area Under the Receiver Operating Characteristic curve (AUROC), sensitivity, specificity, precision, and F1-score will be used to assess model effectiveness.
- **Interpretability:** Explanation consistency (stability across similar inputs), human-readability (assessed via clinician surveys), and fidelity (correlation between feature importance and model prediction changes) will measure explanation quality.
- **Clinical impact:** Metrics will include changes in diagnostic accuracy, reduction in false positives and false negatives, decision time, and clinician confidence scores.
- **Generalizability:** Performance variance across diverse datasets and calibration curves for different demographic subgroups will be analyzed.

### 11. Expected Outcomes
The proposed research is expected to yield several key outcomes:
- **Identification of Effective XAI Methods:** The study will identify the most effective and clinically actionable XAI methods for CVD risk models, offering guidance for future AI development in healthcare.
- **Evidence on Clinician Benefit:** It will provide empirical evidence regarding the benefit of model explanations on clinician workflow, diagnostic accuracy, and decision confidence.
- **Demonstrated Model Robustness:** The research will demonstrate enhanced model robustness and explanation fidelity across heterogeneous datasets and diverse patient demographics, addressing generalizability concerns.

### 12. Limitations and Risks
- **Limited availability or accessibility of diverse datasets:** Obtaining access to comprehensive, high-quality, and ethically approved datasets with sufficient demographic diversity may pose a challenge.
- **Potential bias if datasets are not representative:** Reliance on available datasets, even aggregated, may still introduce biases if they do not adequately represent the global patient population for CVD.
- **Clinician recruitment challenges for the human-evaluation study:** Recruiting a sufficient number of cardiologists for a randomized controlled trial and ensuring their sustained engagement can be difficult.
- **Over-interpretation of SHAP or other explanations without clinical validation:** There is a risk that explanations, even well-intentioned, could be misinterpreted or over-relied upon by clinicians without thorough clinical validation of their utility and limitations.
- **Uncertainty Note:** The current evidence base from the initial literature review is small (two papers) and may not fully capture the breadth of XAI applications in early CVD detection. Further comprehensive literature scanning (e.g., PubMed, IEEE Xplore, medRxiv) is advised before finalizing the research design to ensure all relevant prior work is considered.

### 13. References
- Imran et al. (2025). *SHAP‑Based Explainable AI Model for Early Detection of Cardiovascular Disease*. URL: <https://www.semanticscholar.org/paper/540b68818f48c4eed5968871a83acf126a69d451>
- Sapra & Sapra. (2024). *An Interpretable Approach with Explainable AI for the Detection of Cardiovascular Disease*. URL: <https://www.semanticscholar.org/paper/25c01730644742804e81fa99f2b8fd74880abbc9>

---
### Review Notes

1.  **Literature Review Scope:** The initial search yielded only two papers from Semantic Scholar. While these were relevant, the "Uncertainty Note" in the Limitations and Risks section correctly highlights the need for further, broader literature scanning (e.g., PubMed, IEEE Xplore, medRxiv) to ensure a comprehensive understanding of the field before finalizing the research design. This is a critical item requiring human verification.
2.  **Dataset Suitability:** The "Dataset Catalog Matches" from the original research evidence included datasets (anneal, kr-vs-kp) that are not immediately relevant to cardiovascular disease. The "Dataset Plan" in the proposal correctly identifies this and proposes more appropriate supplementary datasets (Framingham, MIMIC-III, NHANES) for CVD research. However, the proposal notes "No claim of download or validation has been made yet" for these proposed datasets, which is an important item requiring human verification and action.
3.  **Peer-Review Status:** The "Scope of validation" in the Problem Statement notes that "Peer‑review status and full‑text accessibility not confirmed." This is a limitation of the initial evidence provided and would require human verification for the cited papers.
4.  **Clinical Validation:** The proposed methodology includes a "Clinician study" which directly addresses the identified research gap of "Sparse clinical validation." The feasibility of recruiting a sufficient number of cardiologists for this study is listed as a risk, requiring human oversight and resource allocation.
