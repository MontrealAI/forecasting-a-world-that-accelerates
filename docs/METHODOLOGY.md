# Methodology map

The framework is organized around a chain that must not be collapsed:

`capability → reliable execution → verified completion → authorized deployment → adoption → realized outcome`

## Canonical realized-outcome equation

Under scenario `s`:

`Y_s(t) = B_s(t) min{ Q_0 exp[∫ g_Q,s(u)du], M_s(t)D_s(t)U_s(t) }`

The first branch is technical capacity. The second is absorptive demand. `B_s(t)` is a residual bottleneck factor that may include authority, trust, regulation, capital, compute, energy, supply chains, and physical execution only to the extent those constraints have not already been represented elsewhere.

## Growth decomposition

Technical-output growth is decomposed into target-specific elasticities on latent capability, cost decline, time compression, automation, effective parallelism, and verified reliability. The elasticities are parameters to estimate or stress-test, not universal constants.

## Candidate regimes

The implementation evaluates linear, exponential, accelerating exponential, decaying acceleration, logistic, and change-point structures. The paper also formalizes a conditional recursive-improvement regime in which the growth rate itself can compound. The latter is a serious tail scenario, not an assertion that a singularity will occur.

## Workflow translation

A directed acyclic task graph converts task-level success, retries, verification, human fallback, authority latency, external waiting, cost, and dependencies into expected total work, critical path, coordination overhead, reliability, and cost per verified outcome.

## Evaluation

- Rolling-origin hindcasts test prospective behavior rather than in-sample fit alone.
- Proper or scale-appropriate scores evaluate point and probabilistic forecasts.
- Controlled ablations remove one structural component at a time.
- Sensitivity analysis identifies assumptions that dominate the result.
- Triggers force recalculation when the observed path leaves its predictive envelope or the regime changes.

See the paper for derivations and `protocol/prompt.md` for the complete operational sequence.
