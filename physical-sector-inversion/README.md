# Physical-Sector Okun Inversion

**A separate analysis from the [AI-exposure study](../README.md) in the repository root.**

This sub-project does not use AI-exposure scores or an "AI cutoff." It asks one narrow, self-contained question about three low-AI, goods-producing and rate-sensitive sectors:

**Construction, Manufacturing, and Transportation & Utilities**

> When did each sector's Okun relationship actually invert, and how unusual is that inversion when the pandemic is left in the data?

The one deliberate difference from the root study: **COVID is included here, not excluded.** Leaving the pandemic in is the entire point. It reveals that COVID was the most Okun-consistent episode in the whole sample, and that the real inversions are recent, arriving in 2024 and 2025.

> **Where this ended up.** The sub-project began by treating the goods-sector inversion as a puzzle needing a goods-sector cause, and tested interest rates and federal fiscal spending against it. Both failed. Decomposing the inversion itself ([what actually inverted](#what-actually-inverted-going-deeper)) shows why: it is a small sign flip sitting on top of an **economy-wide hiring slowdown** that hit 8 of 9 sectors in 2024-2025 and that AI exposure does not predict. Read the sections in order; the conclusion reverses the framing the early sections set up.

## What Okun's Law is, in one line

When an economy (or a sector) produces more, it usually hires more, so unemployment falls. Measured as a slope: when output growth goes up, the change in unemployment should go down. A negative slope means the rule holds. A positive slope means it has inverted, meaning output grew but unemployment rose anyway.

## Method

- **Difference form:** regress the 4-quarter (year-over-year) change in the sector's unemployment rate on the year-over-year percent change in its real output. YoY differencing cancels the seasonality in the not-seasonally-adjusted sector unemployment series.
- **Rolling window:** re-estimate the slope (beta) and its correlation (r) on every trailing 12-quarter window, so the relationship's stability over time is visible.
- **COVID kept:** no quarters are dropped. The 2020-2021 window is shaded on the chart for context only.
- **Probability test:** for each sector, fit a normal distribution to its own pre-2022 rolling correlations (a baseline that itself includes the deep COVID negatives), then ask how likely the recent peak correlation would be under that historical distribution. This mirrors the aggregate test in the root study. **These normal-approximation p-values were later shown to be too small**; see the correction below.

## The result

![Rolling Okun coefficient and correlation for the three sectors](rolling_okun_inversion.png)

| Sector | AIIE | Held through COVID (rolling r) | Inversion onset | Peak r | p (normal) | **p (bootstrap)** | Δβ |
|---|---:|---|---|---:|---:|---:|---:|
| Construction | −1.00 | −0.68 to −0.91 | 2024 Q2 | +0.82 | 0.018 | **0.036** | +0.45 |
| Manufacturing | −0.48 | −0.87 to −0.92 | 2024 Q3 | +0.68 | 0.006 | **0.031-0.046** | +0.49 |
| Transportation & Utilities | −0.34 | −0.91 to −0.97 | 2024 Q4 | +0.60 | 0.007 | **0.034-0.058** | +0.51 |

> **Correction: these inversions are marginal, not clearly significant.** The p-values in the "normal" column assume the pre-2022 rolling correlations are normally distributed and independent. They are neither: correlations are bounded and skewed, and consecutive 12-quarter windows share 11 quarters of data. A distribution-free circular block bootstrap (root-level `permutation_test.py`, null = the pre-2022 regime continued) raises all three to roughly **0.03 to 0.058**. A Bonferroni correction across the three sectors would require p < 0.017, which none of them clear. The finding's real strength is that all four goods sectors invert together on the same clock, not any single sector's p-value. By contrast the aggregate break in the root study survives the same bootstrap comfortably (p ≈ 0.0005).

Read each panel left to right. All three lines sit negative for most of history, plunge to their most negative values *during* COVID (the pink band), and only climb above zero in 2024. The green line marks where each sector's correlation turns positive and stays positive.

## What this shows

**During COVID, the law held harder than ever.** In 2020 and 2021 output collapsed and jobs vanished together, then both recovered together. That is textbook Okun behavior, and it drove the rolling correlation to between −0.68 and −0.97 across the three sectors. Whatever inverted these sectors, it was not the pandemic.

**The inversion is a 2024-2025 event.** Construction turns first (2024 Q2), then Manufacturing (2024 Q3), then Transportation (2024 Q4). By 2025 all three reach correlations between +0.60 and +0.82, meaning output kept climbing while unemployment climbed with it. Under each sector's own pre-2022 history, the bootstrap puts a positive correlation that large at roughly 0.03 to 0.058, marginal rather than decisive.

**The timing rules things out.** Because the inversion arrives in 2024, it is far too late to be a direct COVID effect, and it postdates the late-2022 arrival of generative AI by roughly two years. It lines up instead with two forces that peaked in 2023-2025: federal infrastructure and industrial spending actually flowing into projects, and interest rates held high for an extended stretch.

## Do they move together, and does anyone else?

The three charts above look almost interchangeable, which raises the question of whether these are really three separate findings or one common factor showing up three times. They co-move strongly. Correlating the rolling Okun coefficient across industries, Manufacturing and Transportation are nearly the same series (0.92), with Construction a looser third (0.73 to 0.78). At the raw-data level their year-over-year unemployment changes correlate 0.80 to 0.89 even with COVID removed, so this is a shared labor-market driver, not a coincidence of chart smoothing.

One caveat keeps this honest: every sector's unemployment moves together to some degree because of the shared business cycle, so co-movement by itself is not unique to these three. The distinctive feature is the specific shape, holding for years and then inverting in 2024-2025.

Scanning all nine industries on both tests at once (does it co-move with the cluster, and did it invert recently and stay inverted) turns up one clear extra member.

![Rolling-beta correlation heatmap and the four goods sectors overlaid](comovement.png)

**Wholesale Trade repeats the pattern.** It correlates with the cluster (rolling-beta 0.66) and its rolling correlation reaches +0.44 in 2025, the same late inversion as the other three. That extends the group to four, and the four have an obvious common identity: they are the physical goods economy. Construction builds it, Manufacturing makes it, Transportation moves it, and Wholesale distributes it.

The service sectors do not repeat it. Financial Activities, Professional & Business, Education & Health, and Leisure & Hospitality all stay negative through 2025 (their Okun relationship held). Information's coefficient shape correlates with the cluster, but its recent inversion is marginal (+0.12) and it sits with the high-AI service sectors, so it belongs to the [AI story in the root analysis](../README.md), not this goods cluster.

That the inverting sectors are exactly the goods-producing ones, and the holding sectors are exactly the service ones, is the strongest hint so far about cause. It points at something specific to physical production and distribution rather than a whole-economy shift. **That reading turns out to be only half right**: the *unemployment-measured inversion* is goods-specific, but the underlying labor-market shift behind it is not. See [what actually inverted](#what-actually-inverted-going-deeper) below.

## What this does not show

- **The sample is very short.** Each inversion rests on only four to six quarters of post-onset data. The confidence around every number here is wide.
- **Overlapping windows.** Consecutive 12-quarter windows share most of their data. This is no longer just a caveat: the block bootstrap in `permutation_test.py` quantified it, and it roughly quadruples these sectors' p-values (0.006-0.018 becomes 0.03-0.058).
- **No cause is established.** This analysis dates the inversion and measures how unusual it is. It does not yet test any explanation for it.

## Causes to explore next

The natural next step, and the reason these three sectors were pulled out together, is that all three are physical, capital-intensive, and low on AI exposure, which points away from the technology story and toward two candidates:

1. **Federal fiscal spending.** The Infrastructure Investment and Jobs Act (2021), CHIPS Act (2022), and Inflation Reduction Act (2022) directed large sums into exactly these sectors. Money committed in 2021-2022 shows up as actual construction and manufacturing output in 2023-2025, which can raise output without proportional hiring when projects are capital-heavy or labor-constrained. A fiscal-exposure control per sector (federal outlays by NAICS from USAspending.gov) would test this directly.
2. **The sustained high-rate environment.** Rate-sensitive sectors can keep producing on already-financed backlogs while new hiring stalls, which would loosen the output-to-jobs link with a lag.

These are hypotheses to test, not findings. This document exists to establish the pattern cleanly first.

## The fiscal hypothesis, tested

> **Verdict: NOT SUPPORTED, but the test is structurally weak.**

`fiscal_control.py` pulls federal obligations by NAICS from the USAspending API (quarterly, back to 2008) and adds fiscal intensity, obligations as a share of the sector's value added, as a third control alongside the rate control. If fiscal spending inflated goods-sector output without hiring, adding it should shrink those sectors' Δβ toward zero and leave the service sectors alone.

![Testing the fiscal hypothesis](fiscal_control.png)

**The acts themselves cannot be isolated.** IIJA carries fund code 1 and CHIPS code 8, so both are directly taggable, but the tagged obligations reach only about 0.08% of construction value added and 0.00% elsewhere. Nearly all IIJA money goes to states as formula grants and is never booked against a construction NAICS in federal contract data. The IRA has no fund code at all and works mainly through tax credits, which never appear in obligation data. So the specific 2021-2022 acts are effectively invisible here.

**Total federal obligations are meaningful but do not explain the breakdown.** They are economically large (4-6% of construction value added, 9-11% of manufacturing) and did rise roughly 2 points in the goods sectors after 2021. But adding them as a control moves the goods sectors' mean Δβ only from +0.218 to +0.189, and the fiscal coefficient is statistically significant in just 1 of 8 sectors (Transportation).

**A lagged specification appears to work, then fails falsification.** Lagging fiscal intensity four quarters, on the theory that obligations become activity about a year later, appears to collapse the goods breakdown (+0.218 to +0.022). That is exactly what the fiscal story predicts, so it deserved a check. On the common lagged sample the control shrinks the **non-goods** sectors more than the goods sectors (−0.068 against −0.042), and the single largest move is Information, which has no plausible fiscal story. The apparent collapse is a sample artifact of lagging, not a fiscal effect.

**What this leaves.** The fiscal explanation is not refuted, because federal contract data structurally cannot see the money that matters, and obligations are not the same thing as activity. But it is no longer an untested assumption presented as the leading candidate. The honest position is that the goods-sector inversion has no confirmed explanation: it is not COVID, not interest rates, not AI exposure, and not federal contract spending as far as this test can measure it.

## What actually inverted (going deeper)

Every explanation tried so far has failed, which usually means the question is wrong. `what_actually_inverted.py` stops hunting for a cause and instead asks what the inversion physically consists of. Three tests, each narrowing the answer, and the third one reframes the whole sub-project.

![What actually inverted: three tests](what_actually_inverted.png)

### Test 1: the flip is in the correlation, not the magnitude

An inverted correlation is not the same as a large economic effect. Putting each sector's correlation next to its actual Okun slope beta, the pp change in unemployment per 1% of output growth:

| Sector | r pre | r post | β pre | β post | sd(ΔU) pre | sd(ΔU) post |
|---|---:|---:|---:|---:|---:|---:|
| Construction | −0.10 | +0.58 | −0.064 | +0.061 | 1.00 | 0.22 |
| Manufacturing | −0.09 | −0.07 | −0.021 | −0.016 | 0.55 | 0.32 |
| Transportation & Utilities | −0.27 | +0.29 | −0.109 | +0.187 | 0.72 | 0.73 |
| Wholesale | −0.52 | +0.48 | −0.092 | +0.090 | 0.40 | 0.37 |

The correlations swing hard, but every slope stays inside ±0.19pp, and unemployment variation itself shrank (Construction's standard deviation fell from 1.00 to 0.22). A correlation is a normalized measure, so when the thing being measured barely moves, the sign can flip decisively on economically trivial movements. The inversion is real, and it is small. The headline Δβ figures of +0.45 to +0.51 in the table above come from the full pre-period including the 2008 crash; measured against the calmer 2013-2019 baseline the change is a fraction of that.

### Test 2: hiring collapsed, output did not

Unemployment can rise either because employment falls or because the labor force grows faster than hiring. Bringing in sector headcount settles it:

| Sector | Real output 2013-19 | Real output 2024-25 | Employment 2013-19 | Employment 2024-25 |
|---|---:|---:|---:|---:|
| Construction | +4.0%/yr | +3.3%/yr | +4.1%/yr | **+1.6%/yr** |
| Manufacturing | +1.8%/yr | +2.3%/yr | +1.0%/yr | **−0.9%/yr** |
| Transportation & Utilities | +3.2%/yr | +2.3%/yr | +3.3%/yr | **+0.5%/yr** |
| Wholesale | +1.8%/yr | +0.6%/yr | +0.7%/yr | **−0.4%/yr** |

Output growth largely held up, and Manufacturing's even accelerated. Employment growth collapsed in all four, turning negative in two. So the inversion is an employment-side event, not an output collapse. These sectors kept producing and stopped hiring.

### Test 3: that shape is not AI-specific, and it is everywhere

"Output holds, hiring stops" is exactly the signature attributed to AI in the Information sector. So the obvious question is whether it is actually distinctive. Measuring the hiring slowdown across all nine sectors:

| Sector | AIIE | Employment 2013-19 | Employment 2024-25 | Slowdown |
|---|---:|---:|---:|---:|
| Construction | −1.00 | +4.13 | +1.58 | −2.55 |
| Manufacturing | −0.48 | +1.02 | −0.94 | −1.96 |
| Transportation & Utilities | −0.34 | +3.29 | +0.51 | −2.77 |
| Leisure & Hospitality | −0.32 | +2.70 | +0.90 | −1.80 |
| Wholesale | +0.26 | +0.73 | −0.41 | −1.14 |
| Professional & Business | +0.65 | +2.44 | −0.79 | −3.23 |
| Education & Health | +0.78 | +2.19 | +3.78 | +1.59 |
| Information | +1.27 | +0.98 | −2.46 | −3.44 |
| Financial Activities | +1.54 | +1.42 | +0.16 | −1.26 |

**Eight of nine sectors slowed hiring, by an average of 1.8 percentage points.** The only exception is Education & Health, which is driven by demographics and public funding rather than the business cycle. And AI exposure does not predict which sectors slowed: **r = +0.18, p = 0.64.** The same holds for productivity acceleration (r = +0.26, p = 0.50). The lowest-AI sectors accelerated productivity by an average of +1.5pp against +2.5pp for the highest-AI ones, a difference far too small and too noisy to carry an AI story.

### What this reframes

The goods-sector inversion and the tech "AI signature" are most likely **the same event seen in different sectors**: a broad hiring slowdown across the US economy in 2024-2025, on top of which the unemployment-based Okun measure flipped sign in the handful of sectors whose unemployment variation had collapsed enough for a small movement to dominate.

That resolves why nothing explained the goods inversion. It is not a goods-sector phenomenon needing a goods-sector cause. It is an economy-wide labor-market shift that happens to be *visible* in the goods sectors, because their unemployment series are the ones where a small absolute change produced a correlation flip. The service sectors experienced comparable hiring slowdowns without their Okun correlations inverting, since their unemployment sits pinned at a structural floor, which is the same blindness documented in the [finance analysis](../finance/README.md).

It also cuts against the AI reading in the root study from a second direction. Construction and Transportation have the lowest AI exposure in the sample and slowed hiring as much as Information did. Whatever froze hiring in 2024-2025 reached the sectors AI cannot plausibly touch.

**What would distinguish the remaining candidates.** A broad hiring freeze across sectors with nothing in common except timing points at an economy-wide force: the cumulative effect of sustained high rates on hiring plans, a post-pandemic normalization after the 2021-2022 over-hiring surge, or labor supply changes. Separating those needs JOLTS hires and quits by sector, and a labor-force-flows decomposition, neither of which this sub-project has run.

## Reproducing this

From this directory:

```
python3 rolling_okun_inversion.py   # the three-sector rolling coefficients + probabilities
python3 comovement.py               # co-movement heatmap + the four-sector overlay
python3 fiscal_control.py           # tests the fiscal hypothesis (fetches USAspending on first run)
python3 what_actually_inverted.py   # decomposes the inversion; the economy-wide hiring finding
```

All read the FRED CSVs from `../FRED-Data/` and write their charts plus the console tables above. Requires `pandas`, `numpy`, `matplotlib`, and `scipy`.
