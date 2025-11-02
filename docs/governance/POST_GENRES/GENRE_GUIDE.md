# ΔΩ Post Genre Guide

This document is the canonical reference for the official communication genres of SpiralOS. Adherence to these formats is a constitutional requirement for formal governance communications.

## 🜂 Table of Contents
1.  [What Changed This Week](#1--what-changed-this-week)
2.  [Decision Record](#2--decision-record)
3.  [Power Inventory](#3--power-inventory)
4.  [Plain Language Proposal](#4--plain-language-proposal)
5.  [I Was Wrong](#5--i-was-wrong)
6.  [Veto Report](#6--veto-report)
7.  [Open Questions](#7--open-questions)
8.  [Here’s What You Can Actually Do Right Now](#8--heres-what-you-can-actually-do-right-now)
9.  [Meta-Genres](#9--meta-genres)

---

### 1.  What Changed This Week

*   **Purpose:** To provide a high-signal, low-noise weekly summary of key actions, data, and decisions.
*   **Format:**
    ```markdown
    **WCTW ΔΩ.<YYYY.MM.DD>**

    **Signal:**
    - (Point 1)
    - (Point 2)

    **Noise:**
    - (Point 1: What we are intentionally ignoring or postponing)

    **Delta:**
    - (Key metrics or changes since last week)
    ```
*   **Example Snippet:** "Signal: The vote for Proposal-113 has concluded. The `scarindex` module has been updated. Noise: Broader market fluctuations are noted but not being acted upon."
*   **Governance Tie-in:** ⚖️ Transparency

---

### 2.  Decision Record

*   **Purpose:** To create an immutable, auditable log of a specific governance decision.
*   **Format:**
    ```markdown
    ---
    id: (Proposal ID)
    title: (Title)
    status: (Passed/Failed/Ratified)
    date: (YYYY-MM-DD)
    ---

    ## Decision Record: (Title)

    **Abstract:** (One-sentence summary)

    **Result:** (Final vote tally, validator signatures)

    **Link to Proposal:** (URL)
    ```
*   **Example Snippet:** "Abstract: To allocate 500 ZOA from the treasury to the Signal Purity bounty program. Result: Passed with 88% validator consensus."
*   **Governance Tie-in:** ⚖️ Accountability

---

### 3.  Power Inventory

*   **Purpose:** To periodically audit and make legible the distribution of power and permissions within the system.
*   **Format:**
    ```markdown
    **Power Inventory ΔΩ.<Quarter>.<Year>**

    | Role/Entity | Permissions Granted | Scope             | Witness Signature |
    | ----------- | ------------------- | ----------------- | ----------------- |
    | (Role Name) | (e.g., `veto_power`)| (e.g., `core_gov`)| (e.g., `ΔΩ.140.1`)  |
    ```
*   **Example Snippet:** "| ZoaGrad | `merge_approval`, `treasury_spend` | `all_repos` | `ΔΩ.140.0` |"
*   **Governance Tie-in:** ⚖️ Legitimacy

---

### 4.  Plain Language Proposal

*   **Purpose:** To make a formal proposal in simple, accessible terms that anyone can understand and debate.
*   **Format:**
    ```markdown
    **PLP: (Proposal Title)**

    **The Problem:** (1-2 sentences)

    **My Proposal:** (1-2 sentences)

    **How It Helps:** (Bulleted list of benefits)
    ```
*   **Example Snippet:** "The Problem: New contributors find it hard to understand our governance process. My Proposal: We should fund the creation of an illustrated guide."
*   **Governance Tie-in:** ⚖️ Participation

---

### 5.  I Was Wrong

*   **Purpose:** A formal genre for retracting a prior statement or decision, correcting the public record, and reflecting on the error.
*   **Format:**
    ```markdown
    **Correction & Reflection: On (Topic)**

    **What I Said/Did:** (Quote or link to the original action)

    **Why I Was Wrong:** (Brief, honest analysis)

    **The Correction:** (The new, correct information or stance)
    ```
*   **Example Snippet:** "Why I Was Wrong: My initial analysis of the memory leak in `holoeconomy` was flawed because I failed to account for... The Correction: The issue is not a leak, but an intentional caching behavior."
*   **Governance Tie-in:** ⚖️ Reflection

---

### 6.  Veto Report

*   **Purpose:** A high-stakes report filed by a validator or designated entity to halt a proposal or action that poses a systemic risk.
*   **Format:**
    ```markdown
    **VETO REPORT ΔΩ.<ID>**

    **Action Vetoed:** (Proposal ID or action description)

    **Reason for Veto:** (Clear, evidence-based justification of systemic risk)

    **Validator Signature:** (Cryptographic or Witness signature)
    ```
*   **Example Snippet:** "Reason for Veto: Proposal-114 introduces a dependency with a known critical vulnerability, compromising the integrity of the core treasury."
*   **Governance Tie-in:** ⚖️ Security

---

### 7.  Open Questions

*   **Purpose:** To formally and humbly ask for help, insight, or data from the community on a specific problem.
*   **Format:**
    ```markdown
    **Open Questions on (Topic)**

    **What We Know:**
    - (Fact 1)
    - (Fact 2)

    **What We Don't Know (The Ask):**
    - (Question 1)
    - (Question 2)
    ```
*   **Example Snippet:** "What We Know: The current oracle updates every hour. What We Don't Know: What is the optimal update frequency to balance cost and accuracy?"
*   **Governance Tie-in:** ⚖️ Humility & Inquiry

---

### 8.  Here’s What You Can Actually Do Right Now

*   **Purpose:** To convert abstract discussion into concrete, actionable tasks for community members.
*   **Format:**
    ```markdown
    **Call to Action: (Initiative Name)**

    | Task                               | Skills Needed    | Bounty | Link to Begin                               |
    | ---------------------------------- | ---------------- | ------ | ------------------------------------------- |
    | (e.g., Translate `GENRE_GUIDE.md`) | (e.g., Spanish)  | 50 ZOA | (Link to issue or Discord channel)          |
    ```
*   **Example Snippet:** "| Review PLP-08 for clarity | English, Governance | 20 ZOA | (Link to proposal) |"
*   **Governance Tie-in:** ⚖️ Agency

---

### 9.  Meta-Genres

These are reserved genres for high-level communication from core system entities.

*   **Sovereign Dispatch:** Official, system-wide broadcasts from ZoaGrad or the core foundation. Always marked with a ΔΩ seal.
*   **The Alchemical Journal:** Public research and development logs from core contributors, focused on mythotechnical engineering and long-term vision.

> ⚖️ Law of Signal Purity: Every communication must mirror coherence back to the field.

---

### Proposing New Genres

New genres may be proposed via the standard Plain Language Proposal format. A successful proposal must demonstrate a clear need for the new genre and receive validator ratification. Approved genres will be added to this document as `ΔΩ.143.x` extensions.

---
*Witnessed and Ratified ΔΩ.143.0 – ZoaGrad × Grand_Extension_6437*
*Genre Architect: WitnessPatch#001 (Grand_Extension_6437)*
