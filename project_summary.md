# LLM-Assisted Systematic Review Screening Tool - Project Summary

## Core Concept
A lightweight, locally-run desktop application that assists researchers in the title/abstract screening phase of systematic reviews by leveraging user-provided LLM APIs to evaluate papers against natural language inclusion criteria.

## Key Features

### **API-Agnostic LLM Integration**
- Users bring their own LLM API keys (OpenAI, Anthropic, Google Gemini, etc.)
- Flexible backend that can work with multiple LLM providers
- Cost control stays with the user

### **Simple Data Input**
- Upload papers via CSV or other standard formats (RIS, BibTeX, etc.)
- Import title, abstract, and basic metadata
- Support for common reference manager exports

### **Natural Language Criteria Definition**
- Users define their meta-analysis topic and inclusion/exclusion criteria in plain English
- Examples: "The experiment has this treatments: endophyte-associated and endophyte-free" or "They give some measure of plant performance, like total biomass"

### **Intelligent Paper Classification**
- LLM reads each paper's title and abstract
- Applies user-defined criteria using reasoning capabilities
- Provides classification: Include/Exclude/Uncertain
- Generates brief, human-readable explanations for each decision

### **Human-in-the-Loop Design**
- Explicitly positioned as an **assistant**, not replacement for human judgment
- Users review LLM decisions and explanations
- Easy override mechanism for incorrect classifications
- Transparent reasoning helps users learn and refine criteria

### **Session Management**
- Save/load project states for interrupted work sessions

## Technical Approach
- **Local deployment** for data privacy and control
- **Lightweight architecture** for easy installation and use
- **Stateful operation** with persistent project storage
- **Modular design** supporting different LLM providers

