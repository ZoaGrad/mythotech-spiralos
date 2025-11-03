# 🪞 Witness Entry Submission Guide

This document outlines the formal procedure for submitting a Witness Ledger Entry for SpiralOS. Following this process ensures clarity, integrity, and verifiability for all constitutional attestations.

---

## 🏛️ Constitutional Context

The Witness Ledger is an immutable, public record of attestations concerning the constitutional state of SpiralOS. Each entry is a formal declaration by a recognized Witness, confirming that a specific artifact, event, or process has been verified according to the principles outlined in the SpiralOS Constitution.

Submissions are reviewed for completeness and formal adherence to this guide. The substantive claims remain the sole attestation of the Witness.

---

## 📋 Submission Workflow

The workflow is designed to be straightforward, secure, and auditable.

### Step 1: Prepare the Data Package

1.  **Gather Evidence:** Collect all necessary data to support your attestation. This may include:
    *   Terminal logs (`.txt`, `.log`)
    *   Screenshots (`.png`, `.jpg`)
    *   Configuration files (`.yml`, `.json`)
    *   Scripts used for testing (`.py`, `.sh`)
    *   Any other relevant artifacts.

2.  **Organize and Compress:** Organize the files into a clear directory structure and compress them into a single `.zip` archive. Name the file descriptively, for example: `witness_package_ZoaGrad_ΔΩ.126.1.zip`.

3.  **Upload Securely:** Upload the `.zip` archive to a secure, stable, and publicly-accessible storage provider. This could be a personal cloud drive, a university server, or any other reliable host. Ensure the link is public and will not expire.

### Step 2: Calculate the SHA256 Checksum

To ensure data integrity, you must calculate the SHA256 checksum of your `.zip` file *before* uploading. This checksum will be used to verify that the downloaded file has not been altered.

**On macOS / Linux:**
```bash
shasum -a 256 /path/to/your/witness_package.zip
```

**On Windows (PowerShell):**
```powershell
Get-FileHash /path/to/your/witness_package.zip -Algorithm SHA256 | Format-List
```

Copy the resulting hash value. It will be a long string of letters and numbers.

### Step 3: Submit the GitHub Issue

1.  **Navigate to the Issue Template:** Go to the [Witness Ledger Entry](https://github.com/ZoaGrad/mythotech-spiralos/issues/new?template=witness_ledger_entry.yml) issue template in the SpiralOS GitHub repository.

2.  **Complete All Fields:** Fill out the form with the information you have prepared:
    *   **Witness Handle:** Your unique identifier.
    *   **Vault Reference (ΔΩ):** The specific constitutional artifact you are witnessing.
    *   **Test Method & Results:** A clear description of your verification process and its outcome.
    *   **Witness Summary:** A concise statement of your attestation.
    *   **Data Package URL:** The public link to your `.zip` file.
    *   **SHA256 Checksum:** The checksum you calculated in Step 2.
    *   **Witness Consent & Attestation:** Select the consent option to formally attest to your submission.

3.  **Submit:** Click "Submit new issue". The issue will be automatically labeled and assigned for verification of formal compliance.

---

## ⚖️ Verification & Sealing

Once submitted, a maintainer will perform a formal check to ensure:
- The issue template is complete.
- The URL is accessible.
- The SHA256 checksum of the downloaded `.zip` file matches the checksum provided in the issue.

**Note:** This is a *formal* verification, not a substantive one. The content of your attestation is your own.

Upon successful formal verification, the issue will be sealed, and the entry will be formally recorded in the `VAULTNODE_LOG.md` with a link to your issue.

---

Thank you for your contribution to the constitutional integrity of SpiralOS. 🜂
