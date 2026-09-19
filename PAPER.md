# Underperformance Without Contraction

**Entry-level employment and AI exposure in nationally representative data**

Draft. Section 5 is written; the rest is the agreed skeleton.

| # | Section | Status |
|---|---|---|
| 1 | Introduction | outline |
| 2 | Data and measures | outline |
| **3** | **The young-employment share in AI-exposed occupations** | **drafted** |
| **4** | **Is it exposure, or is exposure a proxy?** | **drafted** |
| **5** | **Where the gap comes from** | **drafted** |
| **6** | **Capability predicts the gap, deployment does not** | **drafted** |
| 7 | Limits | outline |

Reproduce Section 3 with `python3 section3_core.py`, Section 4 with
`python3 section4_controls.py`, Section 6 with `python3 section6_measures.py`,
and Section 5 with
`python3 entry_level_decomposition.py` and `python3 adp_cps_reconciliation.py`.

---

# 3. The young-employment share in AI-exposed occupations

## 3.1 Specification

The estimating equation is a two-way fixed-effects difference-in-differences on an
occupation-by-year panel:

    share_it = a_i + d_t + B * ( z(exposure_i) x post_t ) + e_it

where `share_it` is employment in the age band as a percent of occupation i's total
16 to 64 employment in year t, `a_i` and `d_t` are occupation and year fixed
effects, exposure is z-scored across occupations, and `post_t` is an indicator for
years from 2023. Cells are weighted by occupation employment and standard errors
cluster on occupation, which is the level at which exposure varies and therefore
the level at which residuals are correlated.

B is the change in the young share, in percentage points, associated with a one
standard deviation increase in AI exposure after 2022, holding the occupation's own
level and the common year effect fixed. The sample is 457 occupations and 4,625
occupation-years covering 2016 to 2026, built from 6.0 million IPUMS CPS person
records.

Two exposure measures are used throughout. The raw Eloundou et al. GPT-4 beta
rating is the primary measure in the study this paper replicates. The composite
additionally discounts exposure by an O*NET-derived complementarity index, on the
reasoning that an exposed task performed face to face under high consequence of
error is less substitutable than the rating alone implies. Results are reported
under both, and no claim in this paper depends on the composite.

**A defect corrected in the panel.** The non-overlapping age bands originally used
to reconstruct the denominator were under 20, 20 to 24, 26 to 30, 31 to 34, and 35
plus, which leave a hole at exactly age 25. Every 25 year old was therefore missing
from total employment, understating the denominator by about 2 percent, and the 22
to 25 share was a ratio whose numerator included people its denominator did not.
The panel now carries a singleton band at 25 so the non-overlapping set tiles 16 to
64. Correcting it moved the coefficients by roughly 4 percent and changed no
inference, and it is recorded here because the uncorrected figures appear in
earlier versions of this project.

## 3.2 The core result

**Table 3.1.** Young-employment share on AI exposure, two-way fixed effects,
occupation-clustered standard errors. 457 occupations, 4,625 cells, 2016 to 2026.

| age band | exposure measure | B | SE | p |
|---|---|---:|---:|---:|
| **22-25 (primary)** | **composite** | **−0.4004** | 0.1042 | **0.0001** |
| 22-25 (primary) | raw GPT-4 beta | −0.3790 | 0.1018 | 0.0002 |
| 20-24 (robustness) | composite | −0.4421 | 0.1115 | 0.0001 |
| 20-24 (robustness) | raw GPT-4 beta | −0.4200 | 0.1213 | 0.0005 |

All four specifications give the same answer at the same order of magnitude. A one
standard deviation increase in exposure is associated with a 0.40 percentage point
fall in the 22 to 25 share of an occupation's employment after 2022. Against a mean
22 to 25 share of 8.47 percent, that is a relative decline of about 4.7 percent per
standard deviation. The result does not depend on the complementarity adjustment,
since the raw rating gives −0.3790 on its own.

## 3.3 Timing

A fixed post indicator imposes a single step and reveals nothing about when the
change arrives. Replacing it with a full set of exposure-by-year interactions, with
2022 omitted as the base year, gives the path directly.

**Table 3.2.** Event study, 22 to 25 share, composite exposure. 2022 omitted.

| year | B | SE | 95% CI |
|---|---:|---:|---:|
| 2016 | +0.0240 | 0.1575 | [−0.285, +0.333] |
| 2017 | +0.1250 | 0.1553 | [−0.179, +0.429] |
| 2018 | +0.2440 | 0.1867 | [−0.122, +0.610] |
| 2019 | +0.1602 | 0.1376 | [−0.110, +0.430] |
| 2020 | +0.2560 | 0.1098 | [+0.041, +0.471] |
| 2021 | +0.1195 | 0.1258 | [−0.127, +0.366] |
| 2023 | −0.2776 | 0.1271 | [−0.527, −0.028] |
| 2024 | −0.0684 | 0.1254 | [−0.314, +0.177] |
| 2025 | −0.2721 | 0.1245 | [−0.516, −0.028] |
| 2026 | **−0.4643** | 0.1614 | [−0.781, −0.148] |

One of six pre-2022 coefficients is individually significant, and it is 2020, the
pandemic year, where exposed office occupations retained young workers while
in-person work shed them. The remaining five are indistinguishable from zero. Every
post-2022 coefficient is negative, three of four significantly so, and the series
reaches its most negative value in the most recent year rather than immediately
after the cutoff.

That shape matters for interpretation. A one-off reclassification or a
level shift would jump and then flatten. A diffusion process ramps. The 2024
attenuation to −0.0684 interrupts the monotonicity and is not explained here,
though the point estimate stays negative and the trajectory resumes afterward.

## 3.4 What could be doing the work

Three discretionary choices enter the baseline. Each is varied rather than
asserted.

**Table 3.3.** Sensitivity of the composite-exposure coefficient, p-values in
parentheses.

| | 22-25 | 20-24 |
|---|---:|---:|
| **post from 2022** | −0.3696 (0.0007) | −0.4587 (0.0000) |
| **post from 2023 (baseline)** | −0.4004 (0.0001) | −0.4421 (0.0001) |
| **post from 2024** | −0.3432 (0.0005) | −0.4059 (0.0005) |
| employment weighted (baseline) | −0.4004 (0.0001) | −0.4421 (0.0001) |
| **unweighted** | −0.4325 (0.0124) | **−0.2527 (0.1899)** |
| full sample, 457 occupations | −0.4004 (0.0001) | −0.4421 (0.0001) |
| drop 10 largest occupations | −0.3708 (0.0006) | −0.4756 (0.0001) |
| drop 25 largest occupations | −0.4858 (0.0000) | −0.5789 (0.0000) |

The cutoff year does not carry the result: the coefficient moves within a narrow
band across all three choices and stays significant at better than 1 percent
throughout. Influence does not carry it either, and dropping the 25 largest
occupations strengthens rather than weakens it, which rules out the possibility
that a handful of large occupations are generating the effect.

Weighting does matter, and it matters asymmetrically. The 22 to 25 result survives
unweighted at p = 0.0124. The 20 to 24 result does not, falling to −0.2527 with
p = 0.1899. Employment weighting is defensible here, since the quantity of interest
is what happened to young workers rather than what happened to the average
occupational category, and an unweighted specification gives a 400-person
occupation the same influence as a 2-million-person one. It remains the case that
one of the two bands depends on that choice and the other does not.

## 3.5 Why 22 to 25 is the primary band

This project originally used 20 to 24, and the comparison study uses 22 to 25. The
obvious reason to prefer 22 to 25 is comparability. The better reason is that it is
the more defensible band on this data, and the diagnostics in this section are what
establish that.

Running the event study on 20 to 24 gives four of six pre-2022 coefficients
individually significant at 5 percent, all positive, rising to +0.5148 in 2018. The
20 to 24 share was climbing in exposed occupations for years before generative AI
existed, and the post-2022 fall is measured against that rising path. A
conventional placebo does not catch this, because differencing two halves of the
pre-period removes a smooth trend; the event study catches it because it holds
every year against a single base.

The 22 to 25 band has no such problem, with one pre-period coefficient significant
and that one attributable to the pandemic. It also survives the unweighted
specification that 20 to 24 fails. Both considerations point the same way, so 22 to
25 is primary throughout this paper and 20 to 24 is reported as robustness with the
pre-trend caveat attached wherever it appears.

The 20 to 21 year olds are the likely source. They are disproportionately students
and part-time workers, so their occupational distribution tracks enrollment,
schedule, and the post-2021 in-person recovery more than it tracks AI. Removing
them removes the pre-trend.

## 3.6 Summary

The young-employment share falls in AI-exposed occupations after 2022, within
occupation and relative to less-exposed occupations. The estimate is
−0.40 percentage points per standard deviation of exposure for the 22 to 25 band,
significant at p = 0.0001, robust to the exposure measure, the cutoff year,
employment weighting, and the exclusion of the largest occupations. The event study
shows a flat pre-period and a post-2022 path that reaches its most negative value
in 2026. Section 4 asks whether the estimate is exposure proxying for education or
pay.

---

# 4. Is it exposure, or is exposure a proxy?

Section 3 establishes that the young share falls in AI-exposed occupations. It
does not establish that exposure is what matters. Exposed occupations are also
better paid, require more preparation, and were on different paths before 2022.
This section tests each of those.

The section is also where this paper has the most to gain relative to the study it
replicates. Brynjolfsson et al. concede in their own abstract that their patterns
"attenuate when controlling for education, show some divergent trends predating
generative AI, and are more pronounced in the ADP analysis sample than in national
survey benchmarks." The third concession does not apply here, because this paper
runs on a national survey benchmark by construction. The other two are tested
below. The estimation sample is the 451 occupations and 4,563 cells with both a
Job Zone and an OEWS wage.

## 4.1 The controls are informative

A control that is nearly collinear with the treatment tells you little either way,
so the overlap is worth measuring before interpreting anything.

| pair | correlation |
|---|---:|
| exposure, Job Zone | +0.511 |
| exposure, log median wage | +0.372 |
| Job Zone, log median wage | +0.768 |

Exposure is correlated with both controls, which is why the objection is worth
taking seriously, and it is far from collinear with either. Regressing exposure on
Job Zone and log wage together gives an R-squared of 0.263, so **74 percent of the
variation in exposure is orthogonal to both**. There is real independent variation
for the controlled specification to use.

## 4.2 The estimate strengthens under controls

**Table 4.1.** Young-share coefficient with education and wage controls, each
interacted with post. Two-way fixed effects, occupation-clustered SEs.

| specification | 22-25 (primary) | 20-24 (robustness) |
|---|---:|---:|
| no controls | −0.4034 (0.0001) | −0.4446 (0.0001) |
| + education (Job Zone) x post | −0.4208 (0.0002) | −0.4967 (0.0000) |
| + log median wage x post | −0.4636 (0.0000) | −0.5112 (0.0000) |
| **+ both** | **−0.4424 (0.0001)** | **−0.5095 (0.0000)** |
| | *strengthens 10%* | *strengthens 15%* |

The estimate does not attenuate. It moves away from zero under both controls
individually and under both together, in both age bands. This is the direct
contrast with the published result, which attenuates on the same objection, and it
is the single strongest claim this paper makes relative to the existing literature.

The interpretation is that AI exposure is not a restatement of "high-skill
occupation." If it were, adding a preparation measure and a pay measure would
absorb it. Instead the exposure coefficient gets larger, which is what happens when
the controls strip out variation that was working against the effect: high-wage,
high-preparation occupations were absorbing young workers over this period for
reasons unrelated to AI, and holding that constant sharpens rather than dissolves
the exposure gradient.

## 4.3 Trends that predate generative AI

The second concession is the harder one, and Section 3.3 already showed it has
teeth for the 20 to 24 band. Two tests follow, and they disagree in an informative
way.

**The demanding version fails, and it cannot do otherwise.** Absorbing an
occupation-specific linear trend fitted over the full 2016 to 2026 window leaves
−0.1623 with a standard error of 0.2638 for the 22 to 25 band, p = 0.54.

That result should not be read as a refutation, for a reason visible in the
numbers. The standard error is two and a half times the baseline's, and the
resulting interval, [−0.679, +0.355], contains zero and also contains the
baseline estimate of −0.4004. The specification cannot distinguish the two
hypotheses. That is what happens when a linear trend is fitted through a window
that includes the treatment period and the treatment effect ramps: the trend
absorbs the effect by construction. Section 3.3 showed this effect ramps, reaching
its most negative value in the final year. A diffusion-shaped treatment cannot pass
this test whether or not it is real, so the test is uninformative here rather than
adverse.

**The version a ramping effect can pass.** The standard remedy is to fit each
occupation's trend on the pre-period only and extrapolate it through the post
period, so the treatment window contributes nothing to the trend it is judged
against.

**Table 4.2.** Deviations from occupation-specific trends fitted on 2016 to 2022
and extrapolated forward.

| specification | 22-25 (primary) | 20-24 (robustness) |
|---|---:|---:|
| trend fitted 2016-2022 | **−0.3840 (0.0018)** | −0.2506 (0.0663) |
| trend fitted 2016-2022, excluding 2020-2021 | **−0.3570 (0.0073)** | −0.1966 (0.1681) |

The 22 to 25 estimate survives at close to its baseline magnitude and remains
significant at better than 1 percent, including when the pandemic years are
dropped from the trend fit so that COVID cannot tilt the extrapolation. Young
employment in exposed occupations fell below the path those occupations were
already on, and that is the claim the pre-trend objection is meant to defeat.

The 20 to 24 band does not survive, falling to p = 0.066 and then to p = 0.168
without the pandemic years. This is the third independent diagnostic pointing the
same way, after the event study and the unweighted specification in Section 3, and
it is why 22 to 25 is primary.

## 4.4 Placebo

Running the controlled specification on 2016 to 2019 with a fake post indicator at
2018 should produce nothing, and it does.

| band | exposure | Job Zone | wage |
|---|---:|---:|---:|
| 22-25 | +0.0401 (p = 0.66) | +0.0418 (p = 0.74) | +0.1328 (p = 0.21) |
| 20-24 | +0.0744 (p = 0.45) | +0.0441 (p = 0.72) | +0.1003 (p = 0.36) |

No term is significant, and the exposure coefficients are small and positive,
which is the opposite sign to the post-2022 estimate. The design does not
manufacture a result from a window where there was nothing to find.

## 4.5 Is the break at 2022 or at 2020?

The pandemic reorganized work along a dimension correlated with AI exposure, since
exposed occupations are disproportionately the ones that could be done remotely. If
the young-share movement is really a delayed COVID reallocation, a 2020 step should
carry it. Entering both steps in the same regression settles which does.

| band | exposure x post-2020 | exposure x post-2022 |
|---|---:|---:|
| 22-25 | −0.0187 (p = 0.861) | **−0.3927 (p < 0.001)** |
| 20-24 | −0.1373 (p = 0.185) | **−0.3667 (p < 0.001)** |

The 2022 term takes essentially the whole effect and the 2020 term is
indistinguishable from zero. The timing matches generative AI rather than the
pandemic.

## 4.6 What survives

Exposure is not standing in for education or pay, and the estimate strengthens
when both are held constant. It is not a pre-existing trend, at least for the 22 to
25 band, which survives extrapolated pre-period trends with and without the
pandemic years. It is not a placebo artifact and it is not COVID timing.

One qualification belongs on the record. The most demanding trend specification,
with trends fitted over the full window, is uninformative rather than supportive,
and a reader who believes that specification is the right one should treat the
result as unproven rather than refuted. Section 7 returns to this.

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
are reported, with 22 to 25 primary for the reasons given in Section 3.5 and 20 to
24 as robustness.

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

Decomposing the gap requires a benchmark, and the choice is consequential enough
to state explicitly. Zero growth is the right benchmark for asking whether the
exposed side contracted, and the answer is that it did not. It is the wrong
benchmark for asking which side opens the gap, because young employment overall
grew 5.8 percent over this window, so the no-gap counterfactual is both groups
growing at that common rate rather than at zero. Measured against the aggregate,
the exposed side underperforms by 3.9 percentage points and the unexposed side
outperforms by 2.9, splitting the gap 57.5 to 42.5 with a modest tilt toward the
exposed side. The 20 to 24 band splits 58.8 to 41.2. Both sides move and neither
dominates.

Against a zero benchmark the same arithmetic assigns the unexposed side 128
percent of the gap and the exposed side −28 percent. Shares outside the unit
interval are the diagnostic that the benchmark is wrong, and this paper does not
report that decomposition.

## 5.4 Underperformance is imprecise, contraction is ruled out

The finding above should not be read as an absence of any exposure-related
pattern. Young employment across all occupations grew 5.8 percent over the same
window for the 22 to 25 band. The exposed group grew 1.9 percent, a shortfall of
3.9 percentage points against the aggregate. The 20 to 24 band gives 5.7 percent
against 2.2 percent, a shortfall of 3.6 points.

That shortfall is a point estimate and it is not statistically significant. The
bootstrap interval runs [−8.9, +1.3] with p = 0.141, and it carries the same
p-value as the gap itself. That is necessary rather than coincidental: the
aggregate is a weighted average of the two groups, so the shortfall is a fixed
positive multiple of the gap, and the two are one test reported twice.

This is the honest two-sided statement and the paper carries it in both
directions. Young employment in AI-exposed occupations grew more slowly than young
employment overall, by a margin this data cannot distinguish from zero, which is
consistent with exposure suppressing entry at the margin and equally consistent
with no effect at all. It did not decline, which is what a displacement account
requires, and that part the data do resolve, because the interval excludes the
published magnitude decisively. Underperformance against a growing aggregate and
contraction in levels are different claims, and only the second is settled here,
in the negative.

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
of significance reflects the estimand rather than a conflict in the underlying
data. The 3.9 point shortfall against the aggregate is the same test carrying the
same p-value, so it is not independent evidence and is not presented as such.

Both belong in the paper and they support different sentences. The share result
establishes that young workers are increasingly sorted away from AI-exposed
occupations, and it is the paper's inferential finding. The levels result
establishes where in the distribution that sorting occurs, and it rejects a
specific published magnitude. It does not, on its own, establish a statistically
significant reallocation gap, and this paper does not claim one.

## 5.7 Summary

Reproducing the exposure gap in nationally representative data and decomposing it
does not support the displacement reading of the same gap in payroll data.
Employment of young workers in the most AI-exposed occupations grew 1.9 percent
over 2022 to 2026. It underperformed the aggregate by 3.9 points, a shortfall the
data cannot distinguish from zero, and it did not contract, which the data do
resolve: the interval excludes the published figure of −11 percent at p < 0.001.
Neither sample universe nor window explains that discrepancy, and an adversarially
stacked specification reaches only −4.7 percent on a third of the sample.

What the levels establish is narrower than this section's original framing. The
only movement identified with confidence is the less-exposed group growing 8.7
percent, and the gap splits roughly evenly between the two sides. The claim this
paper makes is that entry-level employment in AI-exposed occupations underperformed
a growing aggregate without contracting, and that the published magnitude does not
replicate outside payroll data. It does not claim a statistically significant
reallocation of young workers across the exposure distribution, which these levels
are too coarse to establish.

---

# 6. Capability predicts the gap, deployment does not

The estimate in Sections 3 and 4 uses a task-based exposure measure: a rating of
what share of an occupation's tasks a large language model could perform, built ex
ante from task descriptions. An obvious alternative is to use where AI is actually
being used. The Anthropic Economic Index maps Claude conversations to SOC
occupations and is the natural revealed-preference counterpart.

The two measures give different answers. This section reports the divergence and
argues that it is mostly a fact about the revealed measure.

The sample is the 456 occupations and 4,614 cells where both measures exist.

## 6.1 What the revealed measure measures

Usage is extraordinarily concentrated, and it is not concentrated where
employment is.

| | |
|---|---|
| share of all Claude usage in the top 10 occupations | **29.2%** |
| share of employment in those same 10 occupations | **0.6%** |
| correlation of usage share with occupation employment | +0.015 |

The ten are Counter and rental clerks, Editors, Writers and authors, Technical
writers, Library technicians, Archivists and curators, Librarians, Announcers,
News analysts and reporters, and Miscellaneous media and communication workers.
Setting aside the first, which is likely a crosswalk artifact given the company it
keeps, this is a list of writing, editorial, and library occupations. It is a
portrait of one model's user base and its dominant use case, and treating it as a
map of where AI is deployed across the economy assumes something the data do not
support.

The measure is also mechanically a share of conversations rather than a rate per
worker, so a per-worker intensity, usage share divided by employment share, is
reported alongside it throughout.

Correlations with the task-based measure are moderate, and one of them runs the
wrong way for a displacement story:

| revealed measure | corr with composite | corr with raw GPT-4 beta |
|---|---:|---:|
| usage share | +0.509 | +0.464 |
| usage per worker (log) | +0.381 | +0.396 |
| automation share of usage | **−0.337** | **−0.399** |
| AI autonomy | +0.227 | +0.237 |

The occupations with the highest task-based exposure have usage tilted toward
augmentation rather than automation. Capability and substitutive deployment are
pointing in opposite directions across occupations.

## 6.2 The same specification under each measure

**Table 6.1.** The Section 3 specification, 22 to 25 share, one measure at a time.

| measure | B | SE | p |
|---|---:|---:|---:|
| **task-based, composite** | **−0.4018** | 0.1043 | **0.0001** |
| **task-based, raw GPT-4 beta** | **−0.3801** | 0.1020 | **0.0002** |
| revealed, usage share | −0.2171 | 0.1134 | 0.0555 |
| revealed, usage per worker | −0.0474 | 0.1178 | 0.6873 |
| revealed, automation-weighted | −0.1750 | 0.1189 | 0.1411 |
| revealed, AI autonomy | +0.0673 | 0.0903 | 0.4556 |

The task-based measures are significant at better than 0.1 percent. The best the
revealed measures manage is marginal, and the per-worker version, which is the
right functional form if the question is how intensively an occupation's workers
use AI, is a clean null at p = 0.69.

## 6.3 Horse race

Entering both measures together settles which carries the result.

| specification | task-based | revealed |
|---|---:|---:|
| 22-25, vs usage share | **−0.4141 (0.002)** | +0.0267 (0.860) |
| 22-25, vs usage per worker | **−0.4684 (0.000)** | +0.1711 (0.156) |
| 20-24, vs usage share | **−0.4303 (0.003)** | −0.0282 (0.879) |
| 20-24, vs usage per worker | **−0.5403 (0.000)** | +0.2490 (0.157) |

The task-based coefficient is unchanged or larger when the revealed measure is
held constant, and the revealed coefficient goes to zero and changes sign. Whatever
signal the usage share carried on its own in Table 6.1 was the part of it
correlated with capability.

The automation tilt adds nothing. Entered alone it gives +0.1440 (p = 0.20) for the
22 to 25 band, and conditional on task-based exposure it is +0.0165 (p = 0.88).

**A note on AEI's automation and augmentation shares.** They are exact
complements, summing to 100 for every occupation with a correlation of exactly
−1.0000. Only one is identified, entering both is degenerate, and any result
attributing separate roles to the two is reporting a single dimension as though it
were two. Brynjolfsson et al. use this split as their secondary measure, and the
constraint applies to that use as well.

## 6.4 Neither measure predicts the pre-period

The revealed measure is a single 2026 cross-section, dated after the treatment
period it would be used to assign. That raises the possibility that it is
contaminated by the outcome. Running the placebo from Section 4.4 under each
measure tests it.

| measure | B | p |
|---|---:|---:|
| task-based, composite | +0.1195 | 0.148 |
| task-based, raw GPT-4 beta | +0.1173 | 0.162 |
| revealed, usage share | −0.0922 | 0.358 |
| revealed, usage per worker | −0.0769 | 0.535 |
| revealed, automation-weighted | −0.0562 | 0.565 |
| revealed, AI autonomy | +0.1092 | 0.271 |

Nothing is significant. The revealed measure's null in Table 6.1 is not an artifact
of it predicting the pre-period, and the task-based result is not an artifact of
the reverse.

## 6.5 What the divergence does and does not establish

Capability predicts the entry-level gap and deployment does not, and this is the
one place in the paper where two reasonable measures of the same construct
disagree sharply.

The tempting reading is an anticipation channel: firms adjust entry-level hiring
on what they believe AI will be able to do, ahead of any actual deployment, so a
capability rating tracks hiring while a usage log does not. That reading is
consistent with everything in this section and with the ramp in Section 3.3.

It is not established here, and the obstacle is Section 6.1. A measure that puts
29 percent of its mass on ten occupations holding 0.6 percent of employment, and
which lists librarians and announcers among the most AI-intensive occupations in
the economy, is not a reliable index of deployment. The null could mean deployment
does not drive entry-level hiring. It could equally mean this measure does not
capture deployment. These data cannot separate those, and the paper does not claim
to.

What the section does establish is narrower and still useful. Results in this
literature are measure-dependent, the dependence is large enough to flip a headline
finding from significant to null, and any single-measure result, this paper's
included, should be read with that in mind. It also establishes that the
automation-augmentation split available from AEI is one dimension rather than two.

