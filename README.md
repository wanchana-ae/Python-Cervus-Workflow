# 🧬 Parentage Analysis Toolkit: Python & Cervus Workflow

An automated pipeline for processing Microsatellite (SSR) Genotypes, performing allele binning, quality control (QC), and parentage assignment. This toolkit bridges the gap between raw fragment analysis data and final relationship reports.

## 📑 Script Overview

The workflow is divided into three distinct phases to ensure data integrity and minimize errors during the parentage assignment process.

|PhaseScript|NameKey|Function|
|:-----------|:-----:|:-----------|
|1. Preparation|`Convert_to_Cervus_Genotypes.py`|Performs Allele Binning (decimals to integers) and generates Cervus-ready files.|
||`crate_cervus_offspring_file.py`|Extracts unique candidate parent lists (Mothers/Fathers) from the database.|
|2. Quality Control|`calculate_detailed_errors_export.py`|Calculates per-marker mismatch rates based on known trios.|
||`false_inclusion_export.py`|Computes Power of Exclusion (PE) and overall marker set accuracy.|
|3. Reporting|`parentage_summary_report.py`|Generates the final relationship report with Pass/Fail status based on Mendelian inheritance.|

## 🚀 Getting Started

### 1. Data Cleaning & Binning

Raw data from fragment analysis often contains decimals. Cervus requires integer alleles.

- Run `Convert_to_Cervus_Genotypes.py`.

- It automatically bins alleles within a ±1.5 bp range and generates `Cervus_Genotypes.csv` and `Cervus_Offspring_File.csv`.

### 2. Marker Validation (QC Phase)

Before trusting assignments, evaluate your marker set:

- Run `false_inclusion_export.py` to calculate Exclusion Power.

Aim for >99% combined accuracy for reliable parentage results.

- Run `calculate_detailed_errors_export.py` to identify problematic markers (e.g., high null allele frequency or genotyping errors).

### 3. Final Assignment & Reporting

Once data is validated, generate a human-readable summary:

Run `parentage_summary_report.py`.

The script checks every offspring against its assigned parents using a ±2.0 bp tolerance and marks them as "Pass" or "Fail".

## 📂 Directory Structure

```bash
.
├── scripts/
│   ├── Convert_to_Cervus_Genotypes.py
│   ├── calculate_detailed_errors_export.py
│   ├── false_inclusion_export.py
│   └── ...
├── data/
│   └── Data_ready_to_use_add_fam.csv   # Primary input file
└── results/                           # Automatically generated outputs
    ├── marker_error_report.csv
    ├── overall_summary.csv
    └── parentage_summary_report.csv
```

## 📝 Input Format Requirements

Your input CSV must contain the following columns:

- ID: Unique identifier for each animal.

- Fam_ID: Family group identifier.

- Membership: C (Child), M (Mother), or F (Father).

- Marker_Name_1 & Marker_Name_2: Allele pairs for each locus.
