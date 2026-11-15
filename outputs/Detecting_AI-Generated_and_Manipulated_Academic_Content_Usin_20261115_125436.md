## 1. Title
Detecting AI-Generated and Manipulated Academic Content Using Multimodal Deep Learning

## 2. Abstract
The increasing prevalence of AI-generated text and manipulated images in academic manuscripts necessitates robust detection mechanisms. Existing research primarily focuses on single modalities, leaving a critical gap in integrated multimodal detection. This proposal outlines a project to develop an end-to-end multimodal deep-learning framework capable of simultaneously identifying AI-generated text and image manipulation within academic documents. The proposed methodology involves assembling a novel dataset of synthetic PDF documents combining human and AI-authored texts with authentic and manipulated scientific images. A fusion model incorporating transformer and CNN encoders with cross-modal attention will be trained to flag suspect sections. Expected outcomes include a quantitative demonstration of improved detection through multimodal fusion, a publicly available benchmark dataset, and open-source code, addressing a significant challenge in maintaining academic integrity.

## 3. Introduction
The digital transformation of scholarly communication has brought unprecedented opportunities but also new challenges related to content authenticity. The rise of sophisticated AI text generation models and readily available image manipulation tools poses a significant threat to academic integrity. The ability to distinguish between human-authored, authentic content and AI-generated or manipulated material is becoming crucial for peer review, publication, and scientific trust. Current detection efforts are often fragmented, focusing on either text or images in isolation. This research proposes an integrated, multimodal approach to comprehensively assess the provenance and integrity of academic manuscripts.

## 4. Literature Review
The existing literature offers modality-specific approaches to content integrity. *Image Forensics: Detecting duplication of scientific images with manipulation-invariant image similarity* (arxiv.org/abs/1802.06515v3) presents a deep-learning model designed to identify manipulated or duplicated scientific images. This model is invariant to common transformations such as copy, rotation, scaling, and histogram adjustments, addressing a critical aspect of image authenticity. Complementing this, *The Effects of Assumed AI vs. Human Authorship on the Perception of a GPT-generated Text* (osf.io/wrusc) investigates how labeling influences the perceived credibility of AI-generated text. This experimental study highlights the human-perception dimension of AI authorship but does not offer an automated detection solution. While these papers address critical components, neither provides an integrated solution for multimodal academic document integrity.

## 5. Problem Statement and Research Gap
There is a clear **modality-specific focus** in current research, with image forensics and text perception being treated as separate problems without an integrated academic-document context. This leads to **data scarcity**, as no publicly available multimodal datasets exist that combine AI-generated text, manipulated images, and document layout. Consequently, **evaluation gaps** persist, with existing works evaluating only one modality, leaving cross-modal performance and real-world robustness untested. Furthermore, the limited search results suggest that **semantic relevance** in existing discovery tools is often keyword-overlap based, not guaranteeing peer-review status or quality.

A tentative research gap exists in the **lack of a multimodal deep-learning framework** that simultaneously detects AI-generated text *and* image manipulation within academic manuscripts. There is also a pressing need for **realistic, annotated datasets** that accurately reflect the joint distribution of text, images, and layout found in scholarly documents.

## 6. Objectives
The primary objective is to build an end-to-end system that flags suspect sections of an academic paper, including text, figures, figure captions, and overall layout.

## 7. Research Questions
*   **RQ1**: How well does a joint multimodal model outperform unimodal baselines on AI-generated text detection?
*   **RQ2**: What is the impact of image manipulation detection on overall document authenticity when combined with text-level cues?
*   **RQ3**: Can cross-modal attention learn consistent provenance signals across modalities?

## 8. Proposed Methodology
The proposed methodology will encompass data assembly, model architecture design, and a robust training strategy. For **data assembly**, the image-forensics dataset from arxiv.org/abs/1802.06515v3 will serve as a starting point for image samples. AI-generated scholarly texts (e.g., GPT-4 outputs) will be collected alongside human-authored excerpts from open-access journals. These will be rendered into synthetic PDF documents, preserving typical LaTeX layout, to create a comprehensive multimodal dataset. The **model architecture** will feature a text encoder (e.g., BERT or GPT-2) fine-tuned for authorship classification and an image encoder (e.g., ResNet-50) trained for duplication detection. A cross-modal fusion component, utilizing attention layers, will align image regions with surrounding captions and text. The output head will comprise binary classifiers for each document section and an overall document authenticity flag. The **training strategy** will employ a multi-task loss combining text and image predictions, alongside data augmentation for image transformations. Implementation will be in PyTorch, with a commitment to reproducible experiments and an open-source code plan.

## 9. Dataset Plan
No ready-made multimodal dataset matching the project's specific requirements was found in Hugging Face or OpenML. Therefore, a novel dataset pipeline is proposed:
1.  **Scraping**: Publicly available open-access articles (PDFs) will be scraped for authentic text and image content.
2.  **AI Text Generation**: AI-written sections will be generated using models like GPT-4, prompted to mimic academic writing styles, for insertion into documents.
3.  **Image Manipulation**: A subset of authentic images will be manipulated using techniques such as copy-paste, rotation, and scaling, guided by methods outlined in arxiv.org/abs/1802.06515v3.
4.  **Labeling**: Each document section (text, figure, figure caption) will be labeled as human/AI-authored or authentic/manipulated.
For **licensing**, CC-BY or public domain PDFs will be used, and synthetic data will be released under CC-0. A future plan involves soliciting community annotations via crowdsourcing platforms like Amazon MTurk to enhance dataset diversity and scale.

## 10. Evaluation Metrics
**Per-modality evaluation** will utilize Precision, Recall, and F1-score for AI-generated text detection and Precision, Recall, and F1-score for image duplication/manipulation detection. **Document-level evaluation** will assess overall system performance using Accuracy, ROC-AUC, and detection latency. **Robustness tests** will be conducted by evaluating the model under various image transformations (e.g., rotation, scaling) and paraphrasing of text to measure its resilience to minor alterations.

## 11. Expected Outcomes
The proposed work is expected to yield several significant outcomes:
*   **Quantitative Evidence**: Provide quantitative evidence demonstrating that multimodal fusion significantly improves the detection of AI-generated content and image manipulation compared to unimodal baselines.
*   **Benchmark Dataset**: Create and release a novel, annotated benchmark dataset for multimodal academic document integrity, released under a permissive license (CC-0), to facilitate future research.
*   **Open-Source Contributions**: Release open-source code and pre-trained models, ensuring reproducibility and enabling wider adoption and development within the research community.

## 12. Limitations and Risks
This proposal acknowledges several inherent limitations and risks. The primary risk is **overfitting** to synthetic manipulation patterns within the generated dataset; this will be mitigated through diverse data augmentation techniques. **Ethical concerns** regarding the mislabeling of legitimate AI-assisted research as deceptive are also present; transparency guidelines will be integrated into the system's output and interpretation. **Data privacy** concerns will be addressed by ensuring no proprietary text is included without explicit permission. Finally, the **limited evidence** from the literature review (only two papers, no direct multimodal dataset matches) introduces uncertainty regarding the completeness of prior work and the feasibility of a fully multimodal training pipeline; the proposed plan is provisional and will adapt as further sources become available.

## 13. References
*   Cicconet, M., Elliott, H., Richmond, D. L., Wainstock, D., & Walsh, M. (2018). *Image Forensics: Detecting duplication of scientific images with manipulation-invariant image similarity*. arxiv.org/abs/1802.06515v3
*   Lermann Henestrosa, A., & Kimmerle, J. (2024). *The Effects of Assumed AI vs. Human Authorship on the Perception of a GPT-generated Text*. osf.io/wrusc
