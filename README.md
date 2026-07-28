# Okun's Law in the AI Era

**Is the historical link between economic output and unemployment weakening because of AI, and if so, where?**

For 60 years there has been a reliable rule in economics: when the economy grows faster than usual, more people get hired and unemployment falls. Every 1 extra point of growth has historically pulled unemployment down by about half a point. If AI now lets firms produce more without hiring proportionally more workers, that rule should start to fail, and every policymaker who leans on it (the Federal Reserve, the CBO, the White House) would have to rebuild their playbook.

This project set out to test that, reached a conclusion that seemed to *contradict* the AI story, and then discovered the conclusion was an artifact of measuring the wrong labor variable. Corrected, the evidence leans the other way, though not far enough to pin the effect on generative AI specifically. The whole arc, including the wrong turn, the correction, and a later test that failed to confirm the timing, is documented below, because how the answer moved matters as much as the answer.

## The bottom line

1. **A real, statistically extreme break in the growth-to-jobs relationship appears after Q4 2022 in the aggregate U.S. economy.** The rolling output-unemployment correlation, near −1.0 for two decades, inverts to +0.81, something the historical distribution essentially never produces.
2. **Whether that break looks like AI depends entirely on how you measure labor.** Measured on unemployment, AI exposure predicts *less* breakdown (the "contradicts AI" result). But unemployment is saturated for the high-AI service sectors, which sit at their unemployment floor and cannot register a decoupling. Measured on **real productivity** (real output per worker, the variable AI actually targets), AI exposure significantly *predicts* the output-to-jobs decoupling (r = +0.77, p = 0.016). A purpose-built job-replaceability score predicts it even better (r = +0.90, p = 0.001). **But this is a claim about levels, not timing:** a direct test of whether replaceable sectors *accelerated* after AI arrived comes back insignificant, so the result cannot be pinned to generative AI specifically.
3. **There is a second, separate story in the physical economy.** The biggest unemployment-side inversions landed in Construction, Manufacturing, Transportation, and Wholesale, the low-AI goods sectors, and arrived in 2024-2025. Those most likely reflect the 2021-2022 fiscal spending wave (IIJA, CHIPS Act, IRA), not AI.

So the honest headline is: the aggregate break is real; the AI-driven part of it lives in the high-replaceability sectors (Information and Finance most clearly) and is visible in productivity, not unemployment; and a fiscal-driven part lives in the goods sectors.

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
| [`finance/`](finance/README.md) | Finance deep dive (all content also summarized in Part 3 below) |
| [`physical-sector-inversion/`](physical-sector-inversion/README.md) | Goods-sector deep dive (all content also summarized in Part 4 below) |
| [`generate_results_csv.py`](generate_results_csv.py) | Compiles all regression results into `results_comprehensive.csv` (12 labeled sections) |

Requires `pandas`, `numpy`, `matplotlib`, `scipy`, `openpyxl`.

---

# Part 1: The aggregate break

## Phase 1: Did Okun's law actually break?

> **Verdict: ESTABLISHED**

Take real GDP, potential GDP, the unemployment rate, and the natural rate; convert output and unemployment to gaps; then, instead of one regression across all history, re-estimate the Okun coefficient on a sliding 12-quarter window so its stability over time is visible.

![Rolling Okun coefficient and correlation](rolling_okuns_coefficient.png)

From 2000 to 2019 the coefficient stays firmly negative and the rolling correlation sits near −1.0, the rule working almost mechanically for two decades. **After Q4 2022 the coefficient swings wildly and the correlation inverts to +0.81.** Under the pre-2022 distribution, a value that positive has probability ~0.0000. The sign of the relationship flipped, its magnitude became unstable, and the inversion is far into the tail of history. The same inversion appears in the difference form of the aggregate data (peak r ≈ +0.55), so it is not an artifact of the gap specification.

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

> **Verdict: Separate mechanism confirmed for the goods sectors**

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

Reading it: the breakdown survives every way of measuring rates in seven of nine sectors, and is tightest exactly where it matters (Construction, Manufacturing, Information). The two sectors that cross zero are the two that "held" anyway. Transportation and Wholesale stay positive but swing widely across specs, so their magnitudes deserve less confidence. Since the goods-sector breakdown is not a rate artifact and their AI exposure is the lowest in the sample, a third mechanism is needed; the leading candidate is fiscal spending (Part 4).

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
| BEA finance deflator (FISIM-contaminated) | 1.5%/yr | 0.3%/yr |
| **GDP deflator (neutral)** | **3.8%/yr** | **2.4-2.8%/yr** |

![Real finance output under two deflators vs employment](finance/finance_real_bracket.png)

Under the neutral deflator, finance real productivity runs roughly **double the ~1.5%/yr US average**. A NAICS fix (using Finance & Insurance employment, `CES5552000001`, instead of Financial Activities employment that includes Real Estate) barely moved anything, so the deflator was the whole story.

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
| Employment elasticity change (Δγ) | +0.28 | 0.47 | no relationship |
| **Real productivity growth** | **+0.77** | **0.016** | **supports AI** |

The middle row is included for completeness: the change in each sector's output-elasticity of employment shows no cross-sectional relationship with exposure either way, so the reversal comes specifically from the productivity lens, where the level *and* trend of output per worker are visible rather than only short-run co-movement. The project's central "contradicts AI" finding does not survive being measured on the variable AI actually targets.

## A better predictor than AIIE: the job-replaceability score

> **Verdict: SUPPORTS AI, more cleanly**

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

---

# Part 4: The separate physical-sector story

> **Verdict: SEPARATE MECHANISM (likely fiscal), COVID ruled out, AI ruled out**

The goods sectors are their own story, and it is not AI. This part deliberately **keeps COVID in the data**, unlike the root analysis, because seeing the pandemic is the point (full detail in [`physical-sector-inversion/`](physical-sector-inversion/README.md), reproduce with `rolling_okun_inversion.py` and `comovement.py`).

![Rolling Okun coefficient and correlation for the three goods sectors, COVID included](physical-sector-inversion/rolling_okun_inversion.png)

| Sector | AIIE | Rolling r through COVID | Inversion onset | Peak r | p(r ≥ peak) | Δβ |
|---|---:|---|---|---:|---:|---:|
| Construction | −1.00 | −0.68 to −0.91 | 2024 Q2 | +0.82 | 0.019 | +0.45 |
| Manufacturing | −0.48 | −0.87 to −0.92 | 2024 Q3 | +0.68 | 0.007 | +0.49 |
| Transportation & Utilities | −0.34 | −0.91 to −0.97 | 2024 Q4 | +0.60 | 0.007 | +0.51 |

Three findings:

**During COVID the law held harder than ever.** Output and jobs collapsed together, then recovered together, driving the rolling correlation to its most negative values in the sample (−0.68 to −0.97). Whatever inverted these sectors, it was not the pandemic.

**The inversion is a 2024-2025 event.** Construction first (2024 Q2), then Manufacturing (2024 Q3), then Transportation (2024 Q4), reaching correlations of +0.60 to +0.82, values with probability 0.007 to 0.019 under each sector's own pre-2022 history. That timing postdates COVID by years and generative AI by roughly two years.

**They move as one cluster, and Wholesale joins it.** Manufacturing and Transportation's rolling coefficients are nearly the same series (correlation 0.92), Construction a looser third (0.73-0.78), and their raw YoY unemployment changes correlate 0.80-0.89 even with COVID removed. Scanning all nine industries for the same signature (co-moves with the cluster and inverted recently) adds exactly one member: **Wholesale Trade** (cluster correlation 0.66, 2025 rolling r +0.44). The four are the physical goods economy: build it, make it, move it, distribute it. The service sectors all stay negative through 2025, and Information's marginal inversion (+0.12) belongs to the AI story in Part 3.

![Rolling-beta correlation heatmap and the four goods sectors overlaid](physical-sector-inversion/comovement.png)

That the inverters are exactly the goods producers and the holders are exactly the services is the strongest hint about cause: something specific to physical production, not a whole-economy shift. Two candidates fit the 2023-2025 timing, and neither has been tested directly yet: **federal fiscal spending** (IIJA 2021, CHIPS 2022, IRA 2022 money reaching construction sites and factories as output without proportional hiring; testable with a fiscal-exposure control built from USAspending.gov outlays by NAICS) and **the sustained high-rate environment** (rate-sensitive sectors producing on already-financed backlogs while new hiring stalls). Honest limits: each inversion rests on four to six post-onset quarters, overlapping windows make the probabilities optimistic, and co-movement alone is not unique to these sectors (all unemployment co-moves somewhat); the distinctive feature is the shared hold-then-invert shape on the same clock.

---

# Where the whole thing stands

The project split one question into pieces with different answers.

### The aggregate break → **ESTABLISHED**
The output-unemployment correlation inverted from about −1.0 to +0.81 after Q4 2022 (+0.55 in the difference form), with near-zero historical probability. Stands on its own.

### AI is driving a real output-to-jobs decoupling in the high-replaceability sectors → **SUPPORTED, once measured correctly**
On unemployment the dose-response test contradicts AI, but that is an artifact of the unemployment floor in the high-AI service sectors. On real productivity, AI exposure predicts the decoupling (r = +0.77, p = 0.016), and the job-replaceability score predicts it better (r = +0.90, p = 0.001). Information and Finance are the clearest cases: both accelerate sharply in 2024-2025, tech by cutting jobs while output holds, finance by growing real output ~+5.6%/yr with hiring at +0.2%/yr.

**Important limit, established by direct test.** This is a levels claim. When the same nine sectors are tested on whether replaceable industries *accelerated* more after AI arrived (2024-2025 versus their own 2013-2019 baseline), the relationship is not significant (r = +0.45, p = 0.22), because three of the four least-replaceable sectors accelerated just as much. So the evidence supports "sectors with replaceable work sustain higher productivity growth" but not "AI caused a break in 2022."

### The goods-sector inversions → **SEPARATE MECHANISM (likely fiscal)**
Construction, Manufacturing, Transportation, and Wholesale inverted together in 2024-2025, survive all rate specifications, and have the lowest AI exposure and replaceability in the sample. Most likely IIJA/CHIPS/IRA, still untested directly.

### Tech's break survived everything thrown at it → **BEST-STRESS-TESTED SINGLE RESULT**
Information's post-2022 slope stays inside +0.150 to +0.223 across eight specifications (baseline, five rate controls, two overhang controls), and its real productivity (+7.2%/yr, with genuine falling deflators, no FISIM issue) is the highest in the sample while its 2024-2025 employment is shrinking.

### What this is not
Correlation, at n = 9. The long-run-automation objection is not a hypothetical: it was tested directly (see the recency test) and **survived**, since exposure does not significantly predict the post-2022 acceleration in productivity growth. AIIE and the replaceability score are both built from task automatability, so "automatable sectors show labor-saving productivity" carries some circularity. Finance's magnitude depends on a deflator judgment. The defensible claim is precise and narrow: the original "contradicts AI" headline does not survive correct measurement, and sectors whose jobs are more replaceable by AI sustain materially higher real productivity growth, including in 2024-2025. What is *not* established is that generative AI caused a discontinuity at its arrival.

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

The first correction of Error 5 deflated finance with BEA's own finance deflator and concluded "no decoupling" (0.3%/yr). That deflator is FISIM-contaminated and understates real finance output; the neutral GDP deflator gives the honest ~2.4-2.8%/yr. Swinging from a nominal overstatement to trusting a known-broken deflator is its own error.

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
