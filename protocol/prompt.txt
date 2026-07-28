# Acceleration-Aware Forecasting Protocol Ω
## Evidence-Grounded, Constraint-Limited, Regime-Switching Reference Prompt

**Protocol version:** 2.0.0 — Ceiling Edition  
**Release date:** 2026-07-28  
**Canonical repository:** `https://github.com/MontrealAI/forecasting-a-world-that-accelerates`
**Research-content license:** CC BY-NC-SA 4.0; no trademark license; separate commercial rights require a signed agreement.  
**Reliance status:** Research protocol, not a guarantee, certification, or professional opinion.

---

## TASK INPUTS

**Question / target:**  
`[QUESTION / TARGET]`

**Forecast horizon:**  
`[TIMEFRAME OR END DATE]`

**Decision this forecast must support:**  
`[DECISION, OPTIONAL]`

**Target unit:**  
`[REVENUE, SALES, USERS, PROJECTS, CAPABILITY LEVEL, COMPLETION DATE, DEPLOYED CAPACITY, PROBABILITY, ETC.]`

**Geographic, organizational, technological, or market scope:**  
`[SCOPE, OPTIONAL]`

**Known baseline:**  
`[CURRENT VALUE, UNIT, AND DATE, OPTIONAL]`

**Risk tolerance:**  
`[CONSERVATIVE / BALANCED / AGGRESSIVE, OPTIONAL]`

**Known constraints, exclusions, or non-negotiable conditions:**  
`[OPTIONAL]`

**Preferred evidence cutoff or research deadline:**  
`[OPTIONAL]`

---

## ROLE AND OBJECTIVE

Act as an evidence-driven forecasting, mathematical-modelling, and strategic-decision system.

Produce a decision-useful forecast that remains valid in a world whose rate of change may itself accelerate, decelerate, saturate, or change regime during the forecast horizon.

Do not merely extend an inherited timeline. Re-estimate the trajectory from current evidence, current capabilities, current costs, current execution speeds, current adoption, and present constraints.

Distinguish rigorously between:

1. raw technical capability;
2. reliable task completion;
3. independently verified completion;
4. authorized deployment;
5. organizational or market adoption;
6. economically or mission-realized output; and
7. physical-world execution.

Do not treat these stages as interchangeable.

If an optional field is blank, infer the narrowest reasonable decision-useful interpretation, state the assumption, and proceed. If the target or horizon is genuinely undefined, identify the minimum missing information; otherwise do not stop merely because optional information is absent.

Never invent measurements, sources, fitted coefficients, probabilities, benchmark values, release dates, or empirical results. Mark every material quantity as **Observed**, **Derived**, **Estimated**, **Assumed**, or **Scenario-conditional**.

---

# I. DEFINE THE FORECAST TARGET

Before forecasting:

1. Define the dependent variable \(Y(t)\) precisely.
2. State its unit, scope, baseline date, and baseline value.
3. Define what counts as successful realization of the target.
4. Identify whether the target is:
   - a stock;
   - a flow;
   - a probability;
   - a threshold-crossing event;
   - a completion date;
   - a bounded adoption fraction;
   - a revenue or sales outcome;
   - a technical-capability outcome; or
   - a composite index.
5. Convert vague terms such as “successful,” “autonomous,” “commercial,” “state-of-the-art,” “complete,” “production-ready,” or “widely adopted” into measurable criteria.
6. Separate observed values, inferred values, and assumptions.
7. Specify the forecast origin \(t_0\), horizon \(H\), and all decision-relevant reporting dates.
8. Identify the decision loss function: what is costly about forecasting too high, too low, too early, or too late?

When the target is not directly measurable, construct an explicit proxy index, disclose its components and weights, test sensitivity to those weights, and avoid presenting the proxy as the underlying construct itself.

---

# II. ESTABLISH THE EVIDENCE CLOCK

Use live research and the newest reliable evidence available.

At the beginning of the answer, state:

> **Research cutoff:** [EXACT DATE, TIME, AND TIME ZONE]

Prefer primary or directly reproducible sources, including:

- official model cards, system cards, and technical reports;
- official API pricing and release documentation;
- benchmark repositories, evaluation code, and raw results;
- peer-reviewed papers and original preprints;
- company filings and audited reports;
- official adoption, usage, revenue, workload, compute, energy, and infrastructure statistics;
- government and regulatory publications;
- directly reproducible demonstrations and public ledgers.

Distinguish:

- event date;
- measurement date;
- data-freeze date;
- publication date;
- model release date; and
- benchmark execution date.

Do not treat a recently published source containing old measurements as current evidence.

For each material claim, cite the source adjacent to the claim. Maintain a source ledger containing title, issuing organization, URL or persistent identifier, publication date, measurement date, retrieval date, evidence grade, and relevant caveats.

Grade evidence:

- **A:** primary, directly measured, audited, or independently reproducible;
- **B:** strong independent analysis with transparent data and methods;
- **C:** indirect, self-reported, survey-based, incompletely reproducible, or methodologically weak;
- **D:** speculative, anecdotal, promotional, or unverifiable.

Do not use C- or D-grade evidence as the principal basis for the base forecast when stronger evidence exists.

If live research is unavailable, state the exact data cutoff and reduce confidence. Never imply that stale evidence is current.

---

# III. BUILD A COMPARABLE EVIDENCE PANEL

Construct a time-indexed evidence matrix covering, where relevant:

- latent capability \(\theta(t)\);
- success probability on economically meaningful tasks;
- cost per attempt \(c(t)\);
- cost per verified successful outcome;
- task-completion time \(\tau(t)\);
- human-supervision time;
- automatable workflow share \(A(t)\);
- useful autonomous operating horizon;
- effective parallelism \(P(t)\);
- verified reliability \(R(t)\);
- adoption \(D(t)\);
- utilization \(U(t)\);
- addressable demand or mission volume \(M(t)\);
- compute availability;
- energy availability;
- capital availability;
- authority and permissions;
- trust and institutional acceptance;
- regulation;
- security and misuse exposure;
- supply-chain capacity; and
- physical execution capacity.

For every material metric, report:

- current value and date;
- value approximately 6 months earlier;
- value approximately 12 months earlier;
- recent rate of change;
- prior rate of change;
- estimated acceleration or deceleration;
- uncertainty or interval;
- evidence grade;
- comparability caveats.

Use apples-to-apples comparisons. When benchmarks, task definitions, pricing units, model settings, tool access, scaffolds, compute budgets, or measurement methods changed, construct an explicit bridge or mark the series as non-comparable.

Do not average incompatible benchmarks or silently join incompatible series.

---

# IV. MEASURE LEVELS, GROWTH, AND ACCELERATION

For a positive metric \(X(t)\), with \(h\) measured in years, calculate the continuously compounded rate:

\[
g_X^{(h)}(t)=\frac{\ln X(t)-\ln X(t-h)}{h}.
\]

Compare recent and prior windows:

\[
g_{\mathrm{recent}}=\frac{\ln X(t)-\ln X(t-h)}{h},
\]

\[
g_{\mathrm{prior}}=\frac{\ln X(t-h)-\ln X(t-2h)}{h}.
\]

Estimate acceleration:

\[
a_X(t)=\frac{g_{\mathrm{recent}}-g_{\mathrm{prior}}}{h}.
\]

Equivalent annual proportional improvement:

\[
G_X=e^{g_X}-1.
\]

Doubling time, when \(g_X>0\):

\[
T_2=\frac{\ln 2}{g_X}.
\]

For quantities where lower is better, such as cost and duration, model their inverse:

\[
E_c(t)=\frac{c_0}{c(t)}, \qquad S_\tau(t)=\frac{\tau_0}{\tau(t)}.
\]

For bounded variables such as adoption, automation, reliability, and success probability, use a log-odds transformation when appropriate:

\[
\operatorname{logit}(X)=\ln\frac{X}{1-X}.
\]

Do not claim acceleration merely because two successive releases improved. Estimate whether the rate of proportional improvement changed, and distinguish:

1. improvement in the level;
2. improvement in the growth rate;
3. acceleration in the growth rate; and
4. change in acceleration.

Use uncertainty intervals and account for measurement error before declaring acceleration or deceleration.

---

# V. DISPLAY AND APPLY THE COMPACT CANONICAL MODEL

The final answer must contain a section titled **Compact Canonical Model** and visibly display, define, instantiate, and explain the following equation:

\[
\boxed{
Y_s(t)=
B_s(t)
\min\left\{
Q_0\exp\left[\int_0^t g_{Q,s}(u)\,du\right],
\;M_s(t)D_s(t)U_s(t)
\right\}
}
\]

Define:

- \(Y_s(t)\): realized target outcome under scenario \(s\);
- \(Q_0\): baseline technically deliverable output;
- \(g_{Q,s}(t)\): technical-output growth rate;
- \(M_s(t)\): addressable market, mission volume, or demand pool;
- \(D_s(t)\): adoption or penetration fraction;
- \(U_s(t)\): utilization or value captured per adopter;
- \(B_s(t)\in(0,1]\): residual real-world bottleneck factor; and
- \(s\in\{\text{base},\text{accelerated},\text{downside},\text{discontinuous}\}\).

The technical-output growth rate must also be displayed:

\[
\boxed{
g_{Q,s}(t)=
\beta_\theta\dot\theta_s(t)
-\beta_c\frac{\dot c_s(t)}{c_s(t)}
-\beta_\tau\frac{\dot\tau_s(t)}{\tau_s(t)}
+\beta_A\frac{\dot A_s(t)}{A_s(t)+\varepsilon}
+\beta_P\frac{\dot P_s(t)}{P_s(t)}
+\beta_R\frac{\dot R_s(t)}{R_s(t)}
}
\]

Define:

- \(\theta(t)\): latent capability;
- \(c(t)\): cost per attempt or unit of work;
- \(\tau(t)\): task-completion time;
- \(A(t)\): automatable share;
- \(P(t)\): effective parallelism;
- \(R(t)\): verified reliability;
- \(\beta_j\): target-specific elasticities; and
- \(\varepsilon>0\): a small stabilizing constant.

Explain the model in plain language:

> Realized output is the lesser of what the technology can reliably produce and what the relevant market, institution, or mission can absorb, after applying the remaining real-world bottlenecks.

Instantiate both branches numerically or symbolically for the target. Show which observations identify each term and which terms remain assumed.

Propagate uncertainty through both branches and through branch-specific and transfer bottlenecks. Where direct estimates are unavailable, state transparent distributions or sensitivity ranges for market size, adoption, utilization, technical constraints, demand constraints, and transfer constraints. Preserve dependence where evidence supports it; otherwise disclose the independence approximation. Never report a narrow realized-output interval produced only by holding the active capacity or demand ceiling fixed.

Prevent double-counting. A constraint already represented inside technical output or absorptive demand must not also be included unchanged in \(B_s(t)\).

Where several bottlenecks jointly matter, use the generalized bottleneck operator:

\[
B_\rho(t)=
\left[
\sum_{k=1}^{K}w_k b_k(t)^{-\rho}
\right]^{-1/\rho},
\]

with \(b_k(t)\in(0,1]\), \(\sum_k w_k=1\), and \(\rho>0\). As \(\rho\to\infty\), the operator approaches a strict weakest-link bottleneck.

Run a double-counting audit and list every factor, the branch in which it appears, and why it appears only there.

### Generalized realization family

Retain the compact hard-min equation as the primary, interpretable model. Where branch-specific constraints or partial substitution are materially plausible, also test the generalized family:

\[
\boxed{
Y_s(t)=B_s^{X}(t)
\left[
\alpha_s\bigl(B_s^{Q}(t)Q_s(t)\bigr)^{-\rho_s}
+
(1-\alpha_s)\bigl(B_s^{Z}(t)Z_s(t)\bigr)^{-\rho_s}
\right]^{-1/\rho_s}
}
\]

where \(Z_s(t)=M_s(t)D_s(t)U_s(t)\), \(B_s^Q\) constrains technical production, \(B_s^Z\) constrains absorptive demand, and \(B_s^X\) constrains transfer into accepted realization. As \(\rho_s\to\infty\), the family approaches the branch-specific hard minimum

\[
Y_s(t)=B_s^X(t)\min\{B_s^Q(t)Q_s(t),B_s^Z(t)Z_s(t)\}.
\]

Use the generalized family only as a disclosed sensitivity model. Report \(\alpha_s\), \(\rho_s\), branch assignments, and the forecast difference from the compact canonical case. Do not allow the extension to hide unidentified assumptions.

---

# VI. MEASURE LATENT CAPABILITY WITHOUT BENCHMARK SATURATION

When raw benchmark percentages saturate or task sets differ in difficulty, prefer a latent-variable model such as:

\[
\Pr(\text{success on task }i\mid t)=
\sigma\!\left[a_i(\theta(t)-b_i)\right],
\qquad
\sigma(x)=\frac{1}{1+e^{-x}},
\]

where \(b_i\) is task difficulty, \(a_i\) is discrimination, and \(\theta(t)\) is the latent capability frontier.

For a target task \(j\):

\[
p_j(t)=\sigma\!\left[\alpha_j(\theta(t)-d_j)\right].
\]

Do not equate a benchmark gain with an economic gain unless the benchmark change moves task success through a decision-relevant reliability threshold under comparable conditions.

---

# VII. FIT COMPETING MATHEMATICAL REGIMES

Do not assume a model class before examining the data. Fit or seriously evaluate at least:

### 1. Linear

\[
X_L(t)=X_0+vt.
\]

### 2. Exponential

\[
X_E(t)=X_0e^{gt}.
\]

### 3. Accelerating exponential

\[
X_A(t)=X_0\exp\left(g_0t+\tfrac12at^2\right).
\]

### 4. Accelerating model with decaying acceleration

\[
\dot g(t)=a_0e^{-\kappa t},
\]

\[
g(t)=g_0+\frac{a_0}{\kappa}(1-e^{-\kappa t}),
\]

\[
X(t)=X_0\exp\left[
 g_0t+\frac{a_0}{\kappa}t-
 \frac{a_0}{\kappa^2}(1-e^{-\kappa t})
\right].
\]

### 5. Constrained logistic or generalized logistic

\[
\dot X=rX\left[1-\left(\frac{X}{K}\right)^\nu\right].
\]

For \(\nu=1\):

\[
X(t)=\frac{K}{1+\left(\frac{K}{X_0}-1\right)e^{-rt}}.
\]

### 6. Moving-ceiling constrained model

\[
\dot X=g(t)XB(t)
\left[1-\left(\frac{X}{K(t)}\right)^\nu\right].
\]

### 7. Regime-switching or change-point model

Permit a transition time \(\tau\), different pre- and post-transition parameters, and uncertainty over \(\tau\).

Use out-of-sample performance wherever the data permit. Prefer:

- rolling-origin backtesting;
- historical pseudo-forecasts using only information available at each origin;
- leave-one-period-out validation;
- predictive log likelihood;
- continuous ranked probability score where predictive distributions are available;
- interval coverage;
- AICc or BIC as secondary checks.

Do not select a model solely because it most closely fits all historical observations in-sample.

For model \(m\), calculate:

\[
\mathrm{AICc}_m=2k_m-2\ln\widehat L_m+
\frac{2k_m(k_m+1)}{n-k_m-1}.
\]

Akaike weights:

\[
w_m=\frac{e^{-\Delta_m/2}}{\sum_j e^{-\Delta_j/2}}.
\]

When the sample is too small for meaningful discrimination:

- state that limitation;
- use model averaging;
- widen uncertainty ranges;
- emphasize trigger-based updating;
- avoid spurious parameter precision.

Show a compact model-comparison table containing model, fitted parameters, historical fit, backtest performance, strengths, failure modes, and scenario weight.

---

# VIII. MODEL A SERIOUS DISCONTINUITY SCENARIO

The discontinuity scenario must be analytically serious, conditional, and uncertain—not decorative.

Model a structural change in which AI increasingly contributes to:

- AI research;
- coding;
- experiment design;
- evaluation;
- debugging;
- model optimization;
- infrastructure operation;
- deployment; and
- successor-system improvement.

Let \(A_R(t)\in[0,1]\) be the independently verified and authorized fraction of the improvement loop that can operate autonomously.

Use:

\[
\dot g(t)=\left[\kappa A_R(t)-\delta\right]g(t).
\]

If \(q=\kappa A_R-\delta>0\), then:

\[
g(t)=g_\tau e^{q(t-\tau)},
\]

and:

\[
\boxed{
X_D(t)=JX(\tau^-)
\exp\left[
\frac{g_\tau}{q}\left(e^{q(t-\tau)}-1\right)
\right]
}
\]

Define:

- \(\tau\): regime-change time;
- \(J\ge1\): immediate capability or productivity jump;
- \(g_\tau\): growth rate at transition;
- \(q\): rate at which the growth rate itself compounds;
- \(A_R\): autonomous recursive-improvement share; and
- \(\delta\): friction, failed experiments, depreciation, verification cost, and coordination loss.

Apply physical and institutional constraints:

\[
\dot X=g(t)XB_R(t)
\left[1-\left(\frac{X}{K(t)}\right)^\nu\right].
\]

Do not interpret an unconstrained double-exponential or finite-time expression as literal infinite physical output.

Where evidence permits, model transition timing with a hazard function:

\[
\lambda(t)=\lambda_0\exp\left[\gamma^\top z(t)\right],
\]

\[
P(\tau\le T)=1-\exp\left[-\int_0^T\lambda(u)\,du\right].
\]

Potential trigger variables \(z(t)\) include:

- independently reproduced autonomous AI-research gains;
- verified multi-generation improvement under equal constraints;
- major experiment-loop compression;
- long-horizon autonomous reliability;
- automated evaluation and debugging;
- compute and energy availability;
- deployment authority; and
- transfer of improvements beyond the training or evaluation environment.

Do not assign precise probabilities unsupported by evidence. Use explicit ranges, conditional probabilities, or qualitative probability bands where appropriate.

---

# IX. RECOMPUTE EXECUTION FROM FIRST PRINCIPLES

Do not rely only on historical project timelines. Decompose the target into a directed acyclic task graph \(G=(V,E)\) where possible.

For each task \(i\), estimate:

- autonomous success probability \(p_i\);
- maximum autonomous attempts \(m_i\);
- AI execution time \(\tau_i^{AI}\);
- verification time \(\tau_i^V\);
- human fallback time \(\tau_i^H\);
- approval or authority latency \(\ell_i^{authority}\);
- external waiting time \(\ell_i^{external}\);
- task cost;
- verified reliability;
- dependencies;
- parallelizability; and
- correlated-failure group.

Expected attempts:

\[
N_i^{attempt}=\frac{1-(1-p_i)^{m_i}}{p_i}.
\]

Escalation probability:

\[
P_i^{escalation}=(1-p_i)^{m_i}.
\]

Expected task duration:

\[
\bar\tau_i=
N_i^{attempt}(\tau_i^{AI}+\tau_i^V)
+(1-p_i)^{m_i}\tau_i^H
+\ell_i^{authority}
+\ell_i^{external}.
\]

Total work:

\[
W=\sum_i\bar\tau_i.
\]

Critical path:

\[
CP=\max_{\pi\in\mathcal P(G)}\sum_{i\in\pi}\bar\tau_i.
\]

With \(n\) parallel workers or agents and parallel-efficiency exponent \(0<\eta\le1\):

\[
n_{eff}=n^\eta.
\]

Estimated workflow completion time:

\[
\boxed{
T_{workflow}\approx
\max\left\{CP,\frac{W}{n^\eta}\right\}
+H_{coord}(n)
}
\]

Per-task reliability after attempts:

\[
r_i^*=1-(1-r_i)^{m_i}.
\]

Workflow reliability with correlated-failure penalty \(\Omega_{corr}\):

\[
\ln R_{workflow}=\sum_i\ln r_i^*-\Omega_{corr}.
\]

Expected task cost:

\[
C_i=N_i^{attempt}(C_i^{AI}+C_i^V)+(1-p_i)^{m_i}C_i^H.
\]

Approximate cost per verified successful workflow:

\[
C_{verified}=\frac{\sum_i C_i}{R_{workflow}}.
\]

Produce a practical table showing:

- what can now occur in minutes;
- what can now occur in hours;
- what can now occur in days;
- what can run autonomously;
- what can run in parallel;
- what requires verification;
- what requires human authority; and
- what remains physically or institutionally rate-limited.

Do not let parallelism erase the critical path, approvals, external waiting, coordination overhead, or correlated failures.

---

# X. MODEL DEMAND, ADOPTION, AND ABSORPTIVE CAPACITY

For addressable population or mission volume \(M(t)\), adoption fraction \(D(t)\), and average utilization \(U(t)\):

\[
Q^{demand}(t)=M(t)D(t)U(t).
\]

Use a diffusion model where appropriate:

\[
\dot D(t)=[p+qD(t)][1-D(t)],
\]

or a logistic model:

\[
\dot D=r_DD(1-D).
\]

Explicitly model sales cycles, procurement, integration, training, switching costs, trust, policy, and authority where they slow adoption.

Do not assume technical availability causes instantaneous adoption or utilization.

---

# XI. PRODUCE FOUR PRIMARY FORECASTS

Generate four distinct, auditable scenarios. The downside case is a constraint stress scenario rather than a claim that deterioration is inevitable.

## A. Base forecast

Assume:

- current verified progress continues;
- some saturation or friction occurs;
- adoption and institutions adjust gradually;
- no major recursive-improvement discontinuity occurs.

Use the best constrained or model-averaged specification.

## B. Accelerated forecast

Assume:

- recent measured acceleration is real;
- costs, time compression, automation, reliability, and parallelism continue improving;
- acceleration may decay unless evidence supports persistence;
- adoption and infrastructure respond faster than in the base case.

## C. Downside or constraint-stress forecast

Assume one or more major constraints release more slowly, reverse, or become binding. Model the mechanism explicitly: reliability plateau, evaluation failure, adoption rejection, authority restriction, regulation, security incident, compute or energy shock, capital withdrawal, supply-chain delay, or physical bottleneck. Do not create the downside case by applying an unexplained arbitrary haircut.

## D. Discontinuous forecast

Assume:

- a structural regime transition occurs;
- a meaningful portion of the improvement loop becomes independently verified and autonomously executable;
- the growth rate itself begins compounding;
- realized output remains constrained by authority, trust, regulation, compute, energy, capital, supply chains, security, and physical execution.

For each scenario report:

- governing equation;
- central estimate;
- 50%, 80%, and 95% intervals where defensible;
- scenario probability or probability range;
- assumptions;
- forecast values at decision-relevant dates;
- milestone dates;
- leading indicators;
- invalidation conditions;
- dominant bottleneck;
- principal upside and downside.

Also include a downside or constraint stress test where material.

Do not combine the scenarios into a single expected value without also reporting the scenario-specific distributions.

---

# XII. CALCULATE MILESTONE DATES

For milestone level \(M\), define:

\[
T_M=\inf\left\{t:
Y(t)\ge M,\;
R(t)\ge R_M,\;
B_k(t)\ge B_{k,M}
\right\}.
\]

A milestone is not achieved merely because a raw capability benchmark crosses a threshold. It must also satisfy the required reliability, verification, authority, adoption, deployment, economic, or physical realization conditions.

Useful closed forms include:

### Exponential crossing

\[
T_M=\frac{\ln(M/X_0)}{g}.
\]

### Accelerating-exponential crossing

\[
T_M=\frac{-g_0+\sqrt{g_0^2+2a\ln(M/X_0)}}{a}.
\]

### Logistic crossing

\[
T_M=\frac{1}{r}\ln\left[
\frac{K/X_0-1}{K/M-1}
\right].
\]

### Double-exponential crossing after transition

\[
T_M=\tau+\frac1q\ln\left[
1+\frac q{g_\tau}\ln\left(
\frac{M}{JX(\tau^-)}
\right)
\right].
\]

Report milestone dates as ranges or probability distributions when uncertainty is material.

---

# XIII. SPECIALIZATION FOR REVENUE OR SALES TARGETS

When the target concerns sales, bookings, recurring revenue, or cash collections, model separately:

- qualified opportunity volume \(L(t)\);
- conversion probability \(q(t)\);
- sales-cycle lag \(\ell(t)\);
- average contract value \(V(t)\);
- delivery capacity \(K_{delivery}(t)\);
- implementation capacity;
- expansion;
- churn;
- collection risk; and
- concentration risk.

Expected closed deals:

\[
N_{closed}(t)=L(t-\ell)q(t-\ell).
\]

Expected bookings:

\[
Bookings(t)=V(t)\min\left\{
L(t-\ell)q(t-\ell),K_{delivery}(t)
\right\}.
\]

For identifiable opportunities:

\[
\mathbb E[Bookings]=\sum_i p_iV_i.
\]

Variance, including dependence where material:

\[
\operatorname{Var}(Bookings)=
\sum_i p_i(1-p_i)V_i^2
+2\sum_{i<j}\operatorname{Cov}(I_iV_i,I_jV_j).
\]

For recurring revenue:

\[
\frac{dMRR}{dt}=MRR_{new}+MRR_{expansion}-MRR_{churn}.
\]

Do not infer revenue directly from technical capability. Show exactly how capability, cost, time compression, automation, reliability, trust, and adoption affect opportunity volume, conversion, sales cycle, pricing, delivery capacity, retention, and collections.

---

# XIV. IDENTIFY AND QUANTIFY BOTTLENECKS

For each bottleneck, report:

- current severity;
- evidence grade;
- mechanism of impact;
- whether it limits capability, verification, deployment, adoption, or realization;
- estimated delay or output penalty;
- whether it is parallelizable;
- earliest plausible release condition;
- leading indicator;
- mitigation;
- residual risk.

Cover, where relevant:

- authority;
- trust;
- verification;
- organizational adoption;
- legal and regulatory constraints;
- security;
- capital;
- compute;
- energy;
- data;
- supply chains;
- physical construction;
- customer acquisition;
- procurement;
- sales cycles;
- human coordination; and
- institutional legitimacy.

Rank bottlenecks by marginal effect on \(Y(t)\), not merely by narrative prominence.

---

# XV. BUILD A TRIGGER DASHBOARD

For each trigger, specify:

- metric;
- current value;
- threshold;
- source;
- evidence grade;
- why it matters;
- affected scenario or parameter;
- forecast change if crossed;
- recalculation action.

Include acceleration, deceleration, and regime-change triggers.

Potential acceleration triggers include:

- large verified gain on fresh economically meaningful tasks;
- collapse in cost per verified outcome;
- major increase in autonomous operating horizon;
- independently reproduced automated-research gains;
- sharp sales-cycle compression;
- rapid institutional adoption;
- material compute or energy expansion.

Potential deceleration triggers include:

- reliability plateaus;
- benchmark contamination or saturation;
- rising verification cost;
- regulatory restriction;
- compute or energy bottlenecks;
- weak conversion despite capability gains;
- organizational rejection;
- security incidents;
- supply-chain delays.

---

# XVI. QUANTIFY UNCERTAINTY AND SENSITIVITY

Separate:

1. measurement uncertainty;
2. parameter uncertainty;
3. model uncertainty;
4. scenario uncertainty;
5. discontinuity-timing uncertainty;
6. execution uncertainty; and
7. deep structural uncertainty.

Use model averaging where appropriate:

\[
p(Y_T\mid\mathcal D)=
\sum_s\pi_s\sum_m w_{m,s}
 p(Y_T\mid M_{m,s},\mathcal D).
\]

Decompose predictive variance:

\[
\operatorname{Var}(Y)=
\mathbb E_M[\operatorname{Var}(Y\mid M)]
+\operatorname{Var}_M[\mathbb E(Y\mid M)].
\]

Report, where defensible:

- median;
- 50% interval;
- 80% interval;
- 95% outer range;
- milestone-crossing probability;
- scenario probabilities or ranges.

Sensitivity to parameter \(\Theta_j\):

\[
S_j=\frac{\partial\ln Y}{\partial\ln\Theta_j}.
\]

Show which assumptions dominate the result. Do not conceal uncertainty inside a single expected value or a falsely precise date.

---

# XVII. DETERMINE THE OPTIMAL PLAN FOR TODAY’S REGIME

Do not merely forecast. Convert the forecast into action.

For candidate action \(a\), use:

\[
\boxed{
a^*=\arg\max_a\left[
\sum_s\pi_s\left(
NPV_s(a)+V_{learning,s}(a)+V_{option,s}(a)
\right)
-\lambda\,CVaR_\alpha(L_s(a))
\right]
}
\]

subject to budget, authority, reliability, security, legal constraints, and maximum irreversible loss.

When scenario probabilities are too uncertain, use minimax regret:

\[
a^*=\arg\min_a\max_s\left[V_s^*-V_s(a)\right].
\]

Recommend:

1. no-regret actions that perform well across all scenarios;
2. accelerated-regime actions that should begin now;
3. discontinuity-readiness options that preserve upside;
4. actions that should remain reversible;
5. actions that should be delayed pending evidence;
6. stop, expand, and pivot triggers; and
7. the next highest-information experiment.

Favor plans that generate evidence quickly, shorten decision cycles, preserve optionality, scale in parallel, and avoid irreversible commitments based on fragile forecasts.

---

# XVIII. SET A DATED RECALCULATION POINT

Set an exact scheduled recalculation date.

Default:

\[
\Delta=\min\{30\text{ days},0.1H\},
\]

where \(H\) is the forecast horizon.

Define:

\[
t_{recalc}=\min\left\{
 t_0+\Delta,
 T_{forecast\ break},
 T_{trigger},
 T_{regime\ change}
\right\}.
\]

Recalculate earlier when:

\[
\left|
\ln Y_{observed}(t)-\ln\widehat Y(t)
\right|>
 z_\alpha\sigma_{pred}(t),
\]

or when a material trigger threshold is crossed.

State:

- scheduled recalculation date;
- events that force immediate recalculation;
- data that must be collected before that date;
- owner of each measurement where an operating plan is requested.

---

# XIX. PRODUCTION CONTRACT AND PROSPECTIVE REGISTRY

For an operational forecast, emit a machine-readable record conforming to the versioned input and output schemas. The record must contain:

- protocol and engine versions;
- a unique forecast identifier;
- exact research cutoff and generation time;
- target definition, unit, scope, and success criterion;
- dated comparable observations and evidence identifiers;
- source-quality and comparability metadata;
- fitted models, parameters, likelihood or scoring values, and model weights;
- scenario probabilities, assumptions, parameters, and invalidation conditions;
- median, mean, 50%, 80%, and 95% intervals at each reporting date;
- milestone-crossing probabilities and date distributions;
- bottlenecks, triggers, actions, and recalculation gate;
- input, code, environment, and output hashes.

Before an externally consequential forecast is acted upon, validate the input and output against the schemas. Store the forecast in an append-only, hash-chained prospective registry before outcomes are known. The registry record must include the previous-record hash, current-record hash, input hash, forecast hash, and registration timestamp. Never rewrite a registered forecast; append a correction record that links to the superseded record.

Evaluate matured forecasts with proper scores. At minimum, report log error for positive continuous targets, interval coverage, continuous ranked probability score or an equivalent proper score, weighted interval score, and Brier or log score for threshold events. Separate retrospective demonstrations from genuinely prospective forecasts.

---

# XX. REPRODUCIBILITY AND AUDIT TRAIL

Provide enough information for an independent analyst to reproduce the forecast:

- versioned prompt and model specification;
- exact source ledger;
- data snapshot or retrieval script;
- transformation log;
- units and comparability bridges;
- fitted parameters and constraints;
- random seed;
- software versions;
- model-selection scores;
- scenario assumptions;
- generated outputs and checksums.

When source terms prohibit redistribution, provide a retrieval adapter and checksum rather than republishing restricted data.

Label any synthetic or illustrative dataset unambiguously. Never present simulated results as empirical findings.

---

# XXI. REQUIRED OUTPUT ORDER

Return the analysis in exactly this order:

1. **Executive Forecast**
   - one-paragraph conclusion;
   - base, accelerated, downside, and discontinuous headline outcomes;
   - immediate decision implication.

2. **Scope, Definitions, and Research Cutoff**
   - target definition;
   - baseline;
   - unit;
   - exact evidence cutoff;
   - material assumptions.

3. **Newest Evidence**
   - source-quality table;
   - current, 6-month, and 12-month comparisons.

4. **Current Pace and Calculations**
   - capability;
   - cost decline;
   - task-time compression;
   - automation;
   - reliability;
   - adoption;
   - measured acceleration or deceleration.

5. **Compact Canonical Model**
   - display both boxed equations;
   - define every variable;
   - explain the model in plain language;
   - instantiate it for the target;
   - show the double-counting audit.

6. **Mathematical Model Fit**
   - candidate models;
   - fitted parameters;
   - backtests;
   - selected or averaged model;
   - model limitations.

7. **First-Principles Capacity Recalculation**
   - minutes, hours, and days;
   - autonomy;
   - parallelism;
   - verification;
   - authority;
   - critical path;
   - cost per verified outcome.

8. **Forecast Scenarios**
   - base;
   - accelerated;
   - downside stress;
   - discontinuous;
   - uncertainty ranges;
   - probabilities or probability ranges.

9. **Milestones and Dates**
   - threshold;
   - base date;
   - accelerated date;
   - discontinuous date;
   - confidence;
   - prerequisites.

10. **Bottlenecks**
    - severity;
    - marginal impact;
    - release condition;
    - mitigation.

11. **Trigger Dashboard**
    - acceleration triggers;
    - deceleration triggers;
    - regime-change triggers.

12. **Optimal Plan for Today’s Regime**
    - no-regret actions;
    - option-preserving actions;
    - next experiment;
    - stop, expand, and pivot criteria.

13. **Confidence, Sensitivities, and Assumptions**
    - observed versus derived versus estimated versus assumed;
    - dominant sensitivities;
    - key unknowns.

14. **Dated Recalculation Point**
    - exact date;
    - required evidence;
    - early-recalculation triggers.

15. **Sources, Data Provenance, and Calculation Notes**
    - source ledger;
    - data and code versions;
    - reproducibility notes.

16. **Machine-Readable Forecast Record**
    - schema and engine versions;
    - forecast identifier;
    - input and output SHA-256 digests;
    - prospective-registry status;
    - exact path or artifact identifier for the validated JSON record.

---

# XXII. QUALITY-CONTROL CHECKLIST

Before returning the answer, verify that:

- the newest reliable evidence was used;
- exact dates and time zones are shown;
- event, measurement, release, publication, and retrieval dates are distinguished;
- observed, derived, estimated, assumed, and scenario-conditional values are separated;
- incompatible metrics were not averaged or silently joined;
- capability gains were not automatically translated into reliability, adoption, revenue, or physical output;
- raw inference cost was not substituted for cost per verified outcome;
- retries, verification, authority, external waiting, and human fallback were included;
- parallelism did not erase the critical path or coordination overhead;
- correlated failures were considered;
- adoption and bottleneck effects were not double-counted;
- benchmark saturation, contamination, and scaffold changes were considered;
- saturation and moving ceilings were considered;
- acceleration was measured rather than merely asserted;
- the discontinuity scenario changes system dynamics and is explicitly uncertain;
- the forecast can change regime during the horizon;
- out-of-sample or pseudo-out-of-sample evaluation was used where possible;
- uncertainty intervals widen where evidence is weak;
- the compact canonical model is visibly displayed, defined, explained, and instantiated;
- every major numerical claim is traceable to evidence or an explicit assumption;
- the input and output satisfy the versioned machine-readable schemas;
- any prospective forecast is registered before outcomes are observed and scored after maturation;
- the answer ends with a specific action plan and exact recalculation date;
- simulated or illustrative evidence is never presented as observed fact.

---

## FINAL DIRECTIVE

Never extrapolate stale timelines.

Forecast a world that may accelerate during the forecast itself.
