# Okun's Law in the AI Era

**Is the historical link between economic output and unemployment weakening because of AI, and if so, where?**

For 60 years there has been a reliable rule in economics: when the economy grows faster than usual, more people get hired and unemployment falls. Every 1 extra point of growth has historically pulled unemployment down by about half a point. If AI now lets firms produce more without hiring proportionally more workers, that rule should start to fail, and every policymaker who leans on it (the Federal Reserve, the CBO, the White House) would have to rebuild their playbook.

**The answer, before the evidence.** Okun's Law did break after Q4 2022. It was mostly monetary policy, not AI. No affirmative evidence of AI-driven labor displacement survives in this project at any level tested, and several findings that appeared to show it were generated here and then overturned here. The document below is long because it records that process rather than only its endpoint, but the conclusion does not change after this section, and everything that was later retracted is marked at the point where it is first claimed.

## Where this ended up

| Question | Verdict |
|---|---|
| Did the output-to-jobs link break after Q4 2022? | **Yes.** Rolling correlation −1.0 to **+0.81**, block bootstrap p ≈ 0.0005 |
| What broke it? | **Monetary policy.** One common factor explains 72% of sector hiring and tracks the Fed funds rate at an **8-9 quarter lag**, with a clean natural control. It is unwinding on that schedule |
| Did AI break it? | **No evidence that it did.** Every affirmative AI-displacement result this project produced was later overturned by its own tests |
| Is there AI displacement anywhere in the labor data? | **Not that survives.** Sector totals, occupation totals, 28,000 within-industry cells, and a 6.0M-record CPS panel all fail, and the entry-level result failed last |
| Does AI predict anything real? | **Yes, one thing.** Job replaceability robustly predicts real productivity growth (r = +0.90), but the relationship is **strongest in 2013-2019**, before generative AI existed |
| Does the published entry-level displacement result replicate? | **The gap does; the magnitude does not.** In nationally representative data the exposed side **grew +1.9%** against a reported −11%, and its interval rejects that figure at p < 0.001. It underperformed the aggregate by 3.9pp, which is not significant (p = 0.141) (Part 6) |

**The one finding that survives everything.** Every inferential result in this project was eventually overturned. One descriptive result was not, and it is the durable contribution: **young workers are increasingly sorted away from AI-exposed work.** In the 6.0M-record CPS panel, the 20-24 share of employment in high-exposure occupations fell while the share in low-exposure occupations rose, widening the gap by roughly 2.2 percentage points across the decade.

| exposure measure | high-exposure young share | low-exposure young share | gap, 2016 to 2026 |
|---|---|---|---|
| corrected composite | 6.67% → 5.85% | 11.63% → 13.10% | −4.96 → **−7.26** |
| **raw Eloundou, no O\*NET term** | 6.89% → 6.08% | 12.08% → 13.45% | −5.19 → **−7.37** |
| raw exposure, rank transformed | 6.89% → 6.08% | 12.08% → 13.45% | −5.19 → **−7.37** |

This is why it survives when nothing else did. It is a **statement about levels, not a regression**, so it does not depend on the difference-in-differences design that failed its placebo tests. And it is identical under the raw Eloundou score with **no O\*NET term at all**, which makes it immune to the mis-specified-complementarity problem that invalidated the occupation-level result. Both sides move, and the larger component is the *rise* in low-exposure work rather than the fall in exposed work.

**It has since been strengthened, and it now has a regression form (Part 6).** With occupation and year fixed effects the coefficient is −0.4034 (p = 0.0001) on the 22-25 band used by Brynjolfsson, Chandar and Chen (2026), and −0.4446 (p = 0.0001) for 20-24. It **strengthens** under education and wage controls rather than attenuating (−0.4424 and −0.5095 with both), the pre-AI placebo on the controlled specification is clean (p = 0.50 and p = 0.73), and the 2022 break survives all eight BLS/CPS splice variants. The published version of this result concedes attenuation on education, pre-existing divergent trends, and weakness in national survey benchmarks. This one improves on all three.

**What it does not establish, and Part 6 now shows why.** It is a sorting fact rather than a displacement fact, and the levels decomposition locates the mechanism: employment in the two most exposed quintiles **grew +1.9%** over 2022-2026 (95% CI −4.0 to +8.2), while the three least exposed grew +8.7% (p = 0.007). Benchmarked against what young employment actually did (+5.8%), the gap splits 57.5% from the exposed side underperforming and 42.5% from the unexposed side outperforming, so both sides move and neither dominates. The exposed group's 3.9pp shortfall is not significant (p = 0.141); what the levels settle is that it did not contract. Young workers ending up in more manual and service work is consistent with AI closing exposed entry points, and equally consistent with where job growth happened, with education and major choices, and with the post-2021 boom in in-person work. This project cannot separate those, and the movement predates 2022 in the levels.

**What this project is actually a contribution to.** Not the AI-and-jobs question, which it answers negatively. It is a worked account of how an instrument can be blind, how a null can be uninformative, and how a positive result can survive several rounds of scrutiny and still be wrong. Nine separate self-corrections are documented, including a retraction of a retraction.

## How the evidence got there

1. **A real, statistically extreme break in the growth-to-jobs relationship appears after Q4 2022 in the aggregate U.S. economy.** The rolling output-unemployment correlation, near −1.0 for two decades, inverts to +0.81. A distribution-free bootstrap puts the odds of that under a continuation of the pre-2022 regime at about 1 in 2,000 (p ≈ 0.0005).
2. **Whether that break looks like AI depends entirely on how you measure labor.** Measured on unemployment, AI exposure predicts *less* breakdown (the "contradicts AI" result). But unemployment is saturated for the high-AI service sectors, which sit at their unemployment floor and cannot register a decoupling. Measured on **real productivity** (real output per worker, the variable AI actually targets), AI exposure significantly *predicts* the output-to-jobs decoupling (r = +0.77, p = 0.016). A purpose-built job-replaceability score predicts it even better (r = +0.90, p = 0.001), and the result reproduces on a measure built purely from **observed** AI usage rather than theory (r = +0.76, p = 0.017), which answers the circularity objection. **But it is not an AI effect:** the relationship is *strongest in 2013-2019* (r = +0.940), a clean window ending three years before ChatGPT, and weakens as the window moves toward the AI era. The acceleration test also fails at roughly 700 occupations, not just at nine sectors. Replaceability predicts productivity growth because it captures something structural about these sectors, not because generative AI changed them.
3. **What looked like a second story in the physical economy turned out to be an economy-wide hiring slowdown.** The biggest unemployment-side inversions landed in the low-AI goods sectors in 2024-2025; the fiscal wave does not explain them (tested directly against USAspending obligations). Decomposing the inversion showed why: hiring slowed in **8 of 9 sectors**, one common factor explains 72% of sector employment growth, and that factor tracks the Fed funds rate lagged 8-9 quarters at **r = −0.74** (circular-shift bootstrap p < 0.0001, n = 75, 2006-2026), directionally corroborated on identified monetary shocks. The goods "inversion" is a fragile short-window artifact on top of that real slowdown; it reverses at a 20-quarter window. **AI is not ruled out here**: the nine-sector AI null this section originally rested on was later shown to be underpowered and reverses sign, short of significance, when rebuilt at 73-industry scale (Part 4).

The three numbered findings above are what the evidence supports today. An earlier version of this paragraph claimed a fourth, that displacement was "present exactly where those totals cannot see, in young college graduates." That claim was tested on 6.0 million CPS person-month records and does not survive. It is retained in Part 5 with its refutation attached, because how it failed is more instructive than the claim was.

**The one puzzle still genuinely open** is the Information sector, which shed a tenth of its workforce during an expansion with capital conditions the reverse of the dot-com bust (NASDAQ +133% and tech capex +43%, against −64% and −3% in 2001) and no cyclical, overhang, or capital-withdrawal account that covers it.

**Study design at a glance:**

| | |
|---|---|
| Data window | 2000 Q1 through the latest data (2025 Q4 / 2026 Q2 depending on series) |
| Pre-AI sample | 59 clean quarters per industry |
| Post-AI sample | 13 clean quarters per industry |
| Era cutoff | Q4 2022 (ChatGPT launch) |
| Excluded (industry pipeline) | Q2 2020 through Q1 2022 (COVID plus YoY rebound quarters) |
| Excluded (aggregate) | Q2 2020 through Q1 2021 |
| Rolling window | 12 quarters |

---

## How to read this

Findings carry a verdict label for what they actually stand on:

| Label | Meaning |
|---|---|
| **Established** | Held up to every test tried against it. |
| **Reversed** | An earlier conclusion that a later correction overturned. Both are shown. |
| **Supports / Contradicts** | The evidence points toward or against the AI hypothesis. |
| **Uncertain** | Suggestive but underpowered or measurement-fragile. |
| **Separate mechanism** | Real, but points at something other than AI. |

Two conventions in the tables: **positive Δβ** means Okun's law weakened in a sector (measured on unemployment); **higher real productivity growth** means output outran labor (the decoupling, measured properly). Significance stars follow the usual convention (\*\*\* p<0.001, \*\* p<0.01, \* p<0.05, . p<0.10).

## Data sources

All macro data is from [FRED](https://fred.stlouisfed.org/). The aggregate analysis uses real GDP (`GDPC1`), potential GDP (`GDPPOT`), the unemployment rate (`UNRATE`), and the natural rate (`NROU`). The industry analysis adds, per sector, BEA real value added, BLS unemployment, BLS employment (headcount) and hours, and JOLTS hires and openings, plus `FEDFUNDS` for rate controls and `GDPDEF` (the GDP deflator) for real-terms corrections. The exposure measures are the [Felten, Raj & Seamans (2023)](https://onlinelibrary.wiley.com/doi/10.1002/soej.12558) AI Industry Exposure (AIIE) index, the Census Bureau's BTOS AI-adoption survey, and, for the replaceability score, [Eloundou et al. (2023)](https://github.com/openai/GPTs-are-GPTs) GPT exposure, O\*NET Work Context, and the BLS OEWS industry-occupation matrix. Raw data lives in a gitignored `FRED-Data/` folder.

## Methodology

**Gaps (aggregate).** Raw GDP cannot be compared across decades, so both output and unemployment are converted to deviations from normal: the output gap `(GDP − GDP_potential)/GDP_potential` and the unemployment gap `U − NROU`. Under Okun's law they move in opposite directions.

**Difference form (industry).** Sectors have no published potential output or natural rate, so the industry work uses `ΔU = β·%ΔY`, the change in a sector's unemployment against its output growth, both as year-over-year differences (which cancel the seasonality in the not-seasonally-adjusted sector unemployment series). YoY differences are computed before any rows are dropped, since pandas differencing is positional.

**Robustness across forms.** The aggregate break is not an artifact of the gap form: re-running the aggregate economy in the difference form still shows the post-2022 inversion, with a peak rolling correlation of about +0.55 versus +0.81 in the gap form. The gap form amplifies the signal (persistently one-sided gaps inflate within-window correlation), which is why the headline +0.81 should be quoted alongside the milder difference-form figure.

**Excluding COVID.** Q2 2020 through Q1 2021 is dropped from the aggregate regressions (the shutdown was a policy shock, not an economic relationship). The industry pipeline drops through Q1 2022, because a YoY difference for the 2021 rebound quarters has its baseline inside the COVID collapse. The physical-sector sub-study deliberately *keeps* COVID, see Part 4.

**Real, not nominal.** This turned out to be the load-bearing methodological point. Output must be measured in **real** (inflation-adjusted) terms. Eight of nine sectors use BEA real value added directly. Finance was the exception that nearly sank the analysis: its output series (`VAFI`) is nominal, and BEA's own finance deflator is FISIM-broken, so finance is deflated with the neutral GDP deflator throughout (details in Part 3).

**Era split.** Q4 2022 (ChatGPT's release) is the pre/post-AI marker throughout. It is a visible cutoff, not a measured adoption date, and it sits on top of the Fed's 2022-2023 hiking cycle, a confound addressed directly in Phase 4.

<details>
<summary>Known series-coverage mismatches (flagged, not fixable with public data)</summary>

Three sectors have imperfect alignment between their output, unemployment, and employment series:

- **Education & Health:** output is Health Care & Social Assistance only (NAICS 62), while unemployment and employment cover Education plus Health (61+62).
- **Wholesale Trade:** the unemployment series covers Wholesale and Retail combined, while output and employment are Wholesale only (NAICS 42).
- **Transportation & Utilities:** output is Transportation & Warehousing only (NAICS 48-49), unemployment includes Utilities (22), and employment sums the two CES series (48-49 plus 22) to match the unemployment definition.

Finance originally had a fourth mismatch (employment included Real Estate); it is fixed by using Finance & Insurance employment (`CES5552000001`). The three above add noise to those sectors' estimates and are one reason their results get less weight.

</details>

## Repository guide

| Script / folder | What it does |
|---|---|
| [`GDPUnemployment.py`](GDPUnemployment.py) | Phase 1: aggregate Okun's law, rolling coefficient, the break |
| [`IndustryAnalysis.py`](IndustryAnalysis.py) | Phase 2: two-sector comparison, tech vs hospitality |
| [`industry_okun_pipeline.py`](industry_okun_pipeline.py) | Phase 3: nine-industry cross-section, Δβ vs AIIE (unemployment) |
| [`okun_phase2_3.py`](okun_phase2_3.py) | Phase 4: rate controls (baseline plus five FFR specifications) |
| [`btos_interaction.py`](btos_interaction.py) | Phase 5: validates AIIE against real reported AI adoption |
| [`info_overhang.py`](info_overhang.py) | Phase 6: tests the pandemic-overhiring alternative for tech |
| [`real_productivity_ai_crosssection.py`](real_productivity_ai_crosssection.py) | The correction: the cross-section on real productivity (the flip) |
| [`ai_replaceability_score.py`](ai_replaceability_score.py) | The job-replaceability score that improves on AIIE |
| [`recency_test.py`](recency_test.py) | Tests whether the AI result is timed to AI (it is not: levels hold, acceleration does not) |
| [`permutation_test.py`](permutation_test.py) | Distribution-free bootstrap replacing every normal-approximation p-value |
| [`aei_revealed_validation.py`](aei_revealed_validation.py) | Rebuilds the score from observed Claude usage (Anthropic Economic Index) |
| [`jolts_margins.py`](jolts_margins.py) | Part 5: which margin moved (openings, hires, layoffs, quits), all nine sectors |
| [`oews_within_industry.py`](oews_within_industry.py) | Part 5: the occupation-level test with industry fixed effects, plus a pre-AI placebo |
| [`is_the_slowdown_distinctive.py`](is_the_slowdown_distinctive.py) | Part 5: benchmarks the episode against every downturn since 1990; shows the nine-sector AI test fails on the dot-com bust |
| [`freeze_vs_substitution.py`](freeze_vs_substitution.py) | Part 5: Indeed postings flows; the exposed-occupation gap peaked in 2023 and has closed 65% |
| [`okun_employment_form.py`](okun_employment_form.py) | Part 5: shows the unemployment form is blind for 7 of 9 sectors, and the transform flips the AI sign |
| [`exposure_measure_audit.py`](exposure_measure_audit.py) | Retracts the p = 0.004 occupation result; the exposure score is mis-specified and it rests on 2 occupations |
| [`build_cps_panel.py`](build_cps_panel.py) | Parses 6.0M IPUMS CPS records into a 473-occupation panel via OCC2010 |
| [`cps_panel_did.py`](cps_panel_did.py) | Occupation fixed effects + event study; the age gradient does not survive, uniform shrinkage does |
| [`entry_level_inference_audit.py`](entry_level_inference_audit.py) | Audits the headline result with randomization inference; it is marginal, not p = 0.011 |
| [`stats_inference.py`](stats_inference.py) | The single correct place to compute a p-value in this project; HAC, circular-shift bootstrap, power |
| [`pvalue_purge.py`](pvalue_purge.py) | Recomputes every load-bearing claim with valid inference; the out-of-sample rate result fails |
| [`entry_level_reconciliation.py`](entry_level_reconciliation.py) | Part 5: reconciles the wage-distribution null with the CPS age finding; the wage proxy is blind on two counts |
| [`cyclical_abnormality.py`](cyclical_abnormality.py) | Part 5: repairs the nine-sector test with rank statistics, cyclical baselines, and episodes as a null |
| [`tech_capital_vs_labor.py`](tech_capital_vs_labor.py) | Part 5: the capital-side discriminator; same job losses as 2001, opposite capital conditions |
| [`occupation_ai_panel.py`](occupation_ai_panel.py) | Part 5: the acceleration test at ~700 occupations, plus the entry-level wage-distribution proxy |
| [`within_between_decomposition.py`](within_between_decomposition.py) | Part 5: shift-share; tests whether the AI effect hides between industries where fixed effects cannot see it |
| [`headline_result_stress_test.py`](headline_result_stress_test.py) | Part 5: leverage and timing checks on the one surviving AI result |
| [`robotic_exposure_test.py`](robotic_exposure_test.py) | Part 5: builds a robotic-exposure measure and tests the anticipatory-robotics hypothesis |
| [`what_the_stocks_missed.py`](what_the_stocks_missed.py) | Part 5: the rebuttal tests; young-graduate anomaly, search duration, slopes vs correlations |
| [`cps_within_occupation_age.py`](cps_within_occupation_age.py) | Part 5: the closing test; within-occupation age composition, CPS 2016-2025 |
| [`ai_intensity_ramp.py`](ai_intensity_ramp.py) | Part 5: replaces the Q4 2022 step dummy with diffusion; the ramp test that separates the two channels |
| [`entry_level_measure_reaudit.py`](entry_level_measure_reaudit.py) | The retraction of a retraction: the exposure measure was broken, and the null it produced was not evidence of absence |
| [`entry_panel.py`](entry_panel.py) | One construction of the entry-level panel, shared by every script that estimates on it; asserts the age bands tile 16-64 |
| [`section3_core.py`](section3_core.py) | Section 3: the core young-share specification, event study, and the cut-off / weighting / influence checks |
| [`section4_controls.py`](section4_controls.py) | Section 4: education and wage controls, occupation trends, placebo, and the 2020-vs-2022 break race |
| [`spec_checks_vs_canaries.py`](spec_checks_vs_canaries.py) | Part 6: the three specification checks against the published design (age band, quintiles, education) |
| [`entry_level_decomposition.py`](entry_level_decomposition.py) | Part 6: decomposes the exposure gap into levels; the exposed side does not fall |
| [`adp_cps_reconciliation.py`](adp_cps_reconciliation.py) | Part 6: walks the CPS to ADP's universe and window; neither explains the disagreement |
| [`build_cps_panel_adp.py`](build_cps_panel_adp.py) | Part 6: re-cuts the IPUMS extract to ADP's universe and emits a monthly panel |
| [`splice_diagnostics.py`](splice_diagnostics.py) | Eight BLS/CPS splice variants; the drift is a denominator artifact and the 2022 break survives 8 of 8 |
| [`exposure_confound_test_wage_education.py`](exposure_confound_test_wage_education.py) | Tests whether exposure is proxying for wage or education; it is not, and the coefficient strengthens |
| [`datapaths.py`](datapaths.py) | Resolves data filenames to their current location under `FRED-Data/`, so the project runs from a clean checkout |
| [`PAPER.md`](PAPER.md) | The paper draft; Section 5 written, remaining sections outlined |
| [`physical-sector-inversion/does_okun_break_in_recessions.py`](physical-sector-inversion/does_okun_break_in_recessions.py) | Tests whether goods-sector Okun always breaks in downturns. It does not: it works best in them |
| [`finance/`](finance/README.md) | Finance deep dive (all content also summarized in Part 3 below) |
| [`physical-sector-inversion/`](physical-sector-inversion/README.md) | Goods-sector deep dive, including the fiscal test (`fiscal_control.py`, USAspending) |
| [`generate_results_csv.py`](generate_results_csv.py) | Compiles all regression results into `results_comprehensive.csv` (12 labeled sections) |

Requires `pandas`, `numpy`, `matplotlib`, `scipy`, `openpyxl`.

---

# Part 1: The aggregate break

## Phase 1: Did Okun's law actually break?

> **Verdict: ESTABLISHED**

Take real GDP, potential GDP, the unemployment rate, and the natural rate; convert output and unemployment to gaps; then, instead of one regression across all history, re-estimate the Okun coefficient on a sliding 12-quarter window so its stability over time is visible.

![Rolling Okun coefficient and correlation](rolling_okuns_coefficient.png)

From 2000 to 2019 the coefficient stays firmly negative and the rolling correlation sits near −1.0, the rule working almost mechanically for two decades. **After Q4 2022 the coefficient swings wildly and the correlation inverts to +0.81.** The same inversion appears in the difference form of the aggregate data (peak r ≈ +0.55), so it is not an artifact of the gap specification.

**How unlikely is that, properly measured?** The normal approximation used elsewhere in this project reports p ≈ 0.0000, but it assumes normality and ignores that overlapping windows are autocorrelated, both of which understate the tail. A distribution-free circular block bootstrap (null: the pre-2022 regime simply continued, resampling the actual pre-2022 data in blocks) gives **p ≈ 0.0005**, roughly 1 in 2,000. That is orders of magnitude larger than the naive figure and still decisive, so the aggregate break survives the stricter test. See `permutation_test.py`.

Caveats: the post-2022 sample is short (~10-13 clean quarters) and the windows splice across the COVID gap. This documents a break; it does not identify a cause. Every later phase tries to.

<details>
<summary>The three supporting aggregate charts (level scatter, gap divergence, residual quadrant)</summary>

`GDPUnemployment.py` also produces `gdp_unemployment_analysis.png` (the level scatter of every quarter, and why COVID must be excluded), `gap_divergence.png` (the two gaps tracking until 2022 then running parallel), and `gap_okun_residual_quadrant.png` (the residual turning persistently red post-2022 and the recent quarters marching into the "law broken" quadrant).

</details>

---

# Part 2: Which industries, measured on unemployment

This is the part of the project that reached the wrong conclusion. It is kept in full because the correction only makes sense against it.

## Phase 2: Two industries, high AI vs low AI

> **Verdict: SUGGESTIVE**

Comparing Information (high AI exposure) against Leisure & Hospitality (low), using the difference form: post-2022, tech's rolling coefficient turns unstable and drifts positive while hospitality's stays negative. Directionally the AI story, but two industries cannot carry a general claim.

![Two-sector rolling Okun comparison](industry_rolling_okun.png)

## Phase 3: Nine industries against AI exposure

> **Verdict: CONTRADICTS AI (on unemployment), later REVERSED**

Run the difference-form test on all nine sectors, once on the 59 clean pre-cutoff quarters and once on the 13 post-cutoff quarters, and regress each sector's change in Okun coefficient (Δβ) against its AIIE exposure score.

| Industry | AIIE | β pre (sig) | β post (sig) | Δβ | Reading |
|---|---:|---:|---:|---:|---|
| Construction | −0.997 | −0.39 \*\*\* | +0.05 \*\* | **+0.44** | large inversion |
| Manufacturing | −0.484 | −0.33 \*\*\* | +0.11 \* | **+0.44** | large inversion |
| Transportation & Utilities | −0.342 | −0.26 \*\*\* | +0.16 | **+0.41** | large inversion |
| Information | 1.268 | −0.13 \*\* | +0.18 | +0.31 | inverted |
| Wholesale Trade | 0.264 | −0.17 \*\*\* | +0.07 | +0.23 | inverted |
| Professional & Business | 0.654 | −0.34 \*\*\* | −0.23 \* | +0.11 | modest |
| Leisure & Hospitality | −0.315 | −0.36 \*\*\* | −0.30 \*\*\* | +0.05 | barely moved |
| Financial Activities | 1.538 | −0.02 | −0.06 | −0.04 | held |
| Education & Health | 0.775 | −0.03 | −0.22 | −0.19 | strengthened |

Two things the significance columns add. First, the pre-2022 law was strong and precisely estimated in seven of nine sectors (the exceptions being Finance and Education & Health, where β was never distinguishable from zero, an early hint that the instrument cannot see those sectors). Second, most post-period coefficients are individually insignificant at n = 13, so the post-period story rests on the pattern across sectors, not on any single estimate.

![Nine-industry AIIE cross-section](industry_aiie_scatter.png)

The cross-sectional regression runs **the wrong way for the AI hypothesis: r = −0.61, p = 0.083.** It stays negative under the BTOS adoption measure as the regressor too (r = −0.43, n.s.), and no specification in either measure clears a Bonferroni-corrected threshold; the finding was always sign consistency rather than any single p-value. The biggest breakdowns are in low-exposure physical sectors; the high-exposure sectors (Finance, Professional & Business, Education & Health) held or strengthened. This looked like a clean refutation of the AI story. It was not. The tell is Financial Activities at "held": holding that up against the fact that finance is one of the most AI-exposed sectors in the economy is what eventually cracked the whole result open (Part 3).

**Three sector cases worth understanding before the correction:**

- **Construction:** its correlation flipped from a tight −0.75 pre to an equally tight +0.77 post, but its post coefficient is only +0.05. The relationship became very reliable without becoming economically large, a distinction the correlation number alone hides. Its pre-2022 fit is also anchored by the 2008-2012 housing crash, so some of the −0.39 baseline may reflect one crisis rather than a stable law.
- **Education & Health:** a weak relationship in both eras (|r| under ~0.21), unsurprising for a sector driven by demographics and public funding rather than the business cycle, and it carries a known output-coverage mismatch (see Methodology).
- **Financial Activities:** β near zero in both eras with unemployment pinned near 2%. On this instrument the sector is unreadable, which is the thread the whole correction pulled on.

## Phase 4: Was it interest rates?

> **Verdict: rates rejected here, but the test used lags that were too short. See the correction below and in Part 4.**

The Fed's most aggressive hiking cycle in 40 years began right at the AI cutoff, and the sectors that broke most (Construction, Manufacturing, Transportation) are the most rate-sensitive. So the Δβ estimate is re-run under a no-control baseline plus five Federal Funds Rate specifications: contemporaneous YoY change, changes lagged 2 and 4 quarters, the rate level, and the deviation from an 8-quarter rolling mean. The full matrix:

| Industry | simple | lag0 | lag2 | lag4 | level | dev | Range | All positive? |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Construction | +0.44 | +0.38 | +0.32 | +0.37 | +0.44 | +0.35 | 0.12 | yes, tight |
| Manufacturing | +0.44 | +0.31 | +0.29 | +0.39 | +0.50 | +0.31 | 0.22 | yes |
| Transportation & Utilities | +0.41 | +0.35 | +0.26 | +0.20 | +0.12 | +0.33 | 0.30 | yes, wide |
| Information | +0.31 | +0.28 | +0.21 | +0.27 | +0.30 | +0.26 | 0.11 | yes, tight |
| Wholesale Trade | +0.23 | +0.13 | +0.14 | +0.31 | +0.41 | +0.07 | 0.34 | yes, wide |
| Professional & Business | +0.11 | +0.01 | +0.02 | +0.10 | +0.20 | +0.01 | 0.20 | yes, small |
| Leisure & Hospitality | +0.05 | +0.07 | +0.00 | +0.01 | +0.06 | +0.03 | 0.07 | yes, tiny |
| Financial Activities | −0.04 | −0.09 | +0.02 | −0.01 | −0.02 | +0.01 | 0.11 | no (held) |
| Education & Health | −0.19 | +0.16 | −0.02 | −0.17 | −0.20 | +0.06 | 0.36 | no (unstable) |

![Rate-controlled sensitivity](phase2_rate_sensitivity.png)

Reading it: the breakdown survives every way of measuring rates in seven of nine sectors, and is tightest exactly where it matters (Construction, Manufacturing, Information). The two sectors that cross zero are the two that "held" anyway. Transportation and Wholesale stay positive but swing widely across specs, so their magnitudes deserve less confidence.

> **Correction: this phase's rate controls were too short, and the fix has now been run.** Every specification above uses a lag of 0, 2, or 4 quarters (`for lag in [0, 2, 4]` in [`okun_phase2_3.py`](okun_phase2_3.py)). Part 4 finds the rate-to-hiring channel peaks at **8-9 quarters**, entirely outside that range. [`extended_lag_test.py`](extended_lag_test.py) re-runs the identical specification with lags out to 12 quarters. Results in the box below.

### The extended-lag re-test

![Phase 4 re-run at extended lags](extended_lag_test.png)

The longer lags are a **harder** test, not a softer one: in the post-2022 window the lag-0 FFR level barely varies (3.64% to 5.33%, sd 0.63) because rates were high and flat, while the lag-8 version spans 0.07% to 5.33% (sd 2.37). Phase 4's original level control had almost nothing to work with.

**Result 1: Information's break survives, and this is now a much stronger claim.** Its post-2022 coefficient stays positive under every lag from 0 to 12 in both the change and level forms, never once turning negative:

| Rate control | L0 | L2 | L4 | **L6** | **L8** | **L9** | **L10** | **L12** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FFR level | +0.165 | +0.142 | +0.182 | +0.203 | +0.176 | +0.182 | +0.186 | +0.210 |
| ΔFFR (YoY) | +0.186 | +0.186 | +0.223 | +0.540 | +0.191 | +0.163 | +0.131 | +0.149 |

Tech's decoupling is not a monetary artifact at any lag tested. Construction is similarly stable (+0.043 to +0.058 throughout), so its small breakdown is not a rate artifact either.

**Result 2: the "contradicts AI" cross-section is not robust to the fix.** Regressing Δβ on AI exposure at each lag, the wrong-direction result depends entirely on which rate form is used:

| Rate control | L0 | L2 | L4 | **L8** | **L9** | **L10** |
|---|---:|---:|---:|---:|---:|---:|
| ΔFFR (YoY) | −0.63 | −0.58 | −0.50 | **−0.68** (p=.04) | −0.66 | −0.64 |
| FFR level | −0.49 | −0.73 | −0.70 | **−0.16** (p=.69) | **−0.10** (p=.80) | −0.17 |

Under the change form the negative correlation persists and even strengthens. Under the level form at the lags where the rate channel actually operates, it **collapses to nothing** (r = −0.10, p = 0.80). So Part 2's headline finding, that AI exposure predicts *less* breakdown, is specification-dependent once rates are controlled at the right horizon. It should be reported as inconclusive rather than as a contradiction of the AI hypothesis.

Neither side wins cleanly. Tech's individual break passed a genuinely harder test; the cross-sectional evidence against AI weakened to a null under half the specifications. The defensible summary is that **rates do not explain Information's decoupling, and the cross-section can no longer settle the question either way.**

![AIIE cross-section under all six specifications](phase3_cross_section.png)

The cross-sectional slope against AIIE also stays negative in every one of the six specifications (the six-panel chart above), so the unemployment-side contradiction was robust. The problem was never robustness; it was the instrument.

## Phase 5: Is the AI-exposure measure any good?

> **Verdict: VALIDATES the measure**

AIIE is a 2021 theoretical score built before ChatGPT. The Census BTOS survey asks firms directly, every two weeks, whether they used AI in the last two weeks; sector-level answers exist from November 2025, and the analysis averages 14 biweekly panels.

| Industry | AIIE rank | BTOS adoption | BTOS rank |
|---|---:|---:|---:|
| Information | 2 | 38.4% | 1 |
| Financial Activities | 1 | 28.1% | 2 |
| Professional & Business | 4 | 26.6% | 3 |
| Education & Health | 3 | 26.0% | 4 |
| Wholesale Trade | 5 | 15.2% | 5 |
| Manufacturing | 8 | 14.3% | 6 |
| Leisure & Hospitality | 6 | 13.1% | 7 |
| Transportation & Utilities | 7 | 10.1% | 8 |
| Construction | 9 | 9.9% | 9 |

**Spearman ρ = 0.917, p = 0.001**: theoretical exposure and real adoption agree almost perfectly on sector order, so the surprising Phase 3 result is not a mismeasured regressor. The one meaningful reorder is Manufacturing (AIIE rank 8, BTOS rank 6), which is adopting more AI than its occupational-exposure score suggests.

![BTOS cross-section](btos_cross_section.png)

<details>
<summary>Why the intended continuous-adoption test cannot run yet</summary>

The clean version of this study would replace the hard Q4 2022 dummy with each sector's continuously rising BTOS adoption rate and estimate an interaction (does the Okun slope weaken as adoption climbs). With sector-level BTOS existing only from November 2025, there are ~3 quarters of variation per sector, far too little to identify the interaction. Revisit around late 2026 when another year of panels exists.

</details>

## Phase 6: Was tech's break just pandemic overhiring?

> **Verdict: Overhang is real but does NOT explain tech's break**

Tech genuinely over-hired: Information employment peaked about +6% above its 2010-2019 trend in Q4 2022 and has since fallen about 7% below it. The question is whether that correction, rather than AI, produced tech's Okun inversion. Nested regressions on the Information sector:

| Model | β1 (Okun slope, post-2022) | Overhang β3 | p(β3) | VIF | Verdict |
|---|---:|---:|---:|---:|---|
| M1: no controls | +0.180 | | | | inverted |
| M2: + rate control | +0.186 | | | | benchmark |
| M3: + overhang level | +0.163 | −0.06 | 0.89 | ~19 | collinear with rates, uninformative |
| M4: + Δoverhang (clean) | **+0.150** | −0.85 | 0.21 | 1.2 | **slope barely moves** |

Two details make the null result load-bearing rather than incidental. The M3 specification is discarded honestly: overhang and the rate control move almost identically post-2022 (correlation 0.95, VIF ~19), so neither coefficient there means anything; differencing the overhang (M4) removes the collinearity (VIF 1.2). And M4 passes a placebo check: in the **pre**-period, adding Δoverhang absorbs nearly the entire Okun slope (to −0.016), proving the test can detect the mechanism when it is real. Post-2022 it moves the slope by only −0.036.

Across all eight specifications tried against it (baseline, five rate controls, two overhang controls), tech's post-2022 slope stays inside **+0.150 to +0.223**, never approaching zero. Overhiring existed; it does not explain the break.

![Overhang regression](info_overhang_regression.png)

---

# Part 3: The correction that reversed the headline

Phase 3 rested entirely on the **unemployment rate**. That is the wrong instrument for the sectors that matter most, and finding out why reversed the project's central conclusion.

## The turn: unemployment cannot see a full-employment sector

Finance was filed under "the law held." But finance output has grown far faster than its headcount, which is the textbook picture of producing more without hiring more. The reason unemployment missed it: finance unemployment is welded to its ~2% structural floor, the frictional minimum for a professional-services sector.

![Finance unemployment pinned at its floor](finance/finance_unemployment.png)

When output grows, unemployment there cannot fall any further, so the Okun test reads "no response" and scores it "held" (2013-2019 mean 2.9%; 2023-2025 mean 2.3% with a standard deviation of 0.24 points, almost no signal at all). Flat unemployment at full employment hides two opposite worlds, hiring many workers versus hiring almost none while productivity climbs, and unemployment cannot tell them apart. Employment can. The high-AI sectors (Finance, Professional & Business) are exactly the low-unemployment sectors where this blindness bites.

## Finance re-examined: a three-stage correction

The finance re-measurement went wrong twice before it went right, and the swing between the stages is the lesson (full detail in [`finance/`](finance/README.md)):

1. **Nominal (too big).** The finance output series (`VAFI`) is nominal. Using it, output looked like it doubled since 2013 and productivity rose 79%. Mostly prices.
2. **BEA finance deflator (too small).** Deflating with BEA's own Finance & Insurance deflator collapses real productivity to ~0.3%/yr, "no decoupling." But that deflator is **FISIM-contaminated**: financial output is imputed from interest-rate spreads, so when the Fed hiked, BEA booked the nominal surge as price rather than quantity. The finance deflator ran ~4.8%/yr against ~2.9%/yr economy-wide, in a pattern that tracks the rate cycle rather than inflation.
3. **Neutral GDP deflator (honest).** Re-deflated with `GDPDEF`, the answer brackets like this:

| Deflator | Real output growth | Real productivity |
|---|---:|---:|
| BEA finance deflator (FISIM-contaminated) | 1.5%/yr | 0.3-0.4%/yr |
| **GDP deflator (neutral)** | **3.8%/yr** | **2.4-2.6%/yr** |

![Real finance output under two deflators vs employment](finance/finance_real_bracket.png)

Under the neutral deflator, finance real productivity runs roughly **2.4-2.6%/yr (CAGR, endpoint to endpoint), well above the ~1.5%/yr US average**; the acceleration table below, which averages YoY growth rather than taking a single endpoint CAGR, gives the full-period figure as +2.8%/yr, a different but consistent method landing slightly higher. A NAICS fix (using Finance & Insurance employment, `CES5552000001`, instead of Financial Activities employment that includes Real Estate) barely moved anything, so the deflator was the whole story.

**And the decoupling is accelerating.** In real terms, averaging YoY growth within each period (`finance/productivity_acceleration.py`):

| Period | Real output | Employment | Real productivity |
|---|---:|---:|---:|
| 2013-2019 | +3.6%/yr | +1.4%/yr | +2.1%/yr |
| 2022-2023 | +0.2%/yr | +1.3%/yr | −1.1%/yr |
| **2024-2025** | **+5.6%/yr** | **+0.2%/yr** | **+5.5%/yr** |

![Productivity acceleration and its decomposition, finance vs tech](finance/productivity_acceleration.png)

The decomposition next to Information adds the key nuance: both of the two most AI-exposed sectors accelerate sharply in 2024-2025, by different routes. **Finance accelerates from the output side** (real output speeds up while hiring stalls at +0.2%/yr). **Tech accelerates from the labor side** (output growth holds near +6.7%/yr while employment turns negative at −2.5%/yr, outright job cuts). Tech's shape is the cleaner labor-substitution signature; finance's is consistent with AI but also with a strong financial market.

<details>
<summary>Finance caveats, kept prominent</summary>

- Even GDP-deflated, value added can be inflated by a financial-market boom rather than more real work per person, so part of the 2024-2025 spike may be a bull market. Direction robust, magnitude not.
- The GDP deflator is not exactly right for finance either; the truth is bracketed between 0.3 and ~2.6%/yr full-period, with the weight of evidence near the top given the FISIM problem.
- The rolling employment-elasticity chart for finance shows a spike to ~+0.5 in windows ending 2022; that is a COVID-rebound artifact (output and employment recovering together inside the window), not an AI signal.
- JOLTS is mixed rather than a hiring freeze: finance hires slipped (2.5% to 2.2%/mo) while openings rose (4.1% to 4.5%), so firms are posting but converting fewer hires.

</details>

## The corrected cross-section: measured on real productivity, exposure predicts the decoupling

> **Verdict: REVERSES PHASE 3. Later qualified hard: the relationship is real and robust, but it is strongest *before* generative AI, so it is not evidence AI caused it. See the loose-ends section in Part 5.**

Re-run the nine-industry cross-section on real productivity growth (real output per worker), with finance deflated by the GDP deflator and the other eight using their BEA real value added:

| Industry | AI exposure | Real productivity 2013-25 |
|---|---:|---:|
| Information | 1.27 | +7.2%/yr |
| Financial Activities | 1.54 | +2.8%/yr |
| Professional & Business | 0.65 | +2.8%/yr |
| Education & Health | 0.78 | +1.1%/yr |
| Manufacturing | −0.48 | +1.0%/yr |
| Wholesale Trade | 0.26 | +0.3%/yr |
| Leisure & Hospitality | −0.32 | +0.1%/yr |
| Transportation & Utilities | −0.34 | −0.3%/yr |
| Construction | −1.00 | −0.9%/yr |

![The headline reverses depending on the labor variable](real_productivity_ai_crosssection.png)

The three highest-AI sectors have the three highest real productivity growth rates; the lowest-exposure sectors have the lowest. Same nine industries, opposite conclusion:

| Labor variable | r vs AI exposure | p | verdict |
|---|---:|---:|---|
| Unemployment Δβ (Phase 3) | −0.61 | 0.083 | contradicts AI |
| Employment elasticity change (Δγ) | +0.28 | 0.47 | no relationship |
| **Real productivity growth** | **+0.77** | **0.016** | **supports AI** |

The middle row is included for completeness: the change in each sector's output-elasticity of employment shows no cross-sectional relationship with exposure either way, so the reversal comes specifically from the productivity lens, where the level *and* trend of output per worker are visible rather than only short-run co-movement. The project's central "contradicts AI" finding does not survive being measured on the variable AI actually targets.

## A better predictor than AIIE: the job-replaceability score

> **Verdict: A BETTER PREDICTOR of the decoupling. Same qualification as above: it predicts productivity growth best in the pre-AI window, so it is measuring a structural sector property rather than an AI effect.**

AIIE measures whether AI can *touch* a job. What determines whether Okun's law breaks is whether AI *replaces* the worker (automation) or *assists* them (augmentation). Education and Finance can have similar exposure but opposite substitution: finance tasks are largely substitutable, teaching needs a human in the room. So the project builds a replaceability score:

```
Replaceability = Exposure x (1 - Complementarity)
```

Exposure comes from Eloundou et al.'s GPT-exposure scores (beta tier, mean of human and model ratings); complementarity from five O\*NET Work Context variables that shield a job (physical proximity, face-to-face discussion, dealing with the public, responsibility for others' safety, consequence of error), normalized and averaged; the product is aggregated to industry with BLS OEWS employment weights.

| Industry | AIIE | Complementarity | Replaceability | Real productivity |
|---|---:|---:|---:|---:|
| Information | 1.27 | 0.49 | **0.325** | +7.2%/yr |
| Financial Activities | 1.54 | 0.56 | 0.267 | +2.8%/yr |
| Professional & Business | 0.65 | 0.54 | 0.233 | +2.8%/yr |
| Wholesale Trade | 0.26 | 0.56 | 0.207 | +0.3%/yr |
| Education & Health | 0.78 | **0.65** | 0.152 | +1.1%/yr |
| Manufacturing | −0.48 | 0.56 | 0.138 | +1.0%/yr |
| Transportation & Utilities | −0.34 | 0.59 | 0.120 | −0.3%/yr |
| Construction | −1.00 | 0.65 | 0.091 | −0.9%/yr |
| Leisure & Hospitality | −0.32 | 0.59 | 0.088 | +0.1%/yr |

![Job-replaceability score and its fit to real productivity](ai_replaceability_score.png)

It does what it should: **Education & Health drops from 3rd on AIIE to 5th on replaceability**, below Finance, because it has the highest complementarity in the sample (teaching and care need a human in the room). And it predicts the real decoupling **better than AIIE: r = +0.90, p = 0.001** versus +0.77, while correlating 0.87 with AIIE (a refinement, not a different universe). The purpose-built substitution measure is the strongest predictor in the project of where output decoupled from labor.

## The recency test: does the AI result survive being timed to AI?

> **Verdict: FAILS TO CONFIRM. The strongest objection survives.**

The productivity result above is measured over 2013-2025, a window that mostly predates generative AI. So the obvious objection is that it captures long-run automation rather than anything about the AI era. This is the direct test of that objection: if AI is doing the work, exposure should predict not just the **level** of productivity growth but the **change** in it, with replaceable sectors accelerating more after AI arrived relative to their own pre-AI baseline.

```
acceleration = productivity growth (2024-2025) - productivity growth (2013-2019)
```

| Industry | Replaceability | 2013-19 | 2022-23 | 2024-25 | Acceleration |
|---|---:|---:|---:|---:|---:|
| Information | 0.325 | +6.9 | +5.1 | +9.4 | +2.5 |
| Financial Activities | 0.267 | +2.1 | −1.1 | +5.5 | +3.4 |
| Professional & Business | 0.233 | +1.5 | +2.4 | +3.3 | +1.8 |
| Wholesale Trade | 0.207 | +1.1 | −4.7 | +1.0 | −0.1 |
| Education & Health | 0.152 | +0.8 | +1.4 | +0.8 | −0.1 |
| Manufacturing | 0.138 | +0.8 | −2.3 | +3.2 | **+2.4** |
| Transportation & Utilities | 0.120 | −0.1 | −1.8 | +1.8 | **+1.9** |
| Construction | 0.091 | −0.1 | −6.5 | +1.7 | **+1.8** |
| Leisure & Hospitality | 0.088 | −0.1 | −1.8 | −0.7 | −0.5 |

![The recency test: level holds, acceleration does not](recency_test.png)

**The test fails.** Acceleration against replaceability gives r = +0.45, p = 0.22, and against AIIE r = +0.26, p = 0.50. Neither is significant. The reason is visible in the bolded rows: Manufacturing, Transportation, and Construction, three of the four *least* replaceable sectors, accelerated as much as the high-replaceability ones. Meanwhile the level result on the same data stays strong (2024-25 level against replaceability, r = +0.84, p = 0.004).

Robustness, since n = 9 is underpowered and the window choice matters:

| Baseline | Post window | r | p | Spearman | p |
|---|---|---:|---:|---:|---:|
| 2013-2019 | 2024-2025 | +0.45 | 0.22 | +0.52 | 0.15 |
| 2015-2019 | 2024-2025 | +0.36 | 0.34 | +0.35 | 0.36 |
| 2013-2019 | 2023-2025 | +0.44 | 0.23 | +0.48 | 0.19 |
| 2010-2019 | 2024-2025 | +0.55 | 0.12 | +0.67 | 0.05 |
| 2013-2019 | 2025 only | +0.83 | 0.005 | +0.85 | 0.004 |

The slope is positive in all five specifications, which is worth something. But it clears significance only in the narrowest post window, which is also the most specification-searched, so that row should not be quoted as the result. Two candidate explanations for the failure, and this analysis cannot separate them: either AI's productivity effect is not yet large enough to detect against the noise in a nine-sector, two-year window, or the level relationship really is long-run automation that AI has not yet visibly changed.

**What this costs the project.** The AI claim now rests explicitly on *levels*, that the sectors with more replaceable jobs sustain higher real productivity growth, and not on a discontinuity timed to AI's arrival. That is a materially weaker claim than "AI caused a break," and the "long-run automation" caveat stays in force rather than being cleared. Reproduce with `recency_test.py`.

## Validating the score against what people actually do with AI

> **Verdict: SUPPORTS AI. The circularity objection is substantially answered.**

The replaceability score's weakest point is circularity: both of its inputs (Eloundou's GPT-exposure ratings and O\*NET complementarity) describe how automatable a job *looks on paper*, so "automatable sectors show labor-saving productivity" is uncomfortably close to restating the measure's own construction. The fix is to rebuild it from **observed behavior** instead of ratings.

The [Anthropic Economic Index](https://huggingface.co/datasets/Anthropic/EconomicIndex) publishes what people actually do with Claude, by SOC occupation: an `observed_exposure` (how much AI use an occupation shows) and a `collaboration_bucket_automation_pct` (of that use, the share where the model does the task outright rather than assisting a human). That yields a direct analog of the project's own construction, with nothing theoretical in it:

```
AEI replaceability = observed exposure x automation share
```

aggregated to the nine industries with the same OEWS employment weights (67% to 95% employment coverage per industry).

| Industry | Theoretical replaceability | AEI exposure | AEI automation share | **AEI replaceability** | Real productivity |
|---|---:|---:|---:|---:|---:|
| Information | 0.325 | 0.262 | 0.524 | **0.138** | +7.2%/yr |
| Financial Activities | 0.267 | 0.268 | 0.508 | **0.129** | +2.8%/yr |
| Wholesale Trade | 0.207 | 0.230 | 0.560 | 0.112 | +0.3%/yr |
| Professional & Business | 0.233 | 0.214 | 0.555 | 0.111 | +2.8%/yr |
| Education & Health | 0.152 | 0.135 | 0.477 | 0.070 | +1.1%/yr |
| Manufacturing | 0.138 | 0.107 | 0.579 | 0.055 | +1.0%/yr |
| Construction | 0.091 | 0.085 | 0.600 | 0.049 | −0.9%/yr |
| Transportation & Utilities | 0.120 | 0.072 | 0.647 | 0.038 | −0.3%/yr |
| Leisure & Hospitality | 0.088 | 0.038 | 0.566 | 0.018 | +0.1%/yr |

![Validating replaceability against revealed AI usage](aei_revealed_validation.png)

**Three results, one of them a surprise.**

**1. Convergent validity is remarkable.** The revealed-usage score correlates **+0.96** with the theoretical O\*NET score across the nine industries. Two entirely independent constructions, one from expert task ratings and one from millions of observed conversations, rank the industries almost identically. That is strong evidence the theoretical score was measuring something real rather than an artifact of its own assumptions.

**2. The productivity finding survives on revealed data.** AEI replaceability predicts real productivity growth at **r = +0.76, p = 0.017** (Spearman +0.80, p = 0.010), essentially matching AIIE's +0.77 and close behind the theoretical score's +0.90. Since nothing in the AEI measure is a judgment about automatability, the circularity objection is substantially answered: the relationship holds when the regressor is pure observed behavior.

**3. The surprise: automation share alone runs the wrong way.** Taken by itself, the automation-versus-augmentation split is *negatively* related to productivity (Spearman −0.78, p = 0.013). The physical sectors have the **highest** automation shares in the sample (Transportation 0.65, Construction 0.60, Manufacturing 0.58) while the knowledge sectors have the lowest (Education 0.48, Finance 0.51, Information 0.52). The reading: when a construction or transport worker does reach for AI, they hand the task over outright, they just do it very rarely (exposure 0.07 to 0.11 against 0.21 to 0.27 for knowledge work). So **usage intensity, not the automation/augmentation split, carries the industry-level signal.** That partly undercuts the theoretical elegance of "exposure times one minus complementarity," since complementarity turns out to show up as *low usage* rather than as augmentation-style usage. The composite still works because the exposure term dominates.

**4. It does not rescue the recency test.** Acceleration against AEI replaceability is r = +0.41, p = 0.28, in line with the theoretical measures. Since the failure now repeats across three independently constructed exposure measures, including one built from 2026-vintage usage data, it is a property of the data rather than of any single measure. That strengthens the case that the timing limitation is real.

Reproduce with `aei_revealed_validation.py` (streams and caches the AEI release from HuggingFace on first run).

---

# Part 4: The goods sectors, and the economy-wide hiring slowdown

> **Verdict: NOT a goods-sector story. An economy-wide, rate-driven hiring slowdown. COVID and fiscal spending ruled out. AI is not ruled out**: the nine-sector null below was later rebuilt at 73-industry scale and reverses sign; see the revisit near the end of this Part.

This part began by treating the goods sectors as a separate puzzle needing a separate cause, and ended up somewhere else entirely. It deliberately **keeps COVID in the data**, unlike the root analysis, because seeing the pandemic is the point (full detail in [`physical-sector-inversion/`](physical-sector-inversion/README.md)).

The sections below are kept in the order the work happened, because the reversals are part of the evidence: the goods-sector framing comes first, then the tests that dismantled it.

![Rolling Okun coefficient and correlation for the three goods sectors, COVID included](physical-sector-inversion/rolling_okun_inversion.png)

| Sector | AIIE | Rolling r through COVID | Inversion onset | Peak r | p (normal) | **p (bootstrap)** | Δβ |
|---|---:|---|---|---:|---:|---:|---:|
| Construction | −1.00 | −0.68 to −0.91 | 2024 Q2 | +0.82 | 0.018 | **0.036** | +0.45 |
| Manufacturing | −0.48 | −0.87 to −0.92 | 2024 Q3 | +0.68 | 0.006 | **0.031-0.046** | +0.49 |
| Transportation & Utilities | −0.34 | −0.91 to −0.97 | 2024 Q4 | +0.60 | 0.007 | **0.034-0.058** | +0.51 |

**These probabilities were revised down in significance by the bootstrap** (`permutation_test.py`). The normal approximation originally reported 0.006 to 0.018; the distribution-free version gives roughly 0.03 to 0.058, and a Bonferroni correction across the three sectors would require p < 0.017, which none of them clear. The inversions are real and simultaneous, but they should be described as **marginal** rather than clearly significant.

Three findings:

**During COVID the law held harder than ever.** Output and jobs collapsed together, then recovered together, driving the rolling correlation to its most negative values in the sample (−0.68 to −0.97). Whatever inverted these sectors, it was not the pandemic.

**The inversion is a 2024-2025 event.** Construction first (2024 Q2), then Manufacturing (2024 Q3), then Transportation (2024 Q4), reaching correlations of +0.60 to +0.82, values with bootstrap probability roughly 0.03 to 0.058 under each sector's own pre-2022 history. That timing postdates COVID by years and generative AI by roughly two years.

**They move as one cluster, and Wholesale joins it.** Manufacturing and Transportation's rolling coefficients are nearly the same series (correlation 0.92), Construction a looser third (0.73-0.78), and their raw YoY unemployment changes correlate 0.80-0.89 even with COVID removed. Scanning all nine industries for the same signature (co-moves with the cluster and inverted recently) adds exactly one member: **Wholesale Trade** (cluster correlation 0.66, 2025 rolling r +0.44). The four are the physical goods economy: build it, make it, move it, distribute it. The service sectors all stay negative through 2025, and Information's marginal inversion (+0.12) belongs to the AI story in Part 3.

![Rolling-beta correlation heatmap and the four goods sectors overlaid](physical-sector-inversion/comovement.png)

That the inverters looked like exactly the goods producers, and the holders exactly the services, seemed like the strongest hint about cause: something specific to physical production. **Pushing on that hint dissolved it.**

**The leading candidate was tested and did not survive.** `physical-sector-inversion/fiscal_control.py` pulls federal obligations by NAICS from the USAspending API and adds fiscal intensity as a third control. Three findings: the acts cannot be isolated (IIJA and CHIPS tagged obligations reach only ~0.08% of construction value added, because the money moves through states as grants, and the IRA has no fund code and works through tax credits); total federal obligations are economically meaningful but shrink the goods sectors' mean Δβ only from +0.218 to +0.189, significant in 1 of 8 sectors; and a lagged specification that appears to collapse the breakdown fails a falsification check, shrinking service sectors more than goods sectors. So the fiscal explanation is **not supported** by the best available direct test, though the test is structurally weak because federal contract data cannot see money that passes through states.

### What the goods sectors turned out to be

With COVID, rates, AI exposure, and fiscal spending all failing, `what_actually_inverted.py` and `hiring_slowdown.py` stopped hunting for a goods-sector cause and decomposed the inversion itself. The result reframes this entire part.

![The 2024-2025 hiring slowdown](physical-sector-inversion/hiring_slowdown.png)

**It is an economy-wide hiring slowdown, not a goods-sector event.** Hiring slowed in **8 of 9 sectors** in 2024-2025, by roughly 2 percentage points on average, goods and services alike. A single principal component explains **72% of the variance** in sector employment growth, and it is essentially the simple nine-sector average (correlation 0.992). AI exposure predicts neither the hiring slowdown (r = +0.19, p = 0.63) nor the productivity acceleration (r = +0.26, p = 0.50). **Both of those nulls are uninformative**, as Part 5 establishes by benchmarking: the same test returns r = +0.04, p = 0.92 on the 2001 dot-com bust, a shock that was unambiguously concentrated in technology. Do not read them as evidence against AI.

**It is not a post-pandemic over-hiring correction.** Sectors that surged hardest in the 2021-2023 rebound are not the ones slowing hardest (r = −0.22, p = 0.57), and **8 of 9 sectors now sit below their extrapolated 2013-2019 employment trend**, by 1% to 13%. An economy unwinding a hiring binge would be above trend, not below.

**It follows the rate hikes with a long lag.** The common hiring factor tracks the Fed funds rate with a correlation that rises monotonically with the lag and peaks at 8-9 quarters: **r = −0.74 excluding COVID (p < 0.0001, n = 75)**. Rates went from 0.12% in early 2022 to 5.33% by early 2024; add roughly two years of transmission and it lands exactly on the slowdown. The mechanism is standard: rate hikes do not cause layoffs, they stop firms adding people, which produces a low-hire, low-fire market where employment growth falls toward zero while unemployment barely moves.

**The natural control is the most persuasive piece.** Education & Health is the one sector with no rate sensitivity (r = +0.016, p = 0.89), and it is the one sector that did not slow hiring (+1.3pp against −2.3pp for the other eight). The single sector that ignores the rate cycle is precisely the one that ignores the slowdown.

### Two corrections this forces

**The rate hypothesis was never properly tested.** [`okun_phase2_3.py`](okun_phase2_3.py) controls for rates at lags of 0, 2, and 4 quarters (`for lag in [0, 2, 4]`). At those lags the true correlation is only −0.08 to −0.32; the peak at 8-9 quarters sits entirely outside the tested range. Part 2's "not rates" conclusion was measured with a ruler roughly half as long as needed. Re-running it with lags out to 8-12 quarters is the highest-value fix available to this study.

**The inversion itself is not robust.** `why_in_sync.py` attempted to prove the goods-sector story outright and instead broke it. The trio's synchrony is real (+0.85 average pairwise correlation, 92nd percentile of all three-sector combinations), but after removing the economy-wide common factor their residual co-movement is **−0.01**, so there is no separate goods factor; they move together because they ride one common cycle. And the inversion reverses under ordinary window choices:

| Peak rolling r since 2024 | 8q | 12q | 16q | **20q** |
|---|---:|---:|---:|---:|
| Construction | +0.84 | +0.82 | +0.66 | **+0.14** |
| Manufacturing | +0.82 | +0.68 | +0.45 | **−0.58** |
| Transportation | +0.65 | +0.60 | +0.13 | **−0.74** |
| Wholesale | +0.77 | +0.45 | +0.62 | **−0.11** |

At a 20-quarter window three of four sectors are negative again. A structural break should not depend on whether you look through a 12-quarter or 20-quarter window. **The inversion should be treated as a short-window artifact, and the hiring slowdown as the real finding.**

Honest limits: the hiring and rate results rest on n = 75 quarterly observations with a clean natural control and are solid; the inversion rests on 13 post-2022 quarters and is not. Rates are also not the only candidate for a broad hiring slowdown, since immigration and labor-force changes could produce similar timing. That objection used to sit here as an untestable caveat on the grounds that sector-level JOLTS data existed for only two of the nine sectors, which was wrong: FRED carries all four JOLTS rates for all nine. It has since been collected and tested, in Part 5 below. Correlation with a long lag is suggestive of a transmission channel, not proof of one.

### The AI question inside the goods sectors, revisited at scale

Everything above rules AI out using the same nine-sector cross-section the rest of this project eventually diagnosed as underpowered (minimum detectable correlation r = 0.82; the confidence interval on the observed r = +0.18 spans −0.55 to +0.75). The physical-sector-inversion sub-project later ran the identical exercise properly, and the conclusion changes. Full detail is in [`physical-sector-inversion/PAPER.md`](physical-sector-inversion/PAPER.md); the headline results:

**Rebuilt at 73 three-digit NAICS industries, the sign reverses and approaches significance.** [`naics3_ai_test.py`](physical-sector-inversion/naics3_ai_test.py) replaces the nine broad sectors with 73 BLS three-digit industries, and builds AI exposure from each industry's occupation mix (OEWS) times occupational exposure scores (AEI), computed from the **May 2019** mix specifically so the regressor predates generative AI and cannot be an outcome of it. With n = 65 complete cases the minimum detectable correlation drops to 0.34, so a null here is actually informative. The result: **r = −0.220 (p = 0.079)** on the 2019 mix, **r = −0.231 (p = 0.064)** on the 2025 mix, the opposite sign from the nine-sector r = +0.18. Higher AI exposure now goes with a *larger* slowdown, marginally.

**A horse race against rate sensitivity turns on one specification choice.** AI exposure and identified-shock rate sensitivity are nearly uncorrelated (r = −0.045, VIF ≈ 1), so they identify separately. Estimating rate sensitivity with shocks that overlap the 2024-2025 outcome window, rate sensitivity wins decisively (p = 0.002 vs p = 0.17 for AI). Remove the overlap (shocks through 2021 only) and the ranking flips: rate sensitivity falls to p = 0.26 while AI exposure strengthens to p = 0.076. In the specification without mechanical overlap, AI exposure is the stronger of the two predictors. Neither clears conventional significance.

**A genuine causal test (identified monetary shocks, not the raw Fed funds rate) corroborates the rate channel directionally without settling the AI question either way.** [`identified_shocks.py`](physical-sector-inversion/identified_shocks.py) replaces the endogenous policy rate with Bauer-Swanson and Jarociński-Karadi identified shock series and re-estimates as a local projection. At the pre-specified 8-quarter horizon, the contractionary sign appears in all three goods sectors and is absent in the Education & Health control, which is the strongest causal evidence in the project, but none of the three goods-sector effects reach conventional significance (Construction closest, t = −1.9). A genuine complication turns up alongside it: the "central-bank information" shock (the Fed revealing the economy is stronger than believed) is *significantly positive* in Manufacturing and Transportation, meaning two channels of opposite sign operate simultaneously and any correlation against the raw funds rate sums them together.

**The immigration objection is baseline-dependent, and the recent direction favors demand, not supply.** [`immigration_confound.py`](physical-sector-inversion/immigration_confound.py) checks Construction against the four-observable signature of a labor-supply contraction (job openings, hires-per-opening, wage growth, unemployment) under two baselines. Against 2013-2019, Construction matches a supply contraction on all four. Against the 2022-2023 peak instead, every measure reverses: vacancy yield is *recovering* (+35.4%), not deteriorating. The honest synthesis is that the post-COVID labor market is structurally supply-tighter than the 2010s, but the 2024-2025 *change* from that starting point is demand cooling, consistent with the rate channel. This also means the "hiring slowdown" measured throughout this section (2024-25 growth minus the 2013-19 trend) cannot cleanly separate a smaller workforce from weaker demand, so industries with heavier immigrant-labor reliance could show inflated slowdowns for reasons unrelated to either rates or AI.

**Even the deflating objection to the goods-sector inversion itself needed correcting.** [`does_okun_break_in_every_hike.py`](physical-sector-inversion/does_okun_break_in_every_hike.py) tests "Okun's Law always breaks when the Fed hikes" directly against all nine hiking cycles since 1954. It is false as stated (4 of 9 broke; the two largest hikes on record, +7.01pp and +5.41pp in the 1970s, did not). But the split is by era, not size: every cycle from 1994 onward broke it except the smallest one (2015-18, +1.04pp), while none before 1994 did. So the more defensible version of the objection holds: 2022-23 is the fourth consecutive meaningful modern tightening to break Okun, which does make the goods-sector inversion considerably less remarkable as a standalone event.

**Net effect on the verdict above.** "COVID and fiscal spending ruled out" stands. "**AI ruled out**" does not: the test that produced that conclusion was replaced with a properly powered one, and it points, weakly and short of significance, in the *other* direction. The physical-sector-inversion paper's own current position, after this full sequence of adversarial testing, is that the evidence here is **not evidence against an AI channel** in the goods sectors either. It directionally corroborates the rate-transmission timing story on identified shocks, while leaving the cross-industry AI question genuinely open rather than settled.

---

# Part 5: Changing the unit of observation

Everything up to this point is a nine-industry cross-section. At n = 9 the correlation needed for p < 0.05 is 0.666, so only a very large effect can ever register, and by this stage the project had demonstrated that by exhaustion. AIIE, the replaceability score, the revealed-usage score, five acceleration windows, and a rate-orthogonalized acceleration all land between r = +0.42 and +0.56, and none of them clear the bar. Measurement was never the binding constraint. Sample size was.

There is a second problem that more industries would not fix. The industry is the level at which the confounds live. Rates, tariffs, immigration, fiscal flows and demand shocks all hit an industry as a whole, so any industry-level regression of AI exposure on labor outcomes is a race between AI and everything else that varies across industries. Part 4 spent most of its effort on one of those confounds.

Two new datasets address these problems separately. JOLTS changes what is measured. OEWS changes the unit of observation.

## JOLTS: what kind of slowdown was this? (`jolts_margins.py`)

Employment is a net number, and three very different stories produce the same net fall: firms firing people (displacement), firms not backfilling attrition (a freeze), or firms unable to fill posts they have advertised (a supply constraint). JOLTS separates them, reporting job openings, hires, layoffs and quits monthly for every sector. These are unadjusted series, so seasonality is handled with 12-month trailing means rather than partial-year windows.

**Layoffs did not rise.** Comparing the latest twelve months against 2015-2019, the layoffs and discharges rate is flat in seven of nine sectors and the nine-sector mean change is −0.02pp. In Construction it fell 0.68pp. Only two sectors show materially higher involuntary separations: Information (1.14 to 1.68, +0.54) and Transportation & Utilities (+0.41). This was a hiring freeze, not a firing wave, which is what a rate-driven withdrawal of new positions looks like and is not what displacement looks like.

**One test clears, and does not survive correction.** Of five margins tested against replaceability, only the change in job openings reaches significance (r = −0.676, p = 0.045), meaning labor demand fell most where work is most replaceable. That is the right sign for an AI story and the sharpest cross-sectional result in the project outside the productivity level. It also fails Bonferroni across the five tests (which asks for p < 0.010), and its Spearman equivalent is −0.600, p = 0.088. Report it as suggestive.

**The immigration objection, tested rather than flagged.** If a shrinking labor force drove the slowdown, firms would post jobs they could not fill, so hires per opening would fall. Construction's fill rate did collapse, from 1.78 in 2015-2019 to 1.01 in 2023, but it has been *recovering* since (1.22, 1.46, 1.32), and the same trough-and-recovery shape appears in sectors with no particular immigrant intensity. The matching collapse belongs to the 2021-2023 reopening, and it is unwinding through exactly the window a 2025 immigration shock would need to be tightening it. The qualification worth keeping is that Construction's fill rate is still 26% below pre-pandemic, the largest gap of the nine, so a residual supply constraint is not excluded.

## Freeze or substitution? Job postings as the discriminating evidence (`freeze_vs_substitution.py`)

The entry-level result is the project's strongest affirmative finding, and the README states its own load-bearing ambiguity: CPS tables "cannot separate 'AI took the tasks' from 'employers froze entry hiring for AI-adjacent reasons while keeping incumbents.'" Both stories predict fewer junior hires in exposed work. They differ in what happens next.

- **Substitution**: the task is now done by software. The vacancy is destroyed. Postings fall and keep falling as capability diffuses.
- **Freeze**: the work still needs doing, but firms paused. The vacancy is deferred, not destroyed, so postings recover when the uncertainty resolves.

**Employment stocks cannot separate these and postings can.** Employment is a stock: it confounds hiring with separations and moves slowly, so a freeze and a wave of automation look identical in it for years. Postings are a flow, observed daily, and they are the firm's forward-looking statement about labour it intends to buy.

**Data.** Indeed Hiring Lab new-postings index, 44 occupational categories, daily, February 2020 to **August 2026**, the most recent data anywhere in this project. Exposure is not hand-assigned: each category maps to SOC major groups and takes the mean AEI occupational exposure within them.

![Freeze vs substitution](freeze_vs_substitution.png)

**The cross-section is significant but its tails contradict it.** Postings in 2026 relative to a 2021 base correlate with exposure at r = −0.384 (p = 0.010, n = 44). But the largest decliners include **Food Preparation (exposure 0.009, −53.7%)** and **Driving (0.006, −48.0%)**, the two least exposed categories in the sample, sitting alongside Data & Analytics (−49.5%) and Software Development (−48.6%). A relationship whose extreme observations sit at both ends of the exposure range is not measuring exposure cleanly.

**The discriminating test is the shape of the gap over time.** Scaling each group by its own 2021 base so the common decline drops out:

| Year | High exposure | Low exposure | Gap |
|---|---:|---:|---:|
| 2022 | 1.104 | 1.174 | −7.0pp |
| **2023** | 0.802 | 1.072 | **−27.0pp** |
| 2024 | 0.685 | 0.846 | −16.1pp |
| 2025 | 0.604 | 0.716 | −11.2pp |
| 2026 | 0.587 | 0.682 | **−9.5pp** |

**The gap peaked in 2023 and has closed 65% since.** That is the answer. Substitution should *widen* as capability diffuses, and AI capability improved enormously between 2023 and 2026. Instead the exposed-occupation penalty is unwinding. A gap that peaks and closes is a freeze lifting or a cyclical shock passing, not tasks being permanently absorbed by software.

**Timing is genuinely ambiguous and should not be oversold.** The gap widened −9.7pp during the hiking cycle before ChatGPT existed (March to October 2022), then −29.3pp in the ten months after it. That looks AI-timed. But that same window is exactly the tech layoff wave, which hit Software, Data, Marketing and HR for reasons widely attributed to over-hiring correction and rates. The timing cannot separate them; the unwinding can.

### What this settles, and what it does not

**Settled: the occupation-level substitution story does not hold.** At the level of whole occupations, the AI-exposed penalty is closing, not widening. This corroborates the project's own null on occupation totals from a completely independent dataset and a different measurement concept (flows rather than stocks).

**Not settled: the entry-level question, which is the one that mattered.** Indeed publishes postings by occupational category, **not by seniority**. This test cannot see the junior tier, so it cannot confirm or refute the entry-level finding. What it does is narrow the space: whatever is happening is specific to the entry margin and is *not* a wholesale destruction of exposed occupations. That makes the entry-level claim more precise and more unusual, and it means the finding cannot be dismissed as a special case of a general occupation-level collapse, because there is no general occupation-level collapse.

**What would actually settle it.** Postings data broken out by seniority or years-of-experience requirement. Lightcast has it and it is proprietary; Indeed's research team publishes entry-level cuts in write-ups but not in the open tracker. That is the single dataset acquisition that would close this question.

**Caveat on the data.** Indeed measures postings on Indeed, so a shift in employer recruiting channels registers as a decline that is not a decline in labour demand. The index is share-based within Indeed's own volume. Comparisons across categories at the same date are the defensible use; a single category's absolute level over six years is not.

## The unemployment rate cannot see what happened (`okun_employment_form.py`)

Every Okun test in this project measures output against the sector UNEMPLOYMENT RATE. That is the textbook form, and it has a structural blind spot that turns out to bind hard in this episode.

The unemployment rate is `unemployed / labor force`. It only moves when a displaced worker stays in the labor force and searches. A worker who loses a job and **exits** the labor force, through retirement, discouragement, or emigration, leaves employment but never enters the numerator. Employment can fall while the unemployment rate falls too, and an unemployment-based measure registers nothing.

**This is not hypothetical. It applies to seven of the nine sectors.** Comparing 2024-2026 against the 2013-2019 baseline:

| Sector | Employment growth | Unemployment **level** | |
|---|---:|---:|---|
| Information | −3.48 | **+0.22** | visible to both forms |
| EducHealth | +1.32 | −0.48 | employment held up |
| Construction | −2.75 | **−2.24** | **hidden** |
| Transportation | −3.10 | −0.38 | **hidden** |
| ProfBus | −3.08 | −1.30 | **hidden** |
| Manufacturing | −1.87 | −0.92 | **hidden** |
| Leisure | −1.81 | −1.09 | **hidden** |
| Finance | −1.45 | −0.58 | **hidden** |
| Wholesale | −1.11 | −0.51 | **hidden** |

Seven sectors lost employment growth **while their unemployment rate fell**. That combination is arithmetically impossible without the labor force shrinking or workers exiting the industry. Every Okun coefficient this project computed for those seven sectors was measuring a variable that had been drained of the signal.

**Information is the single exception, and that is itself informative.** It is the only sector where unemployment *rose* alongside falling employment, meaning displaced Information workers showed up as unemployed rather than leaving. Whatever hit Information did not look like the labor-force exit affecting the other seven.

**Switching the transform changes the sign of the AI result.** The project differences the unemployment rate year-over-year, which is correct for the difference form of Okun's Law, but comparing episode averages of an already-differenced series is a second difference and answers "did unemployment accelerate" rather than "is unemployment higher." Both against AI exposure, current episode:

| Measure | Spearman with AI exposure | p |
|---|---:|---:|
| unemployment, second difference (what the project used) | **−0.317** | 0.41 |
| unemployment, change in **level** | **+0.467** | 0.21 |
| employment growth | +0.183 | 0.64 |
| output-employment wedge | +0.083 | 0.83 |

The level form is the strongest of the four and the only one with the sign an AI story predicts, where more exposed sectors saw unemployment rise more. It is still not significant at nine sectors, so this is not a result. But the measure the project has been reporting nulls from was pointing the *wrong way* purely because of the transform.

**What this does and does not fix.** It explains why the Okun-coefficient tests have been returning nothing interpretable: for seven of nine sectors the dependent variable could not move in the required direction. It does not by itself produce evidence for AI, since the level-form correlation remains insignificant and the output-employment wedge, which is the cleanest displacement measure, is flat against exposure (+0.083). The honest statement is that the Okun results in this project should be treated as **not yet measured** rather than as nulls, and that any future version needs the employment form or a labor-force-adjusted unemployment measure.

## Fixing the nine-sector test rather than abandoning it (`cyclical_abnormality.py`)

The finding that the nine-sector correlation cannot detect the dot-com bust was left above as a caveat on an existing result. It deserves its own treatment, because it points at a repair rather than a dead end. If the statistic is blind, the question is whether a better statistic on the same nine sectors can see. Three things were wrong with it, and each has a fix.

**Fix 1: rank instead of Pearson. This does not work, and the reason is informative.** Pearson on nine points is hostage to a single outlier, so the rank version is the obvious repair. It fails too:

| Episode | What it was | Pearson | Spearman | Information's rank |
|---|---|---:|---:|---:|
| 1990-91 | credit crunch | +0.662 | +0.643 | 7 of 9 |
| **2001 dot-com** | **technology bust** | **+0.041** | **+0.217** | **1 of 9** |
| 2008-09 GFC | financial crisis | +0.661 | +0.667 | 8 of 9 |
| 2015-16 | oil bust | +0.088 | −0.133 | 5 of 9 |
| 2020 COVID | pandemic | +0.504 | +0.433 | 7 of 9 |
| **2024-26 current** | **the test episode** | **+0.189** | **+0.183** | **1 of 9** |

Both statistics miss 2001 entirely. But Information ranks **first of nine in exactly the two technology episodes** and fifth to eighth in every other one. The signal is in the data; the exposure index is what loses it. AIIE ranks **Finance** as the most exposed sector of the nine, above Information, and Finance does not behave like a technology-shock sector in either 2001 or now. A correlation against a mis-ordered index will be blind however it is computed.

**Fix 2: give every sector its own cyclical baseline.** Construction slows most in nearly every downturn because it is the most cyclical sector, which has nothing to do with technology. Comparing raw slowdowns across sectors therefore mostly measures cyclicality. Estimating each sector's own historical cyclical beta and predicting the current episode from it isolates the residual an AI story is actually about:

| Sector | AI exposure | Actual | Cyclical prediction | **Abnormal** |
|---|---:|---:|---:|---:|
| Transportation | −0.34 | −3.10 | −0.77 | **−2.33** |
| Information | +1.27 | −3.48 | −1.53 | **−1.95** |
| Finance | +1.54 | −1.45 | −0.45 | −1.00 |
| ProfBus | +0.65 | −3.08 | −2.59 | −0.49 |
| EducHealth | +0.78 | +1.32 | −0.52 | +1.84 |

Information slowed nearly 2pp more than its own cyclical history predicts. So did Transportation, which is the awkward part: the most abnormal sector has *low* AI exposure. The correlation is the right sign but not significant (Spearman −0.217, p = 0.58; Pearson −0.315, p = 0.41).

**Fix 3: use the episodes as a null distribution.** Nine sectors cannot calibrate a correlation, but six episodes can calibrate the whole pipeline. Running every episode through the identical procedure as if it were the test episode:

| | Episode | Spearman(abnormal, AI) |
|---|---|---:|
| **TECH** | 2001 dot-com | **−0.300** |
| **TECH** | 2024-26 current | **−0.217** |
| | 2020 COVID | +0.067 |
| | 1990-91 recession | +0.262 |
| | 2008-09 GFC | +0.350 |
| | 2015-16 industrial | +0.417 |

**The two technology episodes are exactly the two negative ones, and all four non-technology episodes are positive.** Under random ordering the chance the two pre-identified technology episodes occupy the two lowest of six positions is 1/C(6,2) = **0.067**.

That number should be read with discipline. The "bottom two" cutoff was chosen after seeing the ordering, so it is post-hoc and the nominal probability overstates the evidence. The rank-based p-value, which is not post-hoc, is 0.333, and with six episodes the smallest achievable p is 0.167, so this design cannot reach conventional significance no matter what the data show. What it does establish is that the statistic behaves differently in technology episodes than in credit, oil and pandemic episodes, and that the current episode sits on the technology side.

**The Okun version, which is the question this project actually asks, does not cooperate.** Applying the identical design to the change in each sector's Okun slope:

| Episode | Spearman(ΔOkun, AI) | p | n |
|---|---:|---:|---:|
| 2008-09 GFC | +0.383 | 0.31 | 9 |
| 2015-16 industrial | −0.150 | 0.70 | 9 |
| 2020 COVID | −0.117 | 0.77 | 9 |
| 2024-26 current | −0.217 | 0.58 | 9 |

Positive would mean more AI-exposed sectors saw their Okun slope move further toward a break. The current episode is **negative**, meaning the opposite, and it is nowhere near significance. BEA industry output starts in 2005, so only four episodes are estimable and the earlier ones drop out entirely.

**What this section establishes.** The employment-side pattern is consistent with a technology shock and behaves differently from every non-technology downturn since 1990, at a strength that cannot clear conventional significance with nine sectors and six episodes. The Okun-side pattern, which is what would be needed to claim AI is breaking Okun's Law, points the wrong way. So the honest position is that the *hiring* evidence has moved from "uninformative null" to "suggestive and pre-registrable", while the *Okun* claim specifically has no support here. The way to settle it is to state the prediction now and test it on episodes that have not happened yet, which is the one thing a six-episode design can be made to do properly.

## OEWS with industry fixed effects: the test with real power (`oews_within_industry.py`)

The unit here is the (4-digit NAICS industry × detailed SOC occupation) cell, from the BLS OEWS industry-by-occupation files, with industry fixed effects:

`Δlog(employment) = a_industry + b × replaceability + e`

Because the fixed effect absorbs everything common to an industry, `b` compares a more replaceable occupation against a less replaceable one **inside the same industry**. Construction's rate shock hits every occupation in construction, so it lands entirely in `a_industry` and cannot contaminate `b`. Same for tariffs, immigration enforcement, and sectoral demand. Sample size goes from 9 to about 28,000 cells across 247 industries and 747 occupations. Errors are clustered by occupation, since replaceability is constant within occupation across industries.

The measure's complementarity component is close to an index of how in-person a job is, and 2020-2022 was the largest shock to in-person work in modern history. So the same regression runs on three windows, and the pre-AI one is the actual test.

| window | what it is | Δlog employment | Δlog wage |
|---|---|---|---|
| 2013-2019 | placebo: pre-AI, pre-COVID | −0.143 (p = 0.245) | −0.042 (p = 0.063) |
| 2019-2025 | spans COVID and AI | −0.147 (p = 0.181) | −0.106 (p < 0.0001) |
| 2022-2025 | post-reopening AI window | −0.109 (p = 0.156) | +0.001 (p = 0.965) |

**The placebo is identical to the AI window.** The employment coefficient is about −0.14 in 2013-2019, before generative AI existed, and about −0.11 in 2022-2025. Whatever downward tilt replaceable occupations have, it was already there. This is the recency objection confirmed at the occupation level with 20,000 observations instead of 9.

**The striking wage result is COVID.** The −0.106 wage effect (p < 0.0001) appears only in the window that spans the pandemic. In the clean AI window it is +0.001, p = 0.965.

**The component split explains why.** Splitting replaceability into its two halves, exposure alone is indistinguishable from zero in every window (−0.04 to +0.04). The entire signal comes from complementarity: +0.365 (p = 0.0007) in the pre-COVID placebo, +0.504 (p = 0.0001) spanning COVID, and +0.120 (p = 0.14, not significant) in the AI window. The pattern is physical and in-person work growing relative to desk work, a long-running trend that COVID amplified and that is absent from 2022-2025. It is not a GPT-exposure effect.

**And the design has power, which is what makes the null informative.** Without industry fixed effects, the 2022-2025 employment coefficient is −0.174 with p = 0.014, significant. Adding industry fixed effects cuts it to −0.109 and kills it. The pooled relationship between AI exposure and employment is industry composition, not within-industry substitution. That directly implicates the nine-sector design this project has used throughout.

The honest caveat cuts the other way too: industry fixed effects absorb any AI effect operating at the industry level, so this design tests substitution *within* industries and is silent on reallocation *between* them. If AI shrinks whole industries rather than particular occupations inside them, this specification cannot see it. Match rates are 63%, 75% and 89% across the three windows, since NAICS and SOC revisions break exact cell matching, and BLS advises against treating OEWS as a time series at all.

## Benchmarking the episode against history (`is_the_slowdown_distinctive.py`)

Part 4 argued the slowdown is not AI-specific on two grounds: eight of nine sectors slowed, and AI exposure does not predict which ones (r = +0.18, p = 0.64). Both were asserted without a benchmark. Running the identical analysis on every episode since 1990 shows one of them holds and the other does not.

**Breadth is normal, so it is not evidence.** The median episode since 1990 slowed 8 of 9 sectors: the 1990-91 recession 8 of 8, the dot-com bust 8 of 9, the GFC 9 of 9, COVID 8 of 9. Only the 2015-16 industrial slowdown was narrow (3 of 9). "Eight of nine slowed" describes essentially every downturn and carries no information about the cause.

**The cross-sectional AI test is demonstrably blind, so its null proves nothing.** The 2001 dot-com bust is the natural check, because everyone agrees that shock was concentrated in technology. Run the same nine-sector regression on it:

| episode | r with AIIE | p | Information's rank for slowdown size |
|---|---|---|---|
| 1990-91 recession | +0.662 | 0.074 | 7 of 8 |
| **2001 dot-com** | **+0.041** | **0.916** | **1 of 9** |
| 2008-09 GFC | +0.661 | 0.053 | 8 of 9 |
| 2015-16 industrial | +0.088 | 0.821 | 5 of 9 |
| 2020 COVID | +0.504 | 0.167 | 7 of 9 |
| **2024-26** | **+0.189** | **0.626** | **1 of 9** |

AIIE returns r = +0.04, p = 0.92 on a bust that was unambiguously a technology shock. The test has a demonstrated false negative on the one case where the answer is known, which is a much stronger statement than the power calculation already noted elsewhere in this project. **The r = +0.18, p = 0.64 result in 2024-2026 cannot be read as evidence against AI.** It is the reading this project previously gave it, and that reading was wrong.

**What the correlation misses, a rank statistic catches, and it is larger than it first looks.** Information ranked first of nine in exactly the two episodes anyone would call technology shocks, and fifth to eighth in every ordinary downturn. Scoring each sector's slowdown as a z-score within its own episode makes the regularity quantitative: Information's z is +0.90, +0.60, +0.40 and +0.82 in the four ordinary downturns (mean +0.68, t = 6.09, p = 0.009), so it is reliably *more* resilient than the average sector when the economy turns down. In 2024-2026 its z is −1.06, a swing of 1.74 standard deviations from its own normal behavior. The tight band is what produces the small p on four observations, so this is a clear regularity resting on thin evidence rather than a well-powered test.

**The magnitude version is stronger than the rank version.** Fitting each sector's slowdown against the nine-sector average slowdown across the ordinary downturns only gives that sector's cyclical beta, which is then used to predict 2024-2026:

| sector | cyclical beta | predicted | actual | residual |
|---|---|---|---|---|
| **Information** | **+0.61** | **−0.64** | **−3.48** | **−2.84** |
| Transportation & Utilities | +1.03 | −0.64 | −3.10 | −2.46 |
| Professional & Business | +0.95 | −2.31 | −3.08 | −0.78 |
| Manufacturing | +0.87 | −2.46 | −1.87 | +0.58 |
| Construction | +2.90 | −4.33 | −2.75 | +1.57 |
| Education & Health | +0.32 | −0.79 | +1.32 | +2.11 |

Information's beta is +0.61, meaning it normally moves *less* than the average sector in a downturn. Given how mild 2024-2026 is on the nine-sector average (−1.93pp), it should have slowed by 0.64pp. It slowed by 3.48pp. That −2.84pp miss is the largest of the nine and it is a real anomaly, not an artifact of ordinal ranking. Caveat: four episodes and two parameters, so this is indicative rather than inference. Note also that Transportation & Utilities is nearly as anomalous at −2.46pp despite having among the lowest AI exposure in the sample.

**But the test that would have separated AI from an overhang correction fails.** The natural discriminator is output: a demand bust should show output falling alongside employment, while AI substitution should show output holding while employment falls. Annual Information GDP back to 1997 says the dot-com bust had the *same* shape, and more of it:

| window | real output | employment | productivity |
|---|---|---|---|
| 1997-2000 boom | +4.70% | +5.42% | **−0.82%** |
| 2001-2003 bust | +4.26% | −4.19% | **+8.93%** |
| 2013-2019 pre-AI norm | +4.35% | +0.98% | +3.33% |
| 2020-2022 pandemic boom | +2.23% | +2.41% | **+0.13%** |
| 2023-2025 correction | +3.88% | −2.24% | **+6.27%** |

Both corrections are preceded by a hiring boom that outran output, and both give it back at a similar rate. Tech productivity growth sagged to −0.82%/yr before the dot-com bust and to +0.13%/yr before this one, against a 2013-2019 norm of +3.33%. An overhang that built up and is unwinding accounts for the current episode with no AI in it, and it has an exact precedent. The "output holds while tech jobs fall" pattern is older than generative AI and was *larger* in 2001. (Series note: this is nominal Information GDP from the state accounts deflated by the economy-wide GDP deflator, the only consistent series reaching 1997. Its annual growth correlates r = +0.873 with BEA real value added over 2006-2025, but understates the level by about 3.9pp/yr in every period, since Information's own deflator falls. Compare rows to each other, not to BEA levels.)

**But "output holds while hiring stops" is not distinctive.** The wedge, defined as the change in mean sector output growth minus the change in mean sector employment growth, is +1.50pp in 2024-2026, against +1.24pp in the GFC and +2.21pp in COVID. Output holding up better than hiring is what downturns normally look like at the sector level. That half of the Part 4 argument survives.

**2001 is a diagnostic, not a precedent.** It is used above only to show that the nine-sector correlation cannot detect a single-sector shock. It is a poor analogy for 2024-2026 and should not be used as one, because the two episodes differ in exactly the dimension that matters:

| | 2001-2003 | 2024-2026 |
|---|---|---|
| NBER recession | yes | no |
| mean real GDP growth | +1.82%/yr | +2.45%/yr |
| unemployment | 4.2% to 6.3% (+2.1pp) | 3.7% to 4.5% (+0.8pp) |
| Information employment | −15.6% peak to trough | −10.3% peak to latest |

Information is shedding a tenth of its workforce during an expansion. In 2001 it shed a sixth inside a recession, with a collapse in telecom and dot-com investment behind it. Employment figures are quarterly averages of the monthly series, peak to trough for 2001-2003 and peak to latest for the current episode, which is still in progress. The demand shock that explains 2001 is simply absent now, which makes the current episode the harder one to explain, not the easier one.

**The labor-market mechanism, though, is close.** JOLTS starts December 2000, so both episodes are covered. Information job openings fell **28%** across the dot-com bust and **25%** now. Hires fell in both, quits fell in both. Layoffs are modestly higher now than then (monthly means of 1.54 for 2025-2026 against 1.32 for 2001-2003 and 1.36 in 2019), with essentially tied peaks (2.40 in January 2002, 2.50 in January 2026). These are unadjusted series and January is seasonally high, which is why seven of the ten highest months on record are Januaries, so read the means rather than the peaks.

**The overhang account runs out exactly where the period of interest starts.** An overhang explanation carries a hard implication: unwinding an excess of +X% returns a sector *to* its trend, not far below it. Fitting Information's log employment on 2010-2019 and extrapolating, the deviation runs +0.8% (2019), +6.0% (2022 peak overhang), **+0.3% (late 2023)**, −2.8% (2024), −4.9% (2025), −7.4% (latest). The pandemic overhang was fully worked off by late 2023, and employment kept falling for another two years. So the overhang explains 2022-2023 and cannot be what drives 2024-2026.

That said, the *level* of the deviation should not be trusted. Running the identical method on the dot-com episode, fitting 1990-2000 and extrapolating, gives −24.9% by 2005, which obviously does not mean a quarter of tech jobs were displaced. Extrapolating a prior decade's trend inflates the gap whenever structural growth slows, and 1990s Information growth was never going to continue. What survives is the timing of the zero crossing, which requires almost no extrapolation. It does not follow that AI explains the remainder, only that the overhang does not.

## The capital-side discriminator (`tech_capital_vs_labor.py`)

The overhang reading above leans on 2001 as its precedent, and that precedent does not survive being checked. The dot-com bust had a specific, measurable cause with nothing to do with the labor market: capital fled technology. If the current episode is the same kind of event, tech capital should be retreating now too. It is doing the opposite, hard.

| | 2001 dot-com bust | 2024-2026 current |
|---|---|---|
| NASDAQ over the episode | **−63.9%** (trough −65.0%) | **+132.6%** (trough +0.0%, never below its start) |
| real tech capex | **−2.6%** | **+42.8%** |
| tech share of business fixed investment | 30.0% to 28.8% (falling) | 30.0% to 34.9% (rising) |
| Information employment | **−10.5%** | **−10.3%** |

The two episodes cost Information almost exactly the same share of its jobs. Every capital variable moves in the opposite direction between them. Tech's share of all business fixed investment is now above its dot-com peak (30.1% in 2000, 33.9% in the latest four quarters, against 28.5% in 2019). Firms are putting a larger share of their capital budget into information technology than at any point in the series while cutting technology headcount.

A funding collapse cannot produce rising capex alongside falling headcount. Capital-labor substitution can, and that is close to its definition. This is the strongest single piece of evidence in the project for the AI reading, and it arrives on the capital side rather than the labor side, which is where every previous test had been looking.

**What it settles and what it does not.** It settles that the 2001 analogy does not carry: the mechanism that drove 2001 is not merely absent now, it is running in reverse. A pandemic-overhang story can still be told, but it can no longer borrow 2001's precedent. It does not settle substitution directly, because rising tech capex is also consistent with an ordinary capital-deepening boom that happens to coincide with a hiring correction. Note too that much of the recent capex is AI data-center buildout, so "firms are spending on AI while cutting staff" is descriptively true without yet showing the spending causes the cuts.

**Series note and a correction made while building this.** Tech investment is BEA's A679, information processing equipment *and software*, which already includes software. A first cut used Y033 (all nonresidential equipment) and added software separately, double-counting and producing a tech share near 60%, which should have been an immediate signal. The corrected share runs 28% to 33%. Real terms splice A679's own chain price index (1947-2013) to BEA's published real series (2007-2026); year-over-year growth rates correlate +0.995 over the 21-quarter overlap.

**Where this leaves the Information anomaly.** Three things now hold at once. Information's 2024-2026 slowdown is a real anomaly against its own cyclical history, 2.84pp worse than its beta predicts and 1.74 standard deviations off its normal-downturn resilience, occurring in an expansion. The labor-side pattern it produces is not new, since 2001 produced a larger one. But the capital conditions are the reverse of 2001, so the one concrete precedent for that labor-side pattern describes a different event. The defensible position has moved: something sector-specific is hitting Information, it is not the business cycle, and it is not a capital-withdrawal event. That is a materially narrower space than the project had before, and AI substitution is the leading occupant of it. Confirming it still needs task-level evidence, because sector aggregates cannot show which work changed hands.

## The four loose ends, tested

Three scripts close out the questions the project had left genuinely open. Two of them shut doors the AI story needed, one vindicates the surviving result against an obvious objection, and the fourth is the most consequential finding in this section.

### 1. The acceleration test, finally run with power (`occupation_ai_panel.py`)

The project's single biggest admitted weakness was the recency failure: replaceability predicts productivity *levels* but not *acceleration* after AI arrived. That was tested five ways and always at n = 9, where the critical correlation is 0.666, so the failure could always have been a power problem rather than a real limitation.

BLS OEWS national files give roughly 800 detailed occupations across four vintages, which allows the identical test at 70 times the sample size, clustered on the 22 SOC major groups. Annualized log employment growth against replaceability, by window:

| window | what it is | occupations | beta | p |
|---|---|---:|---:|---:|
| 2013-2019 | placebo, pre-AI and pre-COVID | 662 | −0.0400 | 0.096 |
| 2019-2022 | spans COVID | 706 | +0.0264 | 0.53 |
| 2022-2025 | the generative-AI window | 749 | −0.0467 | 0.22 |

The AI window coefficient (−0.047) is barely distinguishable from the pre-AI placebo (−0.040). The acceleration test itself, AI window minus placebo, gives beta = −0.035, p = 0.22 weighted, and flips sign to +0.020 unweighted. **The failure is not a power artifact.** It reproduces at n = 661 occupations with the same non-result it gave at n = 9.

**A significant result appeared here and turned out to be an artifact, which is worth recording.** A stacked difference-in-differences with occupation fixed effects across all three windows returns beta = −0.068, p = 0.0017, which looks like the timing evidence the project had been missing. Dropping the COVID window from the baseline collapses it to p = 0.125. The significance was coming from contrasting the AI window against the COVID window, when high-replaceability desk occupations grew relative to in-person ones for reasons that have nothing to do with AI. The clean pre-AI-versus-AI contrast is null.

**The component split confirms the diagnosis already found at the industry level.** Splitting replaceability into exposure and complementarity, GPT exposure alone gives −0.0172 in the placebo and −0.0185 in the AI window, essentially identical and near zero in both. Complementarity carries everything, and it is significant in the *placebo* comparison (+0.072, p = 0.004). The measure's apparent signal is its physical-work component, which was trending before AI existed.

### 2. The between-industry escape hatch is closed (`within_between_decomposition.py`)

Part 5 flagged but never tested an obvious objection to the within-industry null: industry fixed effects absorb any AI effect that operates by shrinking whole industries rather than by substituting occupations inside them. A shift-share decomposition splits each occupation's employment growth into a between-industry component (its industries grew or shrank, share held constant) and a within-industry component.

| window | regressor | between | within |
|---|---|---:|---:|
| 2013-2019 placebo | exposure alone | **−0.0149** (p = 0.019) | +0.0004 (p = 0.98) |
| 2022-2025 AI window | exposure alone | −0.0107 (p = 0.15) | −0.0062 (p = 0.75) |
| 2022-2025 AI window | complementarity | **+0.0489** (p < 0.001) | +0.0180 (p = 0.58) |

The between channel does carry signal, but it is *weaker and insignificant* in the AI window than in the pre-AI placebo, and what loads on it in the AI window is complementarity, not exposure. Between-industry reallocation is also only **10% of the variance** in occupation employment growth in both windows, which bounds how much the fixed-effects design could have been hiding. The escape hatch does not contain an AI effect.

### 3. The entry-level hypothesis, tested by proxy (`occupation_ai_panel.py`, part 4)

The leading current finding in the AI-labor literature is that displacement concentrates in entry-level work and is invisible in occupation totals. OEWS has no age or tenure field, so this uses the wage distribution: a thinning junior tier should push the 10th percentile wage up relative to the median. Testing whether that compression scales with replaceability:

| window | beta on p10/median | p |
|---|---:|---:|
| 2013-2019 placebo | +0.0183 | 0.078 |
| 2019-2022 COVID | +0.0297 | 0.21 |
| 2022-2025 AI window | +0.0048 | 0.74 |

The compression is *largest in the placebo and smallest in the AI window*. No entry-level squeeze specific to AI on this measure. The proxy is crude and cannot see the 22-to-25-year-old margin the literature actually studies, so this does not refute that work; it does mean this dataset shows no trace of it.

### 4. The one surviving result: robust to leverage, but it predates AI (`headline_result_stress_test.py`)

The productivity level result is the last AI-supporting finding standing, so it gets two checks it had never been given.

**It is not an outlier artifact.** Information sits at +7.2%/yr against +2.8%/yr for the next highest, a 4.3pp gap on a range of 8.0pp, which is exactly the setup where one point can manufacture a correlation at n = 9. Leave-one-out: the correlation ranges from +0.853 to +0.944 and stays significant when **any** of the nine sectors is dropped, on both replaceability and AIIE, in both Pearson and rank form. Excluding Information entirely, Spearman is still +0.833 (p = 0.010). This check passes cleanly.

**But the relationship is strongest before generative AI existed.**

| window | what it is | r | p |
|---|---|---:|---:|
| 2005-2013 | entirely pre-AI (GFC-contaminated) | +0.648 | 0.059 |
| **2013-2019** | **clean pre-AI benchmark** | **+0.940** | **0.0002** |
| 2013-2025 | the project's headline window | +0.896 | 0.0011 |
| 2019-2025 | weighted toward the AI era | +0.835 | 0.0051 |

The fit peaks in a clean post-GFC window that ends three years before ChatGPT, and decays monotonically as the window is shifted toward the AI era. That is the opposite of what an AI-caused relationship produces.

This is a materially sharper statement than the project's existing recency caveat. That caveat established only that the *acceleration* test was insignificant. This shows the *level* relationship itself is a pre-AI phenomenon. Replaceability is capturing a structural property of these sectors that has predicted their productivity growth since at least 2013, and generative AI did not strengthen it.

(The 2005-2013 window contains the financial crisis, which hit the two lowest-replaceability sectors hardest and can generate the correlation mechanically, so the verdict rests on 2013-2019 rather than on that row.)

> ### ⚠️ RETRACTED, and the retraction was itself corrected
> This section and the two that follow build to an entry-level displacement finding. **It does not survive**, and a reader should know that before spending the next several pages on it. Re-estimated on 6.0 million IPUMS CPS person-month records as a 473-occupation panel with occupation and year fixed effects, with 96.3% employment coverage instead of 51%, the result fails on its own design: significant pre-trends from 2018, no slope change at 2022 in any specification, and **placebo knots at 2019 and 2020 that fire harder than the real one** (p = 0.004 and p = 0.015). It is also insignificant unweighted (p = 0.139).
>
> The raw levels show why. The young share of high-exposure occupations is **flat** across the decade (6.90% in 2016 to 6.45% in 2025). The young share of *low*-exposure occupations **rose** (12.17% to 13.06%). The gap widened from the manual-work side. Young workers moved toward low-exposure work; they were not pushed out of exposed work.
>
> The sections below are kept unedited because the failure is instructive, and because one intermediate retraction was itself wrong: an audit correctly invalidated the exposure measure, then retracted only the positive result it produced while leaving standing a null from the same broken regressor. See [`entry_level_measure_reaudit.py`](entry_level_measure_reaudit.py) and the verdict section at the end.

## The rebuttal that landed: what the stocks missed (`what_the_stocks_missed.py`)

After the loose-ends section concluded there was "no identified evidence of AI-driven displacement," a rebuttal pointed at the real-world pattern that conclusion seemed to ignore: new graduates unable to find work while output grows. Diagnosing how every design in this project could miss that pattern turned up three shared blind spots, and testing them changed the verdict.

**The blind spots.** Every displacement test used employment *stocks*, but entry-level displacement stops hiring rather than firing, which appears in flows years before stocks move (and the project's own only significant JOLTS margin, openings falling most where work is replaceable at p = 0.045, had been buried under a Bonferroni caveat while "layoffs are flat" was promoted to "no displacement"; a hiring freeze is what rate transmission looks like *and* what entry-level displacement looks like, so layoffs-flat discriminates nothing). Every occupation test used occupation *totals*, which net juniors against seniors and can hide a hollowed-out entry tier completely. And the timing verdict compared correlations across windows when the economically meaningful quantity is the slope.

**1. The worker the project never tested: young college graduates.** The entry point to AI-exposed knowledge work is a 20-24 year old with a bachelor's degree. Regressing their unemployment rate on the prime-age rate (fit 2001-2019, r = +0.96, 12-month means) and tracking the residual:

| period | young grads vs cyclical prediction |
|---|---:|
| 2001-2019 fit window | +0.00pp (sd 0.40) |
| largest pre-2020 deviation ever, incl. GFC | +0.88pp |
| 2023 | +0.96pp |
| 2024 | +1.26pp |
| 2025 | +1.60pp |
| **latest (mid-2026)** | **+1.93pp, which is +4.8 sd** |

Young graduates are running almost two points above what the business cycle predicts, more than double the worst deviation in the previous quarter century, and the residual is *climbing* while the aggregate labor market normalizes. The control makes it sharp: the same adjustment for **all** 20-24 year olds, a pool dominated by non-graduates in service and physical work, sits at **−0.35pp**, slightly *better* than predicted. A degree's protection against the rest of the youth cohort has collapsed from its historical 2.9-3.7pp to **0.58pp**. Whatever is hitting young workers is selecting precisely the ones entering AI-exposed knowledge work, on a schedule that worsens through 2024-2026. At the time this was written it read as the project's first affirmative, correctly-timed displacement evidence, corroborating Brynjolfsson, Chandar and Chen (2025) from an independent source. **It did not hold** (see the retraction banner above): on 6.0M CPS records the design fails its own placebo tests, and the high-exposure young share turns out to be flat while the low-exposure share rose. Honest caveats: the residual was already elevated in the COVID disruption (+1.41 in 2021-22) before dipping in 2023, the series is a small-sample CPS cut, and unemployment among grads mixes displacement with longer search.

**2. The "nobody can find a job" anomaly is real but does not discriminate.** Conditioning on months with unemployment between 4.0 and 4.6%, the median search now runs 9.9 weeks against 7.6 historically (83rd percentile), with 22% of the unemployed out 27+ weeks against 16% historically. But the 2010s in the same band show similar durations, and a low-hire low-fire market is what the rate story predicts too. Established: "unemployment is low so the labor market is fine" is false for searchers. Not established: which mechanism.

**3. The timing verdict, corrected on slopes.** The "predates AI" conclusion rested on r falling from 0.940 (2013-19) to 0.835 (2019-25), an untestable difference at n = 9, and r measures fit tightness rather than effect size. The slope, which is the economic quantity, moves the other way: **+24.9 → +28.7 → +32.1** pp/yr per unit of replaceability across 2013-19, 2019-25, and 2022-25. The gradient *steepened* into the AI era. Neither movement is formally testable at n = 9, which cuts both ways: the earlier "predates AI, full stop" verdict rested on a difference no stronger than this one. Corrected verdict: **a pre-existing structural gradient that has steepened since 2019.** That is what AI layered on top of prior automation would look like, and also what several non-AI stories would look like. Undetermined, not dead.

**4. The synthesis that reconciles the rate story with the displacement story.** The aggregate difference-form Okun correlation peaked at +0.55 in mid-2025 and by mid-2026 is oscillating near zero, unwinding on roughly the schedule the rate-lag work predicted. The young-graduate residual is doing the opposite: still climbing. Both facts fit one picture: **the economy-wide Okun break was mostly monetary and is healing, while an entry-level displacement signal in degreed knowledge-work entrants persists and grows beneath it**, too concentrated to move aggregate Okun's Law but exactly what the anecdotal reports describe. The aggregate lens and the entry-level lens were answering different questions, and the project spent months pointing the aggregate lens at an entry-level phenomenon.

## The closing test: age within occupation (`cps_within_occupation_age.py`)

The rebuttal section had age but not occupation. CPS table 11b (employed persons by detailed occupation and age) has both, and its vintages split cleanly around the AI arrival: 2016→2019 and 2022→2025 are both three-year windows computed inside a consistent occupation classification, so one is a placebo and the other is the test, with the 2020 reclassification quarantined between them. The 2025 endpoint was verified against a user-provided extract (totals match to the thousand).

**The method point that decides it.** CPS occupation-by-age cells carry heavy sampling error, and a per-occupation regression of share changes attenuates toward zero; run naively it gives the right sign and p ≈ 0.47, which is exactly how this project's earlier designs kept missing the effect. Pooling *headcounts* into exposure groups before computing anything, the ADP-literature design, removes the attenuation.

**The result.** In the top replaceability quintile (44 occupations, 17.7M workers), over 2022-2025:

| | top quintile | bottom 80% |
|---|---:|---:|
| 20-24 employment | **−5.4%** | +6.3% |
| 35+ employment | +2.2% | |
| total employment | +0.8% | |

The young-growth gap (Q5 minus rest) by window: **+1.5pp** in the 2016-2019 placebo, **−0.6pp** in the 2019-2022 COVID bridge, **−11.7pp** in the AI window. Triple difference: **−13.1pp**, with a SOC-major cluster bootstrap p = **0.011** (the more conservative occupation-level bootstrap gives p = 0.054).

**Three signatures line up.** The age gradient is monotone: −13.1pp for 20-24, −2.8pp for 25-34, **−0.0pp for 35+**. Incumbents are untouched; entrants absorb all of it, which is what displacement at the hiring margin predicts and what a sectoral demand shock does not. The timing break sits in 2022-2025, not in the COVID window. And the composition is the concrete version of the story: accountants and auditors grew +6.9% overall while their 20-24 tier shrank; operations research analysts grew +31.9% while losing young workers; market research analysts +19.1%, same shape. An occupation that expands while its entry tier contracts has not declined. It has stopped hiring at the bottom.

**Robustness.** The triple difference holds at minimum-size cutoffs of 60k/100k/200k (−13.1/−10.9/−11.6pp), sharpens to −17.9pp for the top decile, survives leave-one-occupation-out ([−14.2, −11.3]pp), and keeps its sign under raw GPT exposure with no complementarity term (−5.3pp). This independently reproduces the Brynjolfsson, Chandar and Chen ADP-microdata finding in fully public CPS data at nearly the same magnitude.

**What it does not settle.** CPS published tables cannot separate "AI took the tasks" from "employers froze entry hiring for AI-adjacent reasons while keeping incumbents," and the exposure score is the same one whose complementarity half carries non-AI content, though the raw-exposure version keeps the sign. **Superseded.** This was written as the project's first placebo-clean, age-graded displacement result. Re-estimated on CPS microdata with proper occupation coverage it is neither: placebo knots at 2019 and 2020 fire harder than the real 2022 knot, and the exposure score behind the published version was mis-specified. See the verdict section.

## The step dummy, and the ramp test that separates the two channels (`ai_intensity_ramp.py`)

Every AI test in this project splits time with a **step dummy** at Q4 2022. That encodes an assumption nobody would defend if stated aloud: that AI's labor-market effect switched on fully the moment ChatGPT launched. It did not. GPT-4 arrived in March 2023, enterprise deployment ran through 2024, agentic coding tools through 2025. A step dummy applied to a ramping treatment is a known attenuation problem, because the post-period average blends heavily-treated late quarters with barely-treated early ones. Every null in this project's AI arm was produced under that specification, so the criticism is correct in principle and had to be tested.

**A measured adoption ramp is not available, and no substitute was invented.** Census BTOS asks firms directly whether they used AI in the last two weeks, which would be ideal. In both the project's local copies and the full national history pulled from Census, that question carries data for only **19 biweekly waves, from late 2025 onward**; the 2023-2025 history is not in the published national file. A parametric S-curve could have been substituted, but that is an assumption wearing the costume of a measurement. The diffusion story was tested through its observable implication instead: if diffusion drives the effect, the effect should build year over year.

**On occupation totals, nothing builds, so the attenuation costs nothing.** Annual OEWS files (2022, 2023, 2024, 2025) allow the exposure coefficient to be estimated one year at a time rather than endpoint-to-endpoint:

| window | replaceability | GPT exposure |
|---|---:|---:|
| 2022-2023 | −0.027 | −0.015 |
| 2023-2024 | −0.061 | −0.020 |
| 2024-2025 | −0.041 | −0.015 |

Trend across the three AI years: **p = 0.74** and **p = 0.96**. The step dummy was not concealing a growing effect on this margin. The null is a genuine null, not an artifact of the specification.

**On the entry-level margin, a strong monotone ramp.**

| series | slope/yr | t | p |
|---|---:|---:|---:|
| young-graduate penalty | **+0.304pp** | 15.9 | <0.00001 |
| all-youth penalty (placebo) | +0.163pp | 4.4 | 0.00008 |
| **graduate-specific gap** | **+0.142pp** | 4.2 | 0.0002 |

Annual means run 0.96 → 1.26 → 1.60 → 1.77pp and are still climbing. The placebo also trends up, so part of this is a general youth labor market that has deteriorated; the graduate-specific gap is the cleaner quantity and it still builds.

**The shape discriminator, which is the payoff.** Shape is identifying information. A diffusion-driven effect ramps monotonically and keeps going as adoption spreads. An effect built on an 8-9 quarter monetary transmission lag peaks and unwinds. Over 2023-2026:

| year | entry-level penalty | aggregate Okun correlation |
|---|---:|---:|
| 2023 | 0.96pp | −0.340 |
| 2024 | 1.26pp | −0.084 |
| 2025 | 1.60pp | **+0.347 (peak)** |
| 2026 | **1.77pp (still climbing)** | +0.019 |

One ramps and does not stop. The other rises, peaks, and reverses. That is the signature difference between an AI channel and a rate channel, and neither the step dummy nor any level comparison in this project could have produced it. It is the cleanest evidence the project has that these are two distinct phenomena rather than one story told two ways.

---

# Part 6: Replicating the published entry-level result, and where it disagrees

Brynjolfsson, Chandar and Chen (2026) report that between November 2022 and June 2026, employment of 22-25 year olds fell about **11%** in the two most AI-exposed occupational quintiles while rising about **10%** in the three least exposed, and read the divergence as AI displacing the entry tier of exposed work. Their primary exposure measure is the Eloundou et al. GPT-4 β rating, which is the same measure family this project has been using, and their window sits entirely inside this project's CPS microdata panel. That makes it directly testable here rather than merely comparable.

This part does three things: checks whether this project's version of the result is an artifact of specification choices, decomposes the gap into the two sides that could be producing it, and rules out the two mundane explanations for the disagreement that follows.

## The three specification checks (`spec_checks_vs_canaries.py`)

Three ways the sorting finding could have been a specification artifact, all tested against the published design.

**Age band.** This project uses 20-24; they use 22-25. The result is not band-sensitive, and it holds on the raw Eloundou score with no O\*NET term:

| specification | coef | p |
|---|---:|---:|
| **22-25 share (their band, now primary), composite** | **−0.4034** | **0.0001** |
| 20-24 share, composite exposure | −0.4446 | 0.0001 |
| 22-25 share, raw GPT-4 β | −0.3816 | 0.0002 |
| 20-24 share, raw GPT-4 β | −0.4229 | 0.0005 |

These are the corrected figures. An age-25 hole in the non-overlapping bands had been dropping every 25-year-old from the denominator, which also made the 22-25 share a ratio whose numerator was not inside it; fixing it moved the coefficients about 4% and changed no inference. **22-25 is now the primary band on evidence rather than for comparability** — see the event study in Section 3 of [`PAPER.md`](PAPER.md), where 20-24 shows four of six pre-2022 coefficients significant and fails an unweighted specification, and 22-25 does neither.

**Education.** Their abstract concedes that their patterns "attenuate when controlling for education." These do not attenuate; they strengthen. Adding Job Zone × post and log median wage × post, on 451 occupations with occupation and year fixed effects:

| band | no controls | + education | + wage | + both |
|---|---:|---:|---:|---:|
| 22-25 (primary) | −0.4034 | −0.4208 | −0.4636 | **−0.4424** |
| 20-24 | −0.4446 | −0.4967 | −0.5112 | **−0.5095** |

The pre-AI placebo on the same controlled specification (2016-2019, fake post = 2018) is clean in both bands: exposure +0.0401 (p = 0.66) for 22-25 and +0.0744 (p = 0.45) for 20-24, with the controls themselves insignificant. This is the strongest position this project holds relative to the published literature.

The controls are informative rather than collinear: exposure correlates +0.511 with Job Zone and +0.372 with log wage, and regressing exposure on both gives R² = 0.263, so **74% of the variation in exposure is orthogonal to both**.

**The pre-trend objection, tested two ways (`section4_controls.py`).** Absorbing an occupation-specific linear trend over the *full* 2016-2026 window leaves −0.1623 (p = 0.54) for 22-25. That is uninformative rather than adverse: the standard error is 2.5× the baseline's and the interval [−0.68, +0.36] contains both zero *and* the baseline −0.4004. A trend fitted through the treatment window absorbs a treatment that ramps, and the event study shows this one ramps. Fitting each occupation's trend on the **pre-period only** and extrapolating is the version a ramping effect can pass:

| | 22-25 (primary) | 20-24 |
|---|---:|---:|
| trend fitted 2016-2022 | **−0.3840 (0.0018)** | −0.2506 (0.0663) |
| ex-COVID (2020-21 dropped from the fit) | **−0.3570 (0.0073)** | −0.1966 (0.1681) |

22-25 survives near its baseline magnitude. 20-24 does not, which is the third independent diagnostic behind the band choice.

**Break date.** Entering 2020 and 2022 steps together, the 2022 term takes the whole effect (−0.3927, p < 0.001) and the 2020 term is nothing (−0.0187, p = 0.861). The timing is generative AI, not a delayed COVID reallocation.

**Quintiles.** In regression form the quintile cut agrees: a binary top-2-quintile indicator × post gives −0.2507 (p = 0.032) for 20-24 and −0.1991 (p = 0.051) for 22-25. **In levels it does not agree**, and that disagreement is the rest of this part.

## Which side opens the gap (`entry_level_decomposition.py`)

A gap of the published shape has two possible sources with different meanings. Under **displacement**, exposed occupations lose young workers in levels. Under **reallocation**, exposed occupations hold roughly flat while unexposed occupations absorb a growing share of the young cohort. Both widen the gap, and the share regression cannot tell them apart, because a share moves when either side moves.

Quintiles on the Eloundou GPT-4 β, employment weighted at the 2022 base. CPS microdata only, no BLS splice, since the window sits inside the panel. Bootstrap over occupations, 2,000 reps.

| age band | group | growth | 95% CI | p vs 0 |
|---|---|---:|---:|---:|
| **22-25** (427 occ) | top 2 exposed quintiles | **+1.9%** | [−4.0, +8.2] | 0.507 |
| | bottom 3 quintiles | **+8.7%** | [+2.3, +15.0] | **0.007** |
| | gap | −6.8pp | [−15.5, +2.2] | 0.141 |
| **20-24** (421 occ) | top 2 exposed quintiles | +2.2% | [−3.8, +8.8] | 0.526 |
| | bottom 3 quintiles | +8.2% | [+1.8, +15.0] | 0.011 |
| | gap | −6.1pp | [−15.1, +3.3] | 0.205 |
| *published (ADP)* | *top2 / bot3 / gap* | *−11% / +10% / −21pp* | | |

![Entry-level decomposition](entry_level_decomposition.png)

**The exposed side does not fall.** Its confidence interval excludes −11% decisively (p < 0.001 against that value). What is significant is the *unexposed* side rising, at p = 0.007.

**Which side opens the gap depends on the benchmark, and only one benchmark is defensible.** Zero growth answers "did the exposed side contract" (it did not). It does not answer "which side opens the gap", because young employment overall grew **+5.8%**, so the no-gap counterfactual is both groups growing at that common rate. Against the aggregate:

| | deviation | 95% CI | p | share of gap |
|---|---:|---:|---:|---:|
| exposed side underperforms | −3.90pp | [−8.9, +1.3] | 0.141 | **57.5%** |
| unexposed side outperforms | +2.88pp | [−0.9, +6.9] | 0.141 | 42.5% |

Both sides move and neither dominates, with a modest tilt toward the exposed side (20-24 gives 58.8/41.2). The two rows carry the same p-value necessarily, since the aggregate is a weighted average of the two groups and each deviation is a fixed positive multiple of the gap; they are one test reported twice, and the 3.9pp shortfall is therefore **not** independent evidence. Against a zero benchmark the same arithmetic hands the unexposed side 128% of the gap and the exposed side −28%; shares outside the unit interval are the diagnostic that the benchmark is wrong.

**The two-sided statement, which the paper carries as written.** Young employment across all occupations grew +5.8% over the same window. The exposed group grew +1.9%, a **3.9pp shortfall** against the aggregate. Underperformance relative to a growing aggregate is real. Contraction in levels is not. Those are different claims and only the first survives.

The full path, indexed to 2022 = 100, adds two things:

| year | top2 | bot3 | gap |
|---|---:|---:|---:|
| 2016 | 102.7 | 105.3 | −2.6 |
| 2017 | 103.5 | 103.4 | +0.1 |
| 2018 | 104.6 | 103.1 | +1.5 |
| 2019 | 101.2 | 103.0 | −1.8 |
| 2020 | 97.2 | 89.2 | **+8.0** |
| 2021 | 97.5 | 95.8 | +1.7 |
| 2022 | 100.0 | 100.0 | 0.0 |
| 2023 | 104.7 | 108.8 | −4.0 |
| 2024 | 103.2 | 104.3 | −1.0 |
| 2025 | 102.2 | 106.5 | −4.3 |
| 2026 | 101.9 | 108.7 | **−6.8** |

The pre-2022 gap oscillates around zero with no trend, which is the placebo result in level form. And the 2020 row is a scale check worth keeping honest about: the pandemic gap ran **+8.0pp**, larger in absolute value than the −6.8pp reached by 2026 and in the opposite direction, when in-person work absorbed the shock while exposed office work continued remotely. A gap of the 2026 magnitude is inside the range this pair of series produces under a large sectoral shock. The post-2022 movement differs in sign, timing and monotonicity, so this does not make it uninformative, but the effect is not large relative to the series' own recent history.

## Ruling out the boring explanations (`adp_cps_reconciliation.py`, `build_cps_panel_adp.py`)

A 12.9pp disagreement on the exposed side has two mundane candidate explanations before it can be called substantive: the two studies count different people, and they date from different points. `build_cps_panel_adp.py` re-cuts the same IPUMS extract by class of worker, industry and usual hours and emits a monthly panel; the reconciliation then walks the CPS to ADP's universe one restriction at a time and re-dates to their endpoints.

**Neither works.** The universe ladder (dropping unpaid family workers, the self-employed, government and agriculture, retaining 85% of the base) moves the exposed side by **−0.6pp**, from +1.9% to +1.3%. Re-dating to twelve-month windows ending November 2022 and July 2026 moves it back **+0.6pp**. Both at once:

| specification | top2 | 95% CI | p vs 0 | p vs −11% |
|---|---:|---:|---:|---:|
| as published above (all CPS, annual) | +1.9% | [−3.5, +8.4] | 0.534 | **0.000** |
| ADP universe, annual window | +1.3% | [−4.4, +7.9] | 0.673 | **0.000** |
| **ADP universe, their window** | **+1.9%** | [−3.8, +8.9] | 0.522 | **0.000** |

![ADP/CPS reconciliation](adp_cps_reconciliation.png)

Two channels do move the number and neither moves it far alone. Dropping any single industry spans −0.8% to +3.5%. Keeping only white-collar-heavy sectors, the most generous available proxy for ADP's skew toward firms large enough to outsource payroll, reaches −2.8%. Full-time only reaches −1.3%. **Stacked adversarially** (ADP universe + full-time + white-collar sectors + top quintile only), the CPS reaches **−4.7%**, still 6.3pp short, and by then only **33%** of the sample survives and the interval [−17.8, +8.8] rejects nothing in either direction, including zero (p = 0.55) and −11% (p = 0.33). The CPS runs out of power before it runs into agreement.

What is left is not something a household survey can adjudicate: ADP's firm-size skew, its client selection, and the gap between a payroll job title and a self-reported occupation.

**One bug worth recording.** The October 2025 CPS was never collected, so a twelve-month window spanning it holds eleven months. Dividing by twelve anyway understated the endpoint by roughly 8% and produced a spurious −6.9% that would have been very hard to catch inside a draft. Windows now average over the calendar months observed at both ends, which also makes them month-matched.

## What this part settles

The sorting finding is not a specification artifact: it holds in both age bands, on the raw Eloundou score with no O\*NET term, and it strengthens rather than attenuates under education and wage controls, with a clean pre-AI placebo. That is a genuine improvement on the published version of the same result, which concedes attenuation on all three counts.

The displacement *reading* of that finding does not survive in nationally representative data. The exposed side did not contract, the gap is generated almost entirely by the unexposed side rising, and neither sample universe nor window explains the discrepancy with the published ADP figure.

**The estimands have different power and the paper is explicit about it.** The share regression uses variation across 457 occupations and is significant at p = 0.0001. The levels gap compares two aggregates dominated by a handful of large occupations, and at p = 0.141 it is not significant. That is an estimand difference, not a conflict in the data. The share result establishes *that* young workers are sorted away from exposed work; the levels result establishes *where in the distribution* that happens and rejects a specific published magnitude. It does not establish a significant reallocation gap on its own, and nothing here claims one.

Drafted as Section 5 of [`PAPER.md`](PAPER.md).

---
# Where the whole thing stands

The project split one question into pieces with different answers.

## Statistical inference in this project (`stats_inference.py`, `pvalue_purge.py`)

This project produced five separate false findings from p-values, each written into a README before being caught. All five are the same error: treating overlapping or persistent observations as independent draws. The scale of the problem, from simulating two **genuinely independent** AR(1) series and asking how often each method rejects a true null at 5%:

| Persistence | Naive | Newey-West | Circular-shift bootstrap |
|---|---:|---:|---:|
| ρ = 0.00 | 7.3% | 8.0% | 7.3% |
| ρ = 0.70 | 30.0% | 14.0% | 5.3% |
| ρ = 0.90 | **53.0%** | 27.0% | **6.7%** |
| ρ = 0.95 | **57.7%** | 36.0% | **6.0%** |

Year-over-year macro growth rates have persistence around 0.9. **At that level a naive p-value rejects a true null more than half the time**, and Newey-West is still oversized at 27%. Only the circular-shift bootstrap holds its size. All inference now routes through `stats_inference.py`.

**Not everything was wrong, and the distinction is sharp.** Cross-sectional claims, one observation per sector, are valid as computed: nine sectors are nine independent units. Their problem is power, not bias, so they are now reported with a confidence interval and a minimum detectable effect.

**A second correction: over-correcting is also an error.** An earlier version of this section made the circular-shift bootstrap the universal standard. That is wrong, because it is badly underpowered: at a true correlation of 0.3 it detects the effect only 25.6% of the time, so its nulls mean "could not detect" rather than "not there." Simulation gives the right tool per question:

| Question | Correct test | Size | Power at r = 0.3 |
|---|---|---:|---:|
| Cross-sectional, independent units | ordinary Pearson | 5% | fine |
| Contemporaneous, two persistent series | **prewhitening** | 5.0% | **93.5%** |
| same, circular-shift bootstrap | underpowered | 7.6% | 25.6% |
| **Lagged effect, X at lag k predicts Y** | **distributed-lag regression + HAC** | ~12% | **96.3%** |
| same, prewhitening | wrong tool, strips the signal | 3.7% | 38.7% |
| Rolling windows | divide n by window length | | |
| Fewer than ~30 clusters | randomization inference | | |

Prewhitening is the wrong tool for a *lagged* effect, because removing the dependent variable's own dynamics deletes the channel a lagged effect propagates through. The distributed-lag regression is correct there, at the cost of running about 12% size rather than 5%.

**What changed when the load-bearing time-series claims were recomputed:**

| Claim | As published | r | Bootstrap p | |
|---|---:|---:|---:|---|
| 9-sector hiring vs FFR lag 9, 2006+ | p < 0.0001 | −0.741 | **<0.0001** | survives |
| Physical composite vs FFR lag 9, **1986-2019** | p < 0.0001 | −0.366 | **0.157** | **fails** |
| Same, full available history | not quoted | −0.368 | 0.102 | fails |

**Re-tested with the correct specification** (distributed-lag regression, which keeps the lagged rate explicit while controlling for hiring's own persistence):

| Claim | Coef | t | p | |
|---|---:|---:|---:|---|
| 9-sector hiring vs FFR lag 9, 2006+ | −0.170 | −2.51 | **0.012** | survives |
| Physical composite, **1986-2019 out-of-sample** | −0.015 | −1.35 | 0.178 | not significant |
| Physical composite, full history | −0.004 | −0.28 | 0.777 | not significant |

**The in-sample rate channel survives the correct test at p = 0.012**, which is stronger than the bootstrap-only reading suggested. **The out-of-sample validation still does not**, and that is now established with a well-powered test rather than an underpowered one, which makes it a real negative rather than an absence of evidence. So the position is: the rate-hiring relationship holds in the window that contains the episode it explains, and does not replicate before it.

**Cross-sectional claims against their own detection threshold** (minimum detectable r at n = 9 is **0.82**):

| Claim | r | 95% CI | Reading |
|---|---:|---:|---|
| Productivity decoupling vs **replaceability** | +0.90 | [+0.59, +0.98] | clears its threshold |
| Productivity decoupling vs AI exposure | +0.77 | [+0.22, +0.95] | significant but fragile |
| Rebuilt from observed Claude usage | +0.76 | [+0.19, +0.95] | significant but fragile |
| Hiring slowdown vs AI exposure | +0.19 | [−0.54, +0.76] | uninformative |
| Acceleration vs replaceability | +0.45 | [−0.31, +0.86] | uninformative |

Six of seven cross-sectional claims sit below their own minimum detectable effect. **A correlation below its detection threshold is not evidence of absence**, which is the distinction this project previously collapsed when reading nulls as evidence against AI.

**Rolling-window sample sizes must be divided by the window length.** Two 12-quarter windows one quarter apart share 11 quarters. The DESYNC test's n = 258 is an effective n of 21.5; the rolling-tau trend's n = 16 is an effective n of 1.0. None of these should be quoted with their nominal n.

### The aggregate break → **ESTABLISHED**
The output-unemployment correlation inverted from about −1.0 to +0.81 after Q4 2022 (+0.55 in the difference form). A distribution-free block bootstrap puts this at p ≈ 0.0005 under the null that the pre-2022 regime continued, so it survives the stricter test that replaced the project's original normal approximation. Stands on its own.

### A real output-to-jobs decoupling tracks replaceability → **ESTABLISHED AS A RELATIONSHIP; PREDATES AI BUT STEEPENED INTO THE AI ERA**
On unemployment the dose-response test contradicts AI, but that is an artifact of the unemployment floor in the high-AI service sectors. On real productivity, AI exposure predicts the decoupling (r = +0.77, p = 0.016), the job-replaceability score predicts it better (r = +0.90, p = 0.001), and a score rebuilt from observed Claude usage reproduces it independently (r = +0.76, p = 0.017), with the two constructions agreeing at +0.96. The relationship is also robust to leverage: it survives dropping any one of the nine sectors, including Information, in both Pearson and rank form.

**The relationship predates generative AI, but the timing verdict is weaker than first written.** The correlation is already +0.940 in 2013-2019, a clean window ending three years before ChatGPT, so the *existence* of the gradient is not an AI effect. An earlier draft went further and read the small decline in r toward the AI era as evidence AI did not strengthen it; the rebuttal section in Part 5 corrects that. At n = 9 the r differences are untestable, and the economically meaningful quantity, the slope, *steepened* into the AI era (+24.9 to +28.7 to +32.1 pp/yr per unit of replaceability). The defensible verdict is a pre-existing structural gradient that has steepened since 2019, with the cause of the steepening undetermined.

**The acceleration test also fails with real power, so that limitation is no longer a small-sample excuse.** At nine sectors the acceleration test gave r = +0.45, p = 0.22, which could always have been underpowered. Rerun across roughly 700 OEWS occupations clustered on 22 SOC major groups, it fails again (beta = −0.035, p = 0.22, sign-flipping to +0.020 unweighted), and GPT exposure alone gives near-identical coefficients in the pre-AI placebo (−0.0172) and the AI window (−0.0185).

### AI-driven displacement, at every level tested → **NOT SUPPORTED**
Totals: null. Within-industry: null. Occupation level: retracted, the exposure score was mis-specified. Entry level: fails its own placebo tests on 6.0M CPS records. The reasons differ by level and are set out below, including one retraction that had to be partly undone.
Part 5 runs the labor-side version of this test where it can actually be identified: within industry, across 28,000 occupation-by-industry cells. Replaceable occupations show no significant employment decline relative to less replaceable occupations in the same industry during 2022-2025 (β = −0.109, p = 0.156), and the coefficient is statistically indistinguishable from the pre-AI, pre-COVID placebo window (β = −0.143 in 2013-2019). The wage effect that looks strong over 2019-2025 disappears once COVID is excluded. This is a well-powered null, not an underpowered one, and it does not contradict the productivity finding: output per worker can rise without any occupation inside an industry losing employment relative to another. It does mean the project has no identified evidence for AI-driven labor *displacement*. The loose-ends section closes the three remaining ways that null could have been wrong: the acceleration test reproduces its non-result at roughly 700 occupations rather than 9 sectors; a shift-share decomposition shows the effect is not hiding in between-industry reallocation, which is only 10% of the variance and loads on the wrong component; and the entry-level hypothesis leaves no trace in the wage distribution (that third one has since been withdrawn as uninformative, see the reconciliation below). Four designs, same answer, and that answer stands for what those designs measure: totals. The rebuttal section then found what the totals hide. Young college graduates, the entry point to AI-exposed knowledge work, are running +1.93pp above their cyclical prediction (+4.8 sd, more than double the worst pre-2020 deviation including the GFC), climbing through 2024-2026 while the aggregate market normalizes, while the mostly-non-graduate 20-24 pool sits slightly *below* prediction. Displacement concentrated at the entry level of knowledge work is invisible to stocks and totals by construction; on the one margin where age is observable it is visible, correctly timed, and correctly located. The closing CPS test then confirmed it inside occupations: top-quintile-exposed occupations lost 5.4% of their 20-24 workers over 2022-2025 while their 35+ workforce grew, a triple difference of −13.1pp against the pre-AI placebo (randomization inference p = 0.056 one-sided, 0.111 two-sided; see the correction below), with a monotone age gradient and no break in the COVID window. The effect also builds year over year (+0.30pp/yr, t = 15.9), the shape diffusion predicts, while the aggregate Okun break peaked in 2025 and is unwinding.

> **Superseded by CPS microdata.** The entry-level result has now been re-estimated on 6.0 million IPUMS CPS person-month records (2016-2026) as a 473-occupation panel with occupation and year fixed effects, matched to exposure through the official Census-to-SOC crosswalk rather than by title strings. Coverage rose from 51% to **96.3% of employment**, and 458 clusters replaced roughly 12 effective ones. **The age gradient does not survive.** Employment-weighted, with occupation fixed effects:
>
> | Outcome | Coef | p |
> |---|---:|---:|
> | log employment, age 20-24 | −0.0110 | 0.002 |
> | log employment, age 25-34 | −0.0114 | <0.001 |
> | log employment, age 35+ | −0.0093 | 0.031 |
> | log TOTAL occupation employment | −0.0105 | 0.004 |
> | **young SHARE of occupation** | **−0.0249** | **0.309** |
>
> Read at the time as AI-exposed occupations shrinking uniformly rather than losing their entry tier. **That reading was wrong, and the error is instructive.** The exposure score used in this regression is broken: it averages the O\*NET work-context file across every row, and 83% of those rows are category percentages on incompatible scales that carry no cross-occupation information. The resulting complementarity term correlates with a correctly built one at **r = +0.045**. `ai_replaceability_score.py`, already in this repository, builds it correctly; `cps_panel_did.py` re-implemented it and dropped both filters.
>
> The audit that caught this retracted the *positive* result the broken score produced and left standing the *null* it produced in the same regression. A null from a broken regressor is not evidence of absence. Rebuilt with any defensible measure, the young-share coefficient moves from −0.025 (p = 0.31) to about **−0.48 (p < 0.001)**, a twentyfold change. The published-table gradient of −13.1 / −2.8 / −0.0 was still an artifact of a lossy title match covering half of employment, but "uniform shrinkage" was not the reason it failed. See [`entry_level_measure_reaudit.py`](entry_level_measure_reaudit.py).
>
> **And the replacement does not survive either.** The p = 0.004 occupation-level result was reported here for less than an hour before an audit of the exposure measure retracted it. The composite score, `exposure x (1 - complementarity)`, averages every O*NET work-context element indiscriminately, producing a distribution with skewness 11.0 where 86.8% of occupations fall below 0.01 and the four highest-scoring occupations are credit authorizers, accountants, surveying technicians, and **farmers, ranchers and agricultural managers**. A measure ranking farmers fourth on AI exposure is not measuring AI exposure.
>
> | Exposure measure | Coef | p |
> |---|---:|---:|
> | composite, as published | −0.0103 | **0.004** |
> | composite, rank transformed | **+0.0206** | 0.102 |
> | raw Eloundou exposure, no O*NET term | **+0.0236** | 0.092 |
> | raw exposure, rank transformed | **+0.0240** | 0.075 |
>
> **Every defensible alternative flips the sign to positive.** And the published version stands on two occupations: dropping the top two takes it from p = 0.004 to p = 0.163, and dropping eight flips it to significantly positive. See [`exposure_measure_audit.py`](exposure_measure_audit.py).
>
> **The corrected entry-level estimate is large and still not an AI finding, which is the actual resting place.** With a properly built measure the young-share effect survives leave-one-out across all 458 occupations at randomization-inference p = 0.0002. It fails on design instead of on power: four of six pre-2022 years are individually significant and declining from 2018, no specification finds a slope change at 2022, and **placebo knots at 2019 and 2020 produce significant slope changes (p = 0.004 and p = 0.015) while the real 2022 knot does not**. A design that fires harder on fake dates than the real one is not identifying a 2022 event.
>
> **Net position: this project has no surviving affirmative evidence of AI labor displacement.** Not in totals, not within industries, not at the occupation level, not at the entry level. What it has instead is a documented account of why each apparent finding failed, plus one result that survived every round: young workers are increasingly sorted away from AI-exposed work, a gap that widens by about 2.2pp across the decade and holds identically under the raw Eloundou score with no O\*NET term, so it is immune to the measurement dispute that sank the rest. It is a sorting fact rather than a displacement fact, and the movement predates 2022 in the levels. See [`build_cps_panel.py`](build_cps_panel.py), [`cps_panel_did.py`](cps_panel_did.py) and [`entry_level_measure_reaudit.py`](entry_level_measure_reaudit.py).

> **Correction to the headline p-value.** The entry-level triple difference was reported at p = 0.011 from a bootstrap clustered on SOC major groups. That method is not reliable here: there are only **20 clusters**, and employment is concentrated enough (top three carry 39%, Herfindahl 0.081) that the **effective count is about 12**, well below the ~30 a cluster bootstrap needs. It is also the outlier among the three methods tried. **Randomization inference**, which permutes which occupations are high-exposure and is exact regardless of cluster count, reproduces the point estimate (−13.1pp) and gives **one-sided p = 0.056, two-sided p = 0.111**, agreeing exactly with the occupation-level bootstrap. The effect is 1.59 null standard deviations from zero.
>
> **The finding is therefore marginal, not significant at 5%.** What is unaffected is the supporting structure, because it consists of design features rather than p-values: the monotone age gradient (−13.1 / −2.8 / −0.0 across 20-24, 25-34, 35+), the break landing in the AI window rather than the COVID bridge, the clean 2016-2019 placebo, and leave-one-occupation-out stability of [−14.2, −11.3]pp. Those are what make the result worth taking seriously despite the p-value. See [`entry_level_inference_audit.py`](entry_level_inference_audit.py).

### The goods-sector inversions → **NOT A SEPARATE MECHANISM: an economy-wide, rate-driven hiring slowdown, and AI is not ruled out here either**
Construction, Manufacturing, Transportation, and Wholesale appeared to invert together in 2024-2025 with the lowest AI exposure in the sample, which looked like a distinct goods-sector puzzle. The fiscal wave does not explain it (tested directly against USAspending obligations by NAICS and **not supported**). Decomposing the inversion resolved it: hiring slowed in **8 of 9 sectors**, one common factor explains **72%** of sector employment growth, and that factor tracks the Fed funds rate lagged 8-9 quarters at **r = −0.74** (circular-shift bootstrap p < 0.0001, n = 75, 2006-2026), and now directionally corroborated on identified monetary policy shocks (contractionary sign in all three goods sectors at the predicted 8-quarter horizon, absent in the control, though not individually significant). The clinching detail is the natural control: Education & Health is the only sector with no rate sensitivity (r = +0.016) and the only one that did not slow hiring.

Two things follow. First, Phase 4's rejection of the rate hypothesis used lags of 0, 2, and 4 quarters and therefore never tested the channel, which peaks at 8-9. Second, the inversion itself is **not robust**: at a 20-quarter rolling window three of the four sectors turn negative again (Transportation −0.74, Manufacturing −0.58), and the trio's synchrony vanishes once the economy-wide factor is removed (residual co-movement −0.01, so there is no separate goods factor). The hiring slowdown is the finding; the inversion is a short-window artifact and should not be carried into a write-up as a structural break.

**A third thing follows, and it reverses this section's original AI conclusion.** The nine-sector "AI exposure predicts none of this" claim was underpowered (minimum detectable r = 0.82). Rebuilt at 73 three-digit NAICS industries with a properly constructed, pre-AI-dated exposure measure, the correlation reverses sign and approaches significance (r = −0.22 to −0.23, p ≈ 0.06-0.08), and in the cleanest specification (no mechanical overlap between the rate-sensitivity estimation window and the outcome window) AI exposure is the stronger of the two predictors, though neither reaches conventional significance. The defensible statement changed from "AI exposure predicts none of it" to "AI exposure is not ruled out, and the properly powered test points weakly toward it." Full detail in the AI subsection near the end of Part 4 and in [`physical-sector-inversion/PAPER.md`](physical-sector-inversion/PAPER.md).

### Reconciling the two entry-level results (`entry_level_reconciliation.py`)

> **Now largely moot, retained for one durable point.** This section reconciled a wage-based null against the entry-level age finding, and the age finding has since been retracted on other grounds (placebo knots, pre-trends). What survives and is still worth keeping is the demonstration that the wage proxy was *never informative*: it does not track age composition (r = +0.04 and −0.06), and the effect it was asked to detect is roughly 11 times smaller than its own noise floor. That is a lesson about proxy validation independent of which result turned out to be right.

Two results in this project pointed opposite ways and were both asserted without being connected. `occupation_ai_panel.py` reported that the entry-level hypothesis "leaves no trace in the wage distribution." `cps_within_occupation_age.py` then found exposed occupations lost 5.4% of their 20-24 workers, triple difference −13.1pp, p = 0.011. A referee would have gone straight at that gap.

The wage test had no age field, so it used a proxy: if the junior tier thins, the 10th percentile wage should rise relative to the median. **That proxy fails on two independent grounds, and the wage null carries no information about the age hypothesis.**

![Entry-level reconciliation](entry_level_reconciliation.png)

**1. The proxy does not track age composition at all.** Joining OEWS wage percentiles to CPS occupation-by-age tables through SOC codes, and correlating the change in the 20-24 share against the change in log(p10/median) across matched occupations:

| Window | n matched | corr | p |
|---|---:|---:|---:|
| 2019-2022 (spans COVID) | 161 | +0.043 | 0.587 |
| 2022-2025 (AI era) | 211 | −0.061 | 0.382 |

Essentially zero in both. Occupations that actually lost young workers show no more wage compression than those that did not. The measure was never observing what it was assumed to observe.

**2. Even a valid proxy could not have detected this effect.** The arithmetic is decisive. The 20-24 group averages 8.3% of employment in these occupations, so losing 5.4% of them removes **0.45% of total employment** from the bottom of the distribution. Propagating that through the observed p10-to-median wage gradient gives an implied compression of **0.0048 log points**, against an observed standard deviation of **0.0546**. The effect the age data found is roughly **11 times smaller than the noise floor** of the wage measure. No sample size would have found it.

**3. What the contrast does suggest.** In the matched subsample the exposed-minus-unexposed difference in young-share change is −0.99pp (p = 0.148, so directionally right but not significant here, since 211 matched occupations and a simple difference is far weaker than the full-sample triple difference), while the wage-compression difference is +0.0014 (p = 0.893), essentially exactly zero. **Quantity moves while price does not**, which is the signature of a hiring freeze rather than wage-competition displacement.

**Resolution.** The two results do not conflict. The wage-distribution test was blind to the effect by construction, on two counts, and should no longer be cited as one of the designs that returned a null against the entry-level hypothesis. The relevant caveat on the age finding is the one already stated in its own section: published CPS tables cannot separate "AI took the tasks" from "employers froze entry hiring for AI-adjacent reasons." This section makes the freeze reading somewhat more likely, because a pure task-substitution story with wage competition should have moved prices at least a little, and it moved them not at all.

### Young workers are sorted away from AI-exposed work → **ESTABLISHED; THE DISPLACEMENT MAGNITUDE IS REJECTED, THE MECHANISM IS NOT RESOLVED**

The one result that survived every round of scrutiny, now with a regression form and an external comparison (Part 6). With occupation and year fixed effects across 451 occupations, the young-share coefficient on exposure is −0.4632 (p = 0.0001) for 20-24 and −0.4200 (p = 0.0001) on the 22-25 band, holds on the raw Eloundou score with no O\*NET term, **strengthens** under education and wage controls, has a clean pre-AI placebo, and survives all eight BLS/CPS splice variants.

The displacement reading of that sorting does **not** survive. Decomposed into levels, employment in the two most exposed quintiles grew +1.9% over 2022-2026 (95% CI −4.0 to +8.2), against −11% reported in ADP payroll data, and the interval rejects that figure at p < 0.001. Neither sample universe (−0.6pp) nor window (+0.6pp) explains the discrepancy, and an adversarially stacked specification reaches only −4.7% on a third of the sample. Exposed occupations underperformed the aggregate by 3.9pp and did not contract, which is what displacement requires.

**What the levels do not settle is which side opens the gap.** Benchmarked against aggregate young employment growth (+5.8%), the split is 57.5% exposed / 42.5% unexposed, and neither deviation is significant (p = 0.141 for both, necessarily, since they are one test). An earlier version of this section reported that 128% of the gap came from the unexposed side; that figure used zero growth as the benchmark and truncated a positive growth rate at zero, so it could not have reported anything else. It is withdrawn.

Note the estimands differ in power: the share regression is significant at p = 0.0001 across 457 occupations, the levels gap is not (−6.8pp, p = 0.141), because group aggregates are dominated by a few large occupations. One qualification belongs on the record: the most demanding trend specification, with occupation trends fitted over the full window, is uninformative rather than supportive, and a reader who holds that specification to be the right one should treat the share result as unproven rather than established. The share result establishes *that* the sorting happens; the levels result establishes *where in the distribution* and rejects a published magnitude. Neither this project nor the paper claims a significant reallocation gap in levels.

### Tech's break survived everything thrown at it → **BEST-STRESS-TESTED SINGLE RESULT**
Information's post-2022 slope stays inside +0.150 to +0.223 across eight specifications (baseline, five rate controls, two overhang controls), and its real productivity (+7.2%/yr, with genuine falling deflators, no FISIM issue) is the highest in the sample while its 2024-2025 employment is shrinking.

### What this is not
Correlation, at n = 9. Two objections were tested directly rather than left as caveats, and both bit: the overlapping-window problem (a block bootstrap raised the aggregate p from 0.0000 to 0.0005, and the physical sectors from ~0.007 to ~0.04) and the long-run-automation objection, which the recency test **failed to overturn** (and fails against the revealed-usage measure too), since exposure does not significantly predict the post-2022 acceleration in productivity growth. That objection therefore stands: the gradient is long-run automation as far as this evidence can tell. The circularity worry (AIIE and the replaceability score are both built from task automatability, so the finding risks restating its own construction) was tested by rebuilding the measure from observed AI usage; it reproduced at r = +0.76 and agreed with the theoretical score at +0.96, so this objection is substantially answered rather than outstanding. Finance's magnitude depends on a deflator judgment. The defensible claim is precise and narrow: the original "contradicts AI" headline does not survive correct measurement, and sectors whose jobs are more replaceable by AI sustain materially higher real productivity growth, including in 2024-2025. What is *not* established is that generative AI caused a discontinuity at its arrival. The physical-sector sub-project ran the same n=9 fix for real (73 industries instead of nine) and got a different answer, the AI correlation reversed sign, which is the clearest demonstration in this repository that the small-n problem was not a rhetorical caveat.

## Methodology bugs and errors caught

Documenting these is part of why the surviving findings are trustworthy.

<details>
<summary>Bug 1: mislabeled Δβ axis on the AIIE scatter</summary>

The Phase 3 chart originally annotated the axis so that a more-negative Δβ meant more weakening; the sign was backwards. Corrected, the cross-sectional slope's real direction (contradicting the naive AI story on unemployment) became visible.

</details>

<details>
<summary>Bug 2: duplicate rate specification</summary>

Two supposedly different rate specs ("FFR level" and "FFR deviation from a fixed mean") were identical, since subtracting a constant leaves an OLS slope unchanged. Replaced with a rolling 8-quarter deviation that carries independent information.

</details>

<details>
<summary>Bug 3: backwards lag direction on the rate control</summary>

The lag-2 and lag-4 rate specs used `shift(-lag)` (future values) instead of `shift(+lag)` (true lags), which dropped post-period observations and produced a spurious "conventional significance" that reversed once fixed.

</details>

<details>
<summary>Bug 4: sign convention for Transportation & Utilities</summary>

Transportation's Δβ was reported as a "sign flip" (−0.116) when the correct value under Δβ = β_post − β_pre is +0.117. It shrinks under the rate control but does not reverse.

</details>

<details>
<summary>Error 5: nominal finance output (the big one)</summary>

The finance re-examination first reported nominal output ("doubled, +79% productivity"), which is mostly inflation. This produced a dramatically overstated decoupling that was later corrected to real terms. Two finance scripts that still carried the nominal series were also corrected to deflate in-script.

</details>

<details>
<summary>Error 6: over-trusting the FISIM-broken finance deflator</summary>

The first correction of Error 5 deflated finance with BEA's own finance deflator and concluded "no decoupling" (0.3%/yr). That deflator is FISIM-contaminated and understates real finance output; the neutral GDP deflator gives the honest ~2.4-2.6%/yr. Swinging from a nominal overstatement to trusting a known-broken deflator is its own error.

</details>

<details>
<summary>Repository issue: broken data paths and a real/nominal swap</summary>

At one point every script's data path silently broke when the data folder was renamed, and a reorganization swapped the real finance output series for a nominal one. Both were caught by re-running the full pipeline and auditing series identities.

</details>

## Glossary

<details>
<summary>Okun's Law; gap form vs difference form</summary>

The empirical negative relationship between output and unemployment. Gap form (`U_gap = c·Y_gap`, aggregate only, needs potential-output estimates) is used in Phase 1; difference form (`ΔU = β·%ΔY`, works per industry) is used in Phases 2-6.

</details>

<details>
<summary>β, Δβ, and the employment elasticity γ</summary>

β is the difference-form Okun slope (unemployment change per 1% output growth); Δβ = β_post − β_pre is how much it changed after Q4 2022, positive meaning the law weakened. The employment elasticity γ is the analogous slope for *employment* growth on output growth; classic Okun implies γ ≈ +0.5 to +0.7, and γ near zero or negative means output and jobs have decoupled.

</details>

<details>
<summary>Real vs nominal value added, the GDP deflator, and FISIM</summary>

Nominal value added is in current dollars; real value added removes price inflation. A deflator is the price index used to convert one to the other. The GDP deflator (`GDPDEF`) is the economy-wide price index. FISIM (Financial Intermediation Services Indirectly Measured) is how BEA imputes bank output from interest-rate spreads; it makes the finance-specific deflator unreliable, especially when rates move, which is why finance is deflated with the GDP deflator here.

</details>

<details>
<summary>Productivity (output per worker)</summary>

Real output divided by employment. Its growth rate equals real output growth minus employment growth. Rising productivity with flat hiring is the signature of output decoupling from labor, which is what AI-driven substitution would produce.

</details>

<details>
<summary>AIIE, replaceability, and augmentation vs automation</summary>

AIIE (Felten, Raj & Seamans 2023) scores AI *exposure*, whether AI can touch a job's tasks. Replaceability (built here) scores *substitution*: exposure times one minus complementarity, where complementarity is how much a job resists substitution (physical presence, human contact, accountability). Augmentation means AI assists the worker (Okun holds); automation means AI does the job (Okun breaks). The distinction is what AIIE misses and replaceability captures.

</details>

<details>
<summary>BTOS, FFR, rolling window, overhang, VIF, Bonferroni, Spearman ρ, YoY</summary>

BTOS: Census Business Trends and Outlook Survey, real firm-level AI adoption (sector-level from Nov 2025, 14 biweekly panels used here). FFR: Federal Funds Rate. Rolling window: re-fitting a regression on each trailing N quarters (here 12). Overhang: tech employment's deviation from its 2010-2019 trend (+6% at Q4 2022, about −7% by 2026). VIF: variance inflation factor, a collinearity diagnostic (over ~5 flagged, over 10 severe). Bonferroni: a multiple-comparisons correction; with five distinct rate specs, per-test significance requires p < 0.01, which no unemployment-side spec cleared. Spearman ρ: rank correlation. YoY: year-over-year (4-quarter) differencing, used to cancel seasonality.

</details>

## Result files

`results_comprehensive.csv` compiles every regression in 12 labeled sections (study design, pre/post β with SEs and significance, the Δβ×spec matrix, full coefficient tables, exposure measures, cross-sections under both AIIE and BTOS, overhang models with collinearity diagnostics, and BTOS methodology notes). `okun_industry_summary.csv`, `phase2_results.csv`, `phase3_cross_section.csv`, `btos_beta1_table.csv`, and `btos_sector_ranking.csv` hold the per-analysis outputs; `okun_industry_detail.xlsx` has per-industry detail sheets.

## Reproducing this

1. Download the FRED series referenced in each script's header into `FRED-Data/` at the repo root (gitignored), plus the O\*NET Work Context file, Eloundou GPT-exposure scores, and the OEWS national sector file for the replaceability score.
2. `pip install pandas numpy matplotlib scipy openpyxl`
3. Run the aggregate and phase scripts, then `real_productivity_ai_crosssection.py` and `ai_replaceability_score.py` for the correction, and the scripts in `finance/` and `physical-sector-inversion/` for the two deep dives.

All numbers here are verified against the committed result CSVs and regenerated from the current data.
