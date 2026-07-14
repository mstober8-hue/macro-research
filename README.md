# Okun's Law in the AI Era

**Is the historical link between economic output and unemployment weakening because of AI?**

This project tests whether generative AI (using ChatGPT's release in Q4 2022 as a marker) has started to break Okun's Law — the 60-year-old relationship where GDP growth above potential reliably pulls unemployment down. If firms can now produce more output without proportionally hiring more workers, a core tool of macroeconomic policy is becoming less reliable.

**Status: the aggregate break is real and well-documented. The claim that AI specifically causes it is not yet established** — the one test built to isolate AI (ranking industries by AI exposure) came back pointing the other way. See [What This Does and Doesn't Show](#what-this-does-and-doesnt-show).

---

## The core idea: what is Okun's Law?

Okun's Law, first observed by economist Arthur Okun in 1962, says that when an economy grows faster than its sustainable pace, unemployment tends to fall — and when growth slows, unemployment tends to rise. It's the connection between *how much the economy is producing* and *how many people have jobs*. Every 1 percentage point of GDP growth above trend has historically been associated with roughly a 0.5 point fall in unemployment.

It's intuitive: rising demand means firms need more labor to meet it, so they hire. This research asks whether that's stopped being true — whether AI now lets firms meet rising demand without proportionally hiring.

## Data sources

All data is from [FRED](https://fred.stlouisfed.org/) (Federal Reserve Economic Data). Two series measure output, two measure jobs, all resampled to quarterly frequency.

| Series | What it is | Source |
|---|---|---|
| `GDPC1` | Real GDP (2017 dollars) | BEA, quarterly |
| `GDPPOT` | Potential GDP — what GDP would be at max sustainable output | CBO estimate, quarterly |
| `UNRATE` | Civilian unemployment rate | BLS, monthly (resampled to quarterly mean) |
| `NROU` | Natural rate of unemployment | CBO estimate, quarterly |

Industry-level analysis adds BEA real value-added and BLS unemployment series per sector (see `industry_okun_pipeline.py`), the [Felten, Raj & Seamans (2023)](https://onlinelibrary.wiley.com/doi/10.1002/soej.12558) AI Industry Exposure (AIIE) score, the Census Bureau's Business Trends and Outlook Survey (BTOS) AI-adoption question, and `FEDFUNDS` for interest-rate controls.

## Methodology

**Converting to gaps.** Raw GDP can't be compared across decades — the economy is just bigger now. Both series are converted to deviations from normal:

```
Output gap:        Y_gap = (GDPC1 − GDPPOT) / GDPPOT × 100
Unemployment gap:   U_gap = UNRATE − NROU
```

A positive `Y_gap` means the economy is running above potential; a positive `U_gap` means unemployment is above its natural rate. Under Okun's Law, `U_gap` should move in the opposite direction of `Y_gap`.

**Industry-level analysis uses the difference form instead**, since NAIRU/potential-output estimates only exist at the aggregate level:

```
ΔU = β × %ΔY + ε
```

where `ΔU` is the quarter-over-quarter change in the sector's unemployment rate and `%ΔY` is the quarter-over-quarter growth of its real output. Classic Okun's Law implies β ≈ −0.3 to −0.5; β drifting toward zero (or flipping positive) means growth has stopped pulling unemployment down.

**Excluding COVID.** Q2 2020 – Q1 2021 is dropped from every regression and rolling statistic. GDP cratered and unemployment spiked because businesses were legally closed, not because of any organic output-employment relationship — including these quarters would corrupt every downstream regression. They're kept in the raw dataset and plotted as red diamonds for transparency, just excluded from fitting.

**Era split.** Q4 2022 (ChatGPT's public release) is used throughout as the pre/post-AI cutoff. This is a useful, visible marker but an admittedly imperfect one — enterprise AI adoption happened gradually, and it also happens to sit right on top of the start of the Fed's most aggressive hiking cycle in ~40 years, which is a real confound addressed in Phase 2 below.

## Repository guide

| Script | What it tests | Key outputs |
|---|---|---|
| [`GDPUnemployment.py`](GDPUnemployment.py) | Aggregate Okun's Law, 2000–present, rolling 12-quarter coefficient | `gdp_unemployment_analysis.png`, `gap_divergence.png`, `gap_divergence_abs.png`, `gap_okun_residual_quadrant.png`, `rolling_okuns_coefficient.png`, `okun_projection_2030.png` |
| [`IndustryAnalysis.py`](IndustryAnalysis.py) | Two-sector comparison: Information (high AI exposure) vs. Leisure & Hospitality (low) | `industry_scatter.png`, `industry_rolling_okun.png`, `industry_okun_residual.png`, `industry_unemployment_correlation.png`, `industry_output_vs_unemployment.png` |
| [`industry_okun_pipeline.py`](industry_okun_pipeline.py) | Full 9-industry BLS/BEA pipeline, Δβ ranked and regressed against AIIE score | `okun_industry_summary.csv/.txt`, `okun_industry_detail.xlsx`, `industry_aiie_scatter.png`, `industry_rolling_overlay.png`, per-industry charts (`okun_construction.png`, `okun_manufacturing.png`, etc.) |
| [`okun_phase2_3.py`](okun_phase2_3.py) | Adds a Federal Funds Rate control (6 specifications: no control, lagged 2/4 quarters, level, rolling deviation) to rule out the rate-hike confound | `phase2_results.csv`, `phase2_rate_sensitivity.png`, `phase3_cross_section.csv`, `phase3_cross_section.png` |
| [`btos_interaction.py`](btos_interaction.py) | Cross-checks the AIIE (theoretical exposure) ranking against BTOS (self-reported actual AI adoption) | `btos_beta1_table.csv`, `btos_sector_ranking.csv`, `btos_cross_section.png` |
| [`info_overhang.py`](info_overhang.py) | Tests whether Information sector's breakdown is just a correction from 2020–21 overhiring, not AI or rates | `info_overhang_sanity.png`, `info_overhang_regression.png` |
| [`generate_results_csv.py`](generate_results_csv.py) | Compiles every regression result across all scripts into one labeled CSV | `results_comprehensive.csv` |

Run any script directly with `python3 <script>.py`; each writes its charts and tables to the repo root. Requires `pandas`, `numpy`, `matplotlib`, `scipy`, and (for `industry_okun_pipeline.py`'s Excel export) `openpyxl`.

## Findings walkthrough

### 1. The aggregate break (`GDPUnemployment.py`)

**2010–2019:** the output gap and unemployment gap move in near-perfect mirror image — as GDP recovered from the Great Recession (`Y_gap` rising toward zero), unemployment fell in lockstep (`U_gap` falling toward zero). The rolling correlation between them sits close to −1.0 for almost two decades. Textbook Okun's Law.

**Since Q4 2022:** the output gap has stayed clearly positive (roughly +1 to +1.5%) — the economy running above potential — but the unemployment gap has barely responded. The two lines stop mirroring each other and run nearly parallel.

The rolling 12-quarter Okun coefficient (`C`), which had held steady between −0.5 and −1.25 for twenty years, starts swinging erratically after Q4 2022: briefly negative, then spiking to roughly +0.6, then collapsing back toward zero. Most notably, **the rolling correlation flips from about −1.0 to +0.81** — tested against the pre-2022 historical distribution, the probability of a correlation that positive occurring by chance is effectively zero (`p ≈ 0.0000`).

**Caveat:** the post-ChatGPT sample is short — about 10–13 quarters as of the most recent data. Short-window rolling statistics are noisy by construction, and the instability cuts both directions (`C` was briefly very negative before it inverted). This documents a break; it doesn't by itself prove a cause.

### 2. Two-sector comparison (`IndustryAnalysis.py`)

If AI is the mechanism, the breakdown should concentrate in AI-exposed industries. Comparing Information (software, cloud, media — high exposure) against Leisure & Hospitality (restaurants, hotels — low exposure): the Leisure & Hospitality Okun relationship holds roughly as expected throughout, while Information's rolling coefficient turns volatile and drifts toward a slightly positive slope after Q4 2022. Directionally consistent with the AI hypothesis, but a two-industry comparison is a small sample — the natural next step is testing across every industry with a formal exposure measure.

### 3. Nine-industry cross-section (`industry_okun_pipeline.py`)

This is where the hypothesis gets a real test. Nine BLS super-sectors were ranked by Δβ (how much the Okun coefficient shifted after Q4 2022) and regressed against each sector's AIIE score — Felten, Raj & Seamans' measure of theoretical AI exposure by occupation mix.

| Industry | AIIE score | β pre-2022 | β post-2022 | Δβ |
|---|---:|---:|---:|---:|
| Construction | −0.997 | −0.393 | +0.046 | **+0.439** (most weakened) |
| Manufacturing | −0.484 | −0.327 | +0.110 | **+0.437** |
| Transportation & Utilities | −0.342 | −0.255 | +0.157 | **+0.412** |
| Information | 1.268 | −0.134 | +0.180 | +0.314 |
| Wholesale Trade | 0.264 | −0.167 | +0.066 | +0.232 |
| Professional & Business | 0.654 | −0.341 | −0.227 | +0.114 |
| Leisure & Hospitality | −0.315 | −0.356 | −0.302 | +0.054 |
| Financial Activities | 1.538 | −0.022 | −0.057 | −0.035 (strengthened) |
| Education & Health | 0.775 | −0.034 | −0.222 | −0.188 (strengthened) |

*(β = Okun's difference-form coefficient — more negative means the law holds more strongly. Δβ = β_post − β_pre; positive means the law weakened.)*

**The result is a correction, not a confirmation.** A first pass at the scatter had the axis sign backwards; once corrected, the actual cross-sectional regression comes out **r ≈ −0.61, p ≈ 0.08 (n = 9, marginal at the 90% level)** — meaning *higher* AI exposure predicts a *stronger*, not weaker, Okun relationship. That's the opposite of the hypothesis. Only Information and Wholesale Trade behaved as the AI story would predict; the three highest-exposure sectors (Financial Activities, Professional & Business, Education & Health) held steady or strengthened, while the largest breakdowns concentrated in low-exposure, physical/interest-rate-sensitive sectors — Construction, Manufacturing, Transportation & Utilities.

Three sector notes worth keeping in mind:
- **Construction's** correlation flipped sign (−0.73 → +0.78) but its coefficient barely moved off zero in *either* period — a very reliable relationship, just not an economically large one. Its pre-2022 baseline is also visibly anchored by the 2008–2012 housing crash, raising the question of how much of that number is one historical crisis rather than a stable long-run pattern.
- **Education & Health** shows a weak relationship in both eras (|r| under ~0.2) — unsurprising for a sector driven by demographics and public funding cycles rather than the business cycle.
- **Financial Activities'** real output has nearly doubled relative to 2019 while its unemployment rate has stayed low and flat since roughly 2013 — a genuine, dramatic output/employment divergence, but one that's been building gradually over a decade rather than appearing at the Q4 2022 cutoff, which is why a break-detection test built around that date finds nothing unusual there.

### 4. Ruling out the interest-rate confound (`okun_phase2_3.py`)

The Fed's most aggressive hiking cycle in roughly 40 years began almost exactly when the AI cutoff does, and the three sectors with the biggest breakdowns (Construction, Manufacturing, Transportation) are also the most rate-sensitive industries in the economy. A test that can't separate the two will attribute rate-driven disruption to AI by default.

Adding `FEDFUNDS` as a control (contemporaneous, lagged 2/4 quarters, level, and rolling deviation — six specifications total) **does not make the low-AI-sector breakdown disappear.** After controlling for the contemporaneous rate, Δβ for Construction stays at +0.38, Manufacturing at +0.31, and Transportation falls more (to +0.35 lagged / +0.12 at the level spec) — smaller in places, but the pattern survives across most specifications. This means the rate confound doesn't fully explain the sector pattern away, but it doesn't rescue the AI hypothesis either — the breakdown is still concentrated in low-exposure sectors either way.

### 5. Checking AIIE against actual reported AI adoption (`btos_interaction.py`)

AIIE measures theoretical *exposure*, not real-world *adoption*. The Census Bureau's BTOS survey has asked firms about AI use since late 2025, giving a short (~3-quarter) but real adoption measure to cross-check against. Comparing sector rankings: Financial Activities and Information top both lists; the rest reorder somewhat (e.g., Manufacturing ranks 6th by adoption but 8th by theoretical exposure). The BTOS series is currently too short to run its own time-series regression, but the rank correlation with AIIE is broadly consistent, which is a modest validation of the Felten et al. exposure measure as a reasonable (if imperfect) proxy.

### 6. Overhang hypothesis for Information specifically (`info_overhang.py`)

One alternative explanation, specific to the Information sector: tech firms over-hired 15–20% above trend during 2020–2021, and the "breakdown" after Q4 2022 is really just that hiring correcting itself (mass layoffs) rather than AI or rates. This script adds an employment-overhang control to the regression to test whether it absorbs Information's positive post-2022 β. See `info_overhang_regression.png` for the result.

## What this does and doesn't show

**Established:** Okun's Law has weakened in the aggregate U.S. economy since Q4 2022. The output gap has stayed positive while the unemployment gap hasn't responded the way two decades of prior data would predict, and the statistical signature (correlation inversion, p ≈ 0.0000) is not something the historical distribution produces by chance.

**Not established:** that AI specifically is the cause. The one test built to isolate an AI effect — ranking industries by AI exposure and checking whether exposure predicts more weakening — came back pointing the *other* way, and that result survives a rate-hike control. This doesn't mean AI isn't part of the story; the AIIE score measures occupational exposure to AI capability, not measured displacement, and true labor substitution may lag exposure by longer than 12–13 quarters of post-ChatGPT data can currently show. It does mean the current evidence can't distinguish "AI is breaking Okun's Law" from "post-pandemic fiscal policy (IIJA, CHIPS Act, IRA) inflated physical-sector output without proportional hiring" or "monetary policy is doing more of this than AI is."

## Limitations

- Post-ChatGPT sample is short (~10–13 clean quarters); rolling-window statistics from that few points are noisy, and overlapping windows violate the independence assumption behind the reported p-values (making them somewhat optimistic, though likely still small).
- The Q4 2022 cutoff is a convenient, visible marker (ChatGPT's launch date), not a measured adoption date — actual enterprise AI adoption was gradual and is itself confounded with the 2022–2023 rate-hiking cycle.
- Industry-level data is more volatile than aggregate GDP/unemployment, and a 9-industry cross-section is a small sample for a regression-based test.
- This project documents a correlation-level break and tests one candidate explanation (AI exposure) against two obvious confounds (interest rates, overhiring correction). It does not establish causality.

## Reproducing this

1. Download the FRED series listed above (plus the industry-level and `FEDFUNDS` series referenced in each script's header) as CSVs into the data directory each script expects (`Fred Fed Data/`).
2. `pip install pandas numpy matplotlib scipy openpyxl`
3. Run scripts in this order for the full pipeline: `GDPUnemployment.py` → `IndustryAnalysis.py` → `industry_okun_pipeline.py` → `okun_phase2_3.py` → `btos_interaction.py` → `info_overhang.py` → `generate_results_csv.py`.
