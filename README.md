# Okun's Law in the AI Era

**Is the historical link between economic output and unemployment weakening because of AI, and if so, where?**

For 60 years there has been a reliable rule in economics: when the economy grows faster than usual, more people get hired and unemployment falls. Every 1 extra point of growth has historically pulled unemployment down by about half a point. If AI now lets firms produce more without hiring proportionally more workers, that rule should start to fail, and every policymaker who leans on it (the Federal Reserve, the CBO, the White House) would have to rebuild their playbook.

This project set out to test that, reached a conclusion that seemed to *contradict* the AI story, and then discovered the conclusion was an artifact of measuring the wrong labor variable. The corrected answer supports the AI story. The whole arc, including the wrong turn and the correction, is documented below, because how the answer flipped is as important as the answer.

## The bottom line

1. **A real, statistically extreme break in the growth-to-jobs relationship appears after Q4 2022 in the aggregate U.S. economy.** The rolling output-unemployment correlation, near −1.0 for two decades, inverts to +0.81, something the historical distribution essentially never produces.
2. **Whether that break looks like AI depends entirely on how you measure labor.** Measured on unemployment, AI exposure predicts *less* breakdown (the "contradicts AI" result). But unemployment is saturated for the high-AI service sectors, which sit at their unemployment floor and cannot register a decoupling. Measured on **real productivity** (real output per worker, the variable AI actually targets), AI exposure significantly *predicts* the output-to-jobs decoupling (r = +0.77, p = 0.016). A purpose-built job-replaceability score predicts it even better (r = +0.90, p = 0.001).
3. **There is a second, separate story in the physical economy.** The biggest unemployment-side inversions landed in Construction, Manufacturing, Transportation, and Wholesale, the low-AI goods sectors, and arrived in 2024-2025. Those most likely reflect the 2021-2022 fiscal spending wave (IIJA, CHIPS Act, IRA), not AI. This has its own [sub-project](physical-sector-inversion/README.md).

So the honest headline is: the aggregate break is real; the AI-driven part of it lives in the high-replaceability sectors (Information and Finance most clearly) and is visible in productivity, not unemployment; and a fiscal-driven part lives in the goods sectors.

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

Two conventions in the tables: **positive Δβ** means Okun's law weakened in a sector (measured on unemployment); **higher real productivity growth** means output outran labor (the decoupling, measured properly).

## Data sources

All macro data is from [FRED](https://fred.stlouisfed.org/). The aggregate analysis uses real GDP (`GDPC1`), potential GDP (`GDPPOT`), the unemployment rate (`UNRATE`), and the natural rate (`NROU`). The industry analysis adds, per sector, BEA real value added, BLS unemployment, BLS employment (headcount) and hours, and JOLTS hires and openings, plus `FEDFUNDS` for rate controls and `GDPDEF` (the GDP deflator) for real-terms corrections. The exposure measures are the [Felten, Raj & Seamans (2023)](https://onlinelibrary.wiley.com/doi/10.1002/soej.12558) AI Industry Exposure (AIIE) index, the Census Bureau's BTOS AI-adoption survey, and, for the replaceability score, [Eloundou et al. (2023)](https://github.com/openai/GPTs-are-GPTs) GPT exposure, O\*NET Work Context, and the BLS OEWS industry-occupation matrix. Raw data lives in a gitignored `FRED-Data/` folder.

## Methodology

**Gaps (aggregate).** Raw GDP cannot be compared across decades, so both output and unemployment are converted to deviations from normal: the output gap `(GDP − GDP_potential)/GDP_potential` and the unemployment gap `U − NROU`. Under Okun's law they move in opposite directions.

**Difference form (industry).** Sectors have no published potential output or natural rate, so the industry work uses `ΔU = β·%ΔY`, the change in a sector's unemployment against its output growth, both as year-over-year differences (which cancel the seasonality in the not-seasonally-adjusted sector unemployment series). YoY differences are computed before any rows are dropped, since pandas differencing is positional.

**Excluding COVID.** Q2 2020 through Q1 2021 is dropped from the aggregate regressions (the shutdown was a policy shock, not an economic relationship). The industry pipeline also drops the rebound quarters through Q1 2022, whose year-ago baseline falls inside COVID. One sub-project deliberately *keeps* COVID, see below.

**Real, not nominal.** This turned out to be the load-bearing methodological point. Output must be measured in **real** (inflation-adjusted) terms. Most sectors use BEA real value added directly. Finance was the exception that nearly sank the analysis: its output series is nominal, and BEA's own finance deflator is broken (see the finance section), so finance is deflated with the neutral GDP deflator.

**Era split.** Q4 2022 (ChatGPT's release) is the pre/post-AI marker throughout. It is a visible cutoff, not a measured adoption date, and it sits on top of the Fed's 2022-2023 hiking cycle, a confound addressed directly in Phase 4.

## Repository guide

| Script / folder | What it does |
|---|---|
| [`GDPUnemployment.py`](GDPUnemployment.py) | Phase 1: aggregate Okun's law, rolling coefficient, the break |
| [`IndustryAnalysis.py`](IndustryAnalysis.py) | Phase 2: two-sector comparison, tech vs hospitality |
| [`industry_okun_pipeline.py`](industry_okun_pipeline.py) | Phase 3: nine-industry cross-section, Δβ vs AIIE (unemployment) |
| [`okun_phase2_3.py`](okun_phase2_3.py) | Phase 4: six Federal Funds Rate control specifications |
| [`btos_interaction.py`](btos_interaction.py) | Phase 5: validates AIIE against real reported AI adoption |
| [`info_overhang.py`](info_overhang.py) | Phase 6: tests the pandemic-overhiring alternative for tech |
| [`real_productivity_ai_crosssection.py`](real_productivity_ai_crosssection.py) | The correction: the cross-section on real productivity (the flip) |
| [`ai_replaceability_score.py`](ai_replaceability_score.py) | The job-replaceability score that replaces AIIE |
| [`finance/`](finance/README.md) | Finance re-examined: unemployment floor, nominal-to-real correction |
| [`physical-sector-inversion/`](physical-sector-inversion/README.md) | The goods-sector inversion (fiscal, not AI), COVID included |
| [`generate_results_csv.py`](generate_results_csv.py) | Compiles all regression results into one labeled CSV |

Requires `pandas`, `numpy`, `matplotlib`, `scipy`, `openpyxl`.

---

# Part 1: The aggregate break

## Phase 1: Did Okun's law actually break?

> **Verdict: ESTABLISHED**

Take real GDP, potential GDP, the unemployment rate, and the natural rate; convert output and unemployment to gaps; then, instead of one regression across all history, re-estimate the Okun coefficient on a sliding 12-quarter window so its stability over time is visible.

![Rolling Okun coefficient and correlation](rolling_okuns_coefficient.png)

From 2000 to 2019 the coefficient stays firmly negative and the rolling correlation sits near −1.0, the rule working almost mechanically for two decades. **After Q4 2022 the coefficient swings wildly and the correlation inverts to +0.81.** Under the pre-2022 distribution, a value that positive has probability ~0.0000. The sign of the relationship flipped, its magnitude became unstable, and the inversion is far into the tail of history.

Caveats: the post-2022 sample is short (~10-13 clean quarters), rolling windows overlap (which makes the p-value optimistic), and the windows splice across the COVID gap. This documents a break; it does not identify a cause. Every later phase tries to.

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

Run the difference-form test on all nine sectors, pre and post Q4 2022, and regress each sector's change in Okun coefficient (Δβ) against its AIIE exposure score.

| Industry | AIIE | Δβ (unemployment) | Reading |
|---|---:|---:|---|
| Construction | −0.997 | +0.44 | large inversion |
| Manufacturing | −0.484 | +0.44 | large inversion |
| Transportation & Utilities | −0.342 | +0.41 | large inversion |
| Information | 1.268 | +0.31 | inverted |
| Wholesale Trade | 0.264 | +0.23 | inverted |
| Professional & Business | 0.654 | +0.11 | modest |
| Leisure & Hospitality | −0.315 | +0.05 | barely moved |
| Financial Activities | 1.538 | −0.04 | held |
| Education & Health | 0.775 | −0.19 | strengthened |

![Nine-industry AIIE cross-section](industry_aiie_scatter.png)

The regression runs **the wrong way for the AI hypothesis: r = −0.61, p = 0.08.** The biggest breakdowns are in low-exposure physical sectors; the high-exposure sectors (Finance, Professional & Business, Education & Health) held or strengthened. This looked like a clean refutation of the AI story. It was not. The tell is Financial Activities at the bottom of the Δβ column: "held." Holding that up against the fact that finance is one of the most AI-exposed sectors in the economy is what eventually cracked the whole result open (Part 3).

## Phase 4: Was it interest rates?

> **Verdict: Separate mechanism confirmed for the goods sectors**

The Fed's most aggressive hiking cycle in 40 years began right at the AI cutoff, and the sectors that broke most (Construction, Manufacturing, Transportation) are the most rate-sensitive. Adding the Federal Funds Rate as a control across six specifications does **not** make their breakdown disappear.

![Rate-controlled sensitivity](phase2_rate_sensitivity.png)

So the goods-sector breakdown is not a pure rate artifact, but its AI exposure is the lowest in the sample, so AI cannot be the explanation either. The most likely candidate is fiscal spending inflating physical-sector output without proportional hiring. This becomes its own [sub-project](physical-sector-inversion/README.md).

## Phase 5: Is the AI-exposure measure any good?

> **Verdict: VALIDATES the measure**

AIIE is a 2021 theoretical score. The Census BTOS survey now reports real firm-level AI adoption. Ranking the nine sectors by each and comparing gives **Spearman ρ = 0.917, p = 0.001**: the theoretical exposure and the real 2025-26 adoption agree almost perfectly on sector order. So the surprising Phase 3 result is not a mismeasurement of exposure.

![BTOS cross-section](btos_cross_section.png)

## Phase 6: Was tech's break just pandemic overhiring?

> **Verdict: Overhang is real but does NOT explain tech's break**

Tech over-hired in 2020-2021 and has been correcting since. Adding an employment-overhang control to tech's regression across nested models does not absorb its post-2022 inversion: the Okun slope stays positive across all eight rate-and-overhang specifications (range +0.150 to +0.223). Overhang is a real phenomenon that fails to explain the break.

![Overhang regression](info_overhang_regression.png)

---

# Part 3: The correction that reversed the headline

Phase 3 rested entirely on the **unemployment rate**. That is the wrong instrument for the sectors that matter most, and finding out why reversed the project's central conclusion.

## The turn: unemployment cannot see a full-employment sector

Finance was filed under "the law held." But finance real output has grown far faster than its headcount, which is the textbook picture of producing more without hiring more. The reason unemployment missed it: finance unemployment is welded to its ~2% structural floor. When output grows, unemployment there cannot fall any further, so the Okun test reads "no response" and scores it "held." Flat unemployment at full employment hides two opposite worlds, hiring many workers versus hiring almost none while productivity climbs, and unemployment cannot tell them apart. Employment can. The high-AI sectors (Finance, Professional & Business) are exactly the low-unemployment sectors where this blindness bites.

## Finance re-examined, and the correction that nearly went wrong twice

The full story is in [`finance/`](finance/README.md); the short version is a three-stage correction:

1. **Nominal (too big).** The finance output series is nominal. Using it, output looked like it doubled and productivity rose 79%. Mostly inflation.
2. **BEA finance deflator (too small).** Deflating with BEA's own Finance & Insurance deflator collapses real productivity to ~0.3%/yr, "no decoupling." But that deflator is **FISIM-contaminated**: financial output is imputed from interest-rate spreads, so when the Fed raised rates, BEA dumped the nominal surge into the price term. The finance deflator ran ~4.8%/yr versus ~2.9%/yr economy-wide, understating real output in exactly the recent window.
3. **Neutral GDP deflator (honest).** Re-deflated properly, finance real productivity is **~2.6 to 3.0%/yr, double the US average**, and it **accelerated to ~+7%/yr in 2024-2025 with headcount flat-to-falling.** That is a genuine, recent output-to-jobs decoupling, on the AI timeline, and it survives deflation.

## The corrected cross-section: measured on real productivity, AI supports the decoupling

> **Verdict: SUPPORTS AI (reverses Phase 3)**

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
| **Real productivity growth** | **+0.77** | **0.016** | **supports AI** |

The project's central "contradicts AI" finding does not survive being measured on the variable AI actually targets.

## A better predictor than AIIE: the job-replaceability score

> **Verdict: SUPPORTS AI, more cleanly**

AIIE measures whether AI can *touch* a job. What determines whether Okun's law breaks is whether AI *replaces* the worker (automation) or *assists* them (augmentation). Education and Finance can have similar exposure but opposite substitution: finance tasks are largely substitutable, teaching needs a human in the room. So we built a replaceability score:

```
Replaceability = Exposure x (1 - Complementarity)
```

Exposure comes from Eloundou et al.'s GPT-exposure scores; complementarity from five O\*NET Work Context variables that shield a job (physical presence, face-to-face contact, dealing with the public, responsibility for others' safety, consequence of error); the two are combined per occupation and aggregated to industry with the BLS OEWS employment matrix.

![Job-replaceability score and its fit to real productivity](ai_replaceability_score.png)

It does what it should: **Education & Health drops from 3rd on AIIE to 5th on replaceability**, below Finance, because teaching is complementary rather than substitutable. And it predicts the real decoupling **better than AIIE: r = +0.90, p = 0.001** versus +0.77. The purpose-built substitution measure is the strongest predictor in the project of where output decoupled from labor.

---

# Part 4: The separate physical-sector story

The goods sectors (Construction, Manufacturing, Transportation, Wholesale) are their own story, and it is not AI. The [`physical-sector-inversion/`](physical-sector-inversion/README.md) sub-project examines them with COVID kept in the data, which the root analysis excludes. The findings: all four **held Okun's law hardest during COVID** (output and jobs collapsed together, rolling r near −0.9), then **inverted only in 2024-2025** (peak correlations +0.6 to +0.8, probabilities 0.007 to 0.019 under their own history). They move together tightly, so this is one common factor, not four. Because they are low-AI, physical, and their inversion is recent and rate-surviving, the leading candidate is federal fiscal spending (IIJA, CHIPS, IRA) inflating output without proportional hiring, a hypothesis still to be tested directly.

---

# Where the whole thing stands

The project split one question into pieces with different answers.

### The aggregate break → **ESTABLISHED**
The output-unemployment correlation inverted from about −1.0 to +0.81 after Q4 2022, with near-zero historical probability. Stands on its own.

### AI is driving a real output-to-jobs decoupling in the high-replaceability sectors → **SUPPORTED, once measured correctly**
On unemployment the dose-response test contradicts AI, but that is an artifact of the unemployment floor in the high-AI service sectors. On real productivity, AI exposure predicts the decoupling (r = +0.77, p = 0.016), and a job-replaceability score predicts it better (r = +0.90, p = 0.001). Information and Finance are the clearest cases, and finance's decoupling accelerated to ~7%/yr real in 2024-2025 with flat hiring.

### The goods-sector inversions → **SEPARATE MECHANISM (likely fiscal)**
Construction, Manufacturing, Transportation, and Wholesale inverted in 2024-2025, survive rate controls, and have the lowest AI exposure. Most likely IIJA/CHIPS/IRA, not AI.

### What this is not
Correlation, at n = 9. The productivity window spans 2013-2025, so it partly reflects long-run automation rather than generative AI specifically. AIIE and the replaceability score are both built from task automatability, so "automatable sectors show labor-saving productivity" carries some circularity. And finance's magnitude depends on a deflator judgment. The defensible claim is precise: the original "contradicts AI" headline does not survive correct measurement, and the corrected evidence leans toward AI in the sectors substitution theory says it should.

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

The finance re-examination first reported nominal output ("doubled, +79% productivity"), which is mostly inflation. This produced a dramatically overstated decoupling that was later corrected to real terms.

</details>

<details>
<summary>Error 6: over-trusting the FISIM-broken finance deflator</summary>

The first correction of Error 5 deflated finance with BEA's own finance deflator and concluded "no decoupling" (0.3%/yr). That deflator is FISIM-contaminated and understates real finance output; the neutral GDP deflator gives the honest ~2.6-3.0%/yr. The lesson: swinging from a nominal overstatement to trusting a known-broken deflator is its own error.

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

BTOS: Census Business Trends and Outlook Survey, real firm-level AI adoption. FFR: Federal Funds Rate. Rolling window: re-fitting a regression on each trailing N quarters (here 12). Overhang: tech employment's deviation from its 2010-2019 trend. VIF: variance inflation factor, a collinearity diagnostic. Bonferroni: a multiple-comparisons correction. Spearman ρ: rank correlation. YoY: year-over-year (4-quarter) differencing, used to cancel seasonality.

</details>

## Reproducing this

1. Download the FRED series referenced in each script's header into `FRED-Data/` at the repo root (gitignored), plus the O\*NET Work Context file, Eloundou GPT-exposure scores, and the OEWS national sector file for the replaceability score.
2. `pip install pandas numpy matplotlib scipy openpyxl`
3. Run the aggregate and phase scripts, then `real_productivity_ai_crosssection.py` and `ai_replaceability_score.py` for the correction, and the `finance/` and `physical-sector-inversion/` folders for the two sub-projects.

All numbers here are verified against the committed result CSVs and regenerated from the current data.
