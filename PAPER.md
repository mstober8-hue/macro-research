# Reallocation, Not Displacement

**Entry-level employment and AI exposure in nationally representative data**

Draft. Section 5 is written; the rest is the agreed skeleton.

| # | Section | Status |
|---|---|---|
| 1 | Introduction | outline |
| 2 | Data and measures | outline |
| 3 | Replication: the young-share result | outline |
| 4 | Strengthening: controls, placebo, break date | outline |
| **5** | **Where the gap comes from** | **drafted** |
| 6 | Measure divergence: task-based against revealed usage | outline |
| 7 | Limits | outline |

Reproduce Section 5 with `python3 entry_level_decomposition.py` and
`python3 adp_cps_reconciliation.py`.

---

# 5. Where the gap comes from

## 5.1 A share moves when either side moves

Section 3 established that the young-worker share of employment falls in
AI-exposed occupations after 2022, and Section 4 showed that the estimate
survives education and wage controls, a clean pre-AI placebo, and both age
bands. Brynjolfsson, Chandar and Chen (2026) report a closely related fact in
ADP payroll microdata: between November 2022 and June 2026, employment of
22 to 25 year olds fell roughly 11 percent in the two most AI-exposed
occupational quintiles while rising roughly 10 percent in the three least
exposed. They read the divergence as displacement, with AI-exposed occupations
shedding their entry tier.

A gap of that shape admits two accounts, and they carry different meanings.
Under displacement, exposed occupations lose young workers in levels. Under
reallocation, exposed occupations hold roughly flat while unexposed occupations
absorb a growing share of the young cohort. Both produce a widening gap, and the
regression in Section 3 cannot separate them, because the dependent variable is
a ratio and a ratio moves when either side moves. Distinguishing them requires
looking at the levels directly. That is what this section does.

The distinction is not semantic. Displacement implies that AI adoption destroys
entry-level positions in the occupations it touches, which is an argument for
policy aimed at the exposed occupations themselves. Reallocation implies that
those positions persist while the young cohort's growth accrues elsewhere, which
is an argument about labor market entry and occupational choice, with a
different set of instruments and a different urgency.

## 5.2 Design

Occupations are sorted into quintiles on the Eloundou et al. GPT-4 beta rating,
the primary exposure measure in Brynjolfsson et al., weighted by 2022 employment
so that the two groups are comparable in size. The comparison window runs 2022 to
2026 and sits entirely inside the CPS microdata panel, so the BLS splice used
elsewhere in this paper is not needed here and is not used. Standard errors come
from a nonparametric bootstrap resampling occupations with replacement, 2,000
replications. Occupations are the sampling unit and the level at which exposure
varies, so they are the level at which resampling has to happen. Both age bands
are reported: 22 to 25 to match Brynjolfsson et al., and 20 to 24 as this
paper's primary band.

## 5.3 The exposed side does not fall

Table 5.1 gives employment growth by exposure group.

**Table 5.1.** Employment growth by AI-exposure group, 2022 to 2026. Quintiles on
Eloundou GPT-4 beta, employment weighted. Bootstrap over occupations, 2,000 reps.

| Age band | Group | Growth | 95% CI | p vs 0 |
|---|---|---:|---:|---:|
| 22-25 (n = 427) | top 2 exposed quintiles | **+1.9%** | [−4.0, +8.2] | 0.507 |
| | bottom 3 quintiles | **+8.7%** | [+2.3, +15.0] | **0.007** |
| | gap | −6.8pp | [−15.5, +2.2] | 0.141 |
| 20-24 (n = 421) | top 2 exposed quintiles | +2.2% | [−3.8, +8.8] | 0.526 |
| | bottom 3 quintiles | +8.2% | [+1.8, +15.0] | 0.011 |
| | gap | −6.1pp | [−15.1, +3.3] | 0.205 |
| Brynjolfsson et al. (ADP), same window | top 2 / bottom 3 / gap | −11% / +10% / −21pp | | |

Three results follow.

First, the exposed side does not contract. The point estimate is positive in both
age bands, and the 95 percent interval for the 22 to 25 band runs from −4.0 to
+8.2 percent. The −11 percent figure reported in ADP data lies far outside that
interval, and a bootstrap test of the CPS estimate against it rejects at p < 0.001.
The direction of the ADP result is not reproduced in nationally representative
data, and the magnitude is rejected outright.

Second, the significant movement is on the unexposed side. The bottom three
quintiles grew 8.7 percent, with an interval excluding zero at p = 0.007. This is
the one component of the divergence that the data identify with confidence.

Third, the gap itself is not statistically significant in levels. At −6.8
percentage points with an interval of [−15.5, +2.2], the levels comparison cannot
reject the absence of a gap. This is a power result rather than a contradiction,
and Section 5.6 treats it directly.

Decomposing the gap against a zero-growth benchmark makes the arithmetic explicit.
For the 22 to 25 band, none of the −6.8 point gap comes from the exposed side
falling below zero, because it did not fall below zero, and 128 percent of it
comes from the unexposed side rising above zero. The 20 to 24 band gives 136
percent. The gap is an artifact of one side rising.

## 5.4 Underperformance is real, contraction is not

The finding above should not be read as an absence of any exposure-related
pattern. Young employment across all occupations grew 5.8 percent over the same
window for the 22 to 25 band. The exposed group grew 1.9 percent, a shortfall of
3.9 percentage points against the aggregate. The 20 to 24 band gives 5.7 percent
against 2.2 percent, a shortfall of 3.6 points.

This is the honest two-sided statement, and the paper carries it in both
directions. Young employment in AI-exposed occupations grew more slowly than
young employment overall, which is consistent with exposure suppressing entry
into those occupations at the margin. It did not decline, which is what a
displacement account requires. Underperformance relative to a growing aggregate
and contraction in levels are different claims, and only the first survives.

Table 5.2 gives the full path and supports two further points.

**Table 5.2.** Employment index by exposure group, 22 to 25 year olds, 2022 = 100.

| Year | Top 2 quintiles | Bottom 3 quintiles | Gap |
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

The pre-2022 gap oscillates around zero with no visible trend, which is what the
placebo tests in Section 4 report formally and which supports treating 2022 as a
break rather than a continuation.

The 2020 row is a useful scale check. In the pandemic year the gap ran +8.0
points, larger in absolute value than the −6.8 points reached by 2026, and it ran
in the opposite direction because in-person and manual work absorbed the shock
while exposed office work continued remotely. A gap between these groups of the
magnitude observed in 2026 is within the range this pair of series produces in
response to a large sectoral shock. That does not make the post-2022 movement
uninformative, since its sign, timing and monotonicity after 2023 all differ from
2020, and it is worth stating that the effect being measured is not large relative
to the series' own recent history.

## 5.5 Ruling out the two boring explanations

A disagreement of 12.9 percentage points on the exposed side between two datasets
has two mundane candidate explanations before it can be called substantive: the
two studies count different people, and they date from different points. Both were
tested directly.

ADP observes private, nonagricultural, non-self-employed payroll employees. The
CPS as published covers everyone employed. Walking the CPS down to ADP's universe
one restriction at a time moves the exposed-side growth rate from +1.9 percent to
+1.3 percent, a shift of 0.6 points, while retaining 85 percent of the base.
Re-dating from the annual panel to the twelve-month windows ending November 2022
and July 2026 moves it back by 0.6 points. Applied together, ADP's universe over
ADP's window gives +1.9 percent with a 95 percent interval of [−3.8, +8.9]. That
estimate is indistinguishable from zero at p = 0.52 and still rejects −11 percent
at p < 0.001. Neither explanation closes any material part of the gap.

Two channels do move the estimate, and neither moves it far alone. Dropping any
single industry from the ADP universe spans −0.8 to +3.5 percent. Retaining only
white-collar-heavy sectors, the most generous available proxy for ADP's client
skew toward larger firms, reaches −2.8 percent. Restricting to full-time workers
reaches −1.3 percent. Stacked adversarially, every choice set to whichever value
most favors the displacement reading at once, the CPS reaches −4.7 percent with an
interval of [−17.8, +8.8]. At that point 33 percent of the sample remains and the
interval rejects nothing in either direction, including zero (p = 0.55) and −11
percent (p = 0.33). The correct reading is that the CPS runs out of power before
it runs into agreement.

What remains unresolved is not something the CPS can adjudicate. ADP's firm-size
skew, its client selection, and the difference between a payroll job title and a
self-reported occupation are all plausible sources of the residual, and none is
observable in a household survey. The finding this paper claims is the negative
one and it is robust to everything testable: in a nationally representative frame,
restricted to ADP's universe and dated to ADP's window, young employment in the
most AI-exposed occupations did not contract.

## 5.6 What each estimand can support

The share regression and the levels decomposition have different power, and the
paper is explicit about which claim rests on which.

The share regression in Section 3 estimates a coefficient of −0.420 on 22 to 25
year olds with occupation and year fixed effects across 451 occupations, and it is
significant at p = 0.0001. It uses variation across every occupation in the panel,
so the effective sample is large.

The levels decomposition estimates a gap of −6.8 points with p = 0.141. It
compares two aggregates, and aggregates of this kind are dominated by a handful of
large occupations, so the bootstrap distribution is correspondingly wide. The loss
of significance reflects the estimand and not a conflict in the underlying data.

Both belong in the paper and they support different sentences. The share result
establishes that young workers are increasingly sorted away from AI-exposed
occupations, and it is the paper's inferential finding. The levels result
establishes where in the distribution that sorting occurs, and it rejects a
specific published magnitude. It does not, on its own, establish a statistically
significant reallocation gap, and this paper does not claim one.

## 5.7 Summary

Reproducing the exposure gap in nationally representative data and then
decomposing it yields a different mechanism than the displacement reading of the
same gap in payroll data. Employment of young workers in the most AI-exposed
occupations grew slightly and insignificantly, underperformed the aggregate by
about 4 percentage points, and did not contract. The divergence between exposure
groups is generated almost entirely by less-exposed occupations absorbing a
growing share of the young cohort. Neither sample universe nor window explains the
discrepancy with the published ADP estimate, and an adversarial specification
reaches only −4.7 percent on a third of the sample. The evidence supports
reallocation of young workers across the exposure distribution, and does not
support the destruction of entry-level positions in exposed occupations.
