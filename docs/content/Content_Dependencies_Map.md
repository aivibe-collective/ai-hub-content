# Content Dependencies Map

This document provides a visual representation of the dependencies between key content items in the AI Community & Sustainability Hub. Understanding these dependencies is crucial for planning the development sequence and identifying critical path items.

## Learn AI - Beginner Track Dependencies

```
                                                  ┌─────────────┐
                                                  │ LRN-BEG-001 │
                                                  │ What is     │
                                                  │ Generative  │
                                                  │    AI?      │
                                                  └──────┬──────┘
                                                         │
                 ┌─────────────────┬─────────────────────┼─────────────────┬─────────────────┐
                 │                 │                     │                 │                 │
        ┌────────▼─────────┐      │             ┌───────▼────────┐ ┌──────▼───────┐ ┌───────▼────────┐
        │   LRN-BEG-002    │      │             │  LRN-BEG-003   │ │  LRN-BEG-009 │ │  LRN-BEG-013   │
        │ Types of Gen AI  │      │             │ Traditional ML │ │  GenAI Apps  │ │ Understanding  │
        │     Models       │      │             │   vs GenAI     │ │  & Use Cases │ │  AI Bias       │
        └────────┬─────────┘      │             └───────┬────────┘ └──────┬───────┘ └───────┬────────┘
                 │                │                     │                 │                 │
                 │         ┌──────▼───────┐             │                 │          ┌─────▼──────┐
                 │         │  LRN-BEG-018 │             │                 │          │ LRN-BEG-014│
                 │         │   Sandbox    │             │                 │          │ Detect Bias│
                 │         │  Activities  │             │                 │          │ in Dataset │
                 │         └──────────────┘             │                 │          └────────────┘
                 │                                      │                 │
        ┌────────▼─────────┐                           │          ┌──────▼───────┐
        │   LRN-BEG-004    │                           │          │  LRN-BEG-010 │
        │  Intro to LLMs   │                           │          │   Practical  │
        │    and SLMs      │                           │          │  Examples in │
        └────────┬─────────┘                           │          │     SMEs     │
                 │                                      │          └──────┬───────┘
                 │                                      │                 │
        ┌────────▼─────────┐                    ┌───────▼────────┐      │
        │   LRN-BEG-005    │                    │  LRN-BEG-007   │      │
        │ How Foundation   │                    │  The Gen AI    │      │
        │ Models are Trained│                    │     Stack      │      │
        └────────┬─────────┘                    └────────────────┘      │
                 │                                                      │
        ┌────────▼─────────┐                                     ┌──────▼───────┐
        │   LRN-BEG-006    │                                     │  LRN-BEG-011 │
        │   Customizing    │                                     │ From Sandbox │
        │ Foundation Models│                                     │ to Production│
        └────────┬─────────┘                                     └──────┬───────┘
                 │                                                      │
                 │                                                      │
        ┌────────▼─────────┐                                     ┌──────▼───────┐
        │   LRN-BEG-008    │                                     │  LRN-BEG-012 │
        │  Most Popular    │                                     │ Create Your  │
        │      LLMs        │                                     │ Business AI  │
        └──────────────────┘                                     │   Roadmap    │
                                                                 └──────────────┘
```

## Apply AI Section Dependencies

```
                                     ┌─────────────────────────────────────┐
                                     │           Learn AI Track            │
                                     │ LRN-BEG-009, LRN-BEG-010, LRN-BEG-012│
                                     └──────────────────┬──────────────────┘
                                                        │
                     ┌───────────────────┬──────────────┴───────────────┬───────────────────┐
                     │                   │                              │                   │
           ┌─────────▼─────────┐ ┌───────▼───────┐            ┌─────────▼─────────┐ ┌───────▼───────┐
           │    APP-SME-001    │ │  APP-SME-002  │            │    APP-SME-004    │ │  APP-SME-005  │
           │  Retail Sector    │ │  Agriculture  │            │    Healthcare     │ │   Logistics   │
           │    AI Playbook    │ │    Sector     │            │      Sector       │ │    Sector     │
           └───────────────────┘ │  AI Playbook  │            │    AI Playbook    │ │  AI Playbook  │
                                 └───────────────┘            └───────────────────┘ └───────────────┘


           ┌───────────────────┐ ┌───────────────────┐        ┌───────────────────┐
           │    APP-TMP-001    │ │    APP-TMP-002    │        │    APP-TMP-003    │
           │  AI ROI Calculator│ │  Low-code & Zapier│        │   Ethics Audit    │
           │      for SMEs     │ │  AI Workflows     │        │     Checklist     │
           └───────────────────┘ └───────────────────┘        └───────────────────┘
                     ▲                     ▲                            ▲
                     │                     │                            │
                     │                     │                            │
                     └─────────────────────┴────────────────────────────┘
                                           │
                                           │ Used by
                                           │
                     ┌───────────────────┬─┴─────────────────┬───────────────────┐
                     │                   │                   │                   │
           ┌─────────▼─────────┐ ┌───────▼───────┐  ┌───────▼───────┐  ┌────────▼──────┐
           │    APP-CST-001    │ │  APP-CST-002  │  │  APP-CST-003  │  │  Other Case   │
           │  AI-Powered       │ │  Sustainable  │  │  AI-Enhanced  │  │   Studies     │
           │  Inventory Mgmt   │ │  Supply Chain │  │  Customer Svc │  │               │
           └───────────────────┘ └───────────────┘  └───────────────┘  └───────────────┘
```

## Responsible AI & Sustainability Dependencies

```
           ┌───────────────────┐                            ┌───────────────────┐
           │    LRN-BEG-013    │                            │    RAS-ETH-002    │
           │  Understanding    │                            │  Energy + Carbon  │
           │  AI Bias & Fairness│                            │  Tracking Tools   │
           └─────────┬─────────┘                            └───────────────────┘
                     │                                                ▲
                     │                                                │
                     ▼                                                │
           ┌───────────────────┐                            ┌─────────┴─────────┐
           │    RAS-ETH-001    │                            │    LRN-EXP-001    │
           │  Design → Dev →   │                            │Model Quantization │
           │   Deploy Path     │                            │   and Pruning     │
           └───────────────────┘                            └───────────────────┘


           ┌───────────────────┐                            ┌───────────────────┐
           │    RAS-GOV-001    │                            │    RAS-GOV-002    │
           │  EU AI Act        │                            │  GDPR & Privacy   │
           │    Summary        │                            │     Toolkit       │
           └───────────────────┘                            └───────────────────┘
```

## Community & Platform Dependencies

```
           ┌───────────────────┐
           │    HOM-MIS-001    │
           │      Mission      │
           │     Statement     │
           └─────────┬─────────┘
                     │
                     ▼
           ┌───────────────────┐                            ┌───────────────────┐
           │    HOM-CTA-001    │                            │    MOD-COC-001    │
           │  Getting Started  │                            │  Community Code   │
           │   with the Hub    │                            │    of Conduct     │
           └─────────┬─────────┘                            └─────────┬─────────┘
                     │                                                │
                     ▼                                                ▼
           ┌───────────────────┐                            ┌───────────────────┐
           │    COM-FOR-001    │                            │    COM-EVT-001    │
           │  Getting Started  │─────────────────────────────▶ AI Implementation │
           │      Forum        │                            │   Office Hours    │
           └─────────┬─────────┘                            └───────────────────┘
                     │
                     ▼
           ┌───────────────────┐                            ┌───────────────────┐
           │    COM-BAD-001    │                            │    IMP-MET-001    │
           │     Community     │                            │   AI Adoption     │
           │    Contribution   │                            │ Metrics Framework │
           │     Framework     │                            │                   │
           └───────────────────┘                            └───────────────────┘
```

## Key Insights from Dependency Mapping

1. **Foundation Content**: LRN-BEG-001 (What is Generative AI?) is a critical foundation piece that many other content items depend on.
2. **Learning Pathways**: The beginner track has clear learning pathways with sequential dependencies, particularly in the Foundations of Generative AI and GenAI for Business subsections.
3. **Cross-Section Dependencies**: The Apply AI section has strong dependencies on the Learn AI track, particularly for sector playbooks.
4. **Independent Content Areas**: Several content areas can be developed independently in parallel:

   - Community features
   - Basic templates and tools
   - Case studies
   - Governance guides
5. **Critical Path Items**: The following items are on the critical path for multiple dependent content pieces:

   - LRN-BEG-001: What is Generative AI?
   - LRN-BEG-009: GenAI Applications and Use Cases
   - LRN-BEG-013: Understanding AI Bias and Fairness
   - HOM-MIS-001: Mission Statement
   - COM-FOR-001: Getting Started Forum
6. **Development Strategy**: This dependency mapping suggests a development strategy that:

   - Prioritizes foundation content first
   - Develops independent content areas in parallel
   - Focuses on completing critical path items before their dependencies