# Clean-Install Smoke-Test Report

**Package version:** 2.0.0  
**Deterministic record time:** 2026-07-28T16:00:00+00:00  

The wheel and source distribution were installed independently, each exposed a working CLI, and each produced byte-identical JSON and HTML forecast artifacts under the declared reproducibility environment.

## Results

- Wheel SHA-256: `5fb0b8bb137fd57377ec29f15a070d837e30d2a2ba77cafadf70a6292efde429`
- Source-distribution SHA-256: `dee7862e84c4e64e661acb98bca2901473110483fecb512dbcdd3691eb2fcbdc`
- Forecast JSON SHA-256: `47066db2b942f7c70334a354de07adbdae92fe8983539b7d23968869eaf087fe`
- Forecast HTML SHA-256: `bcee1222e18009863df7b72b3d58a0169f7b945602647326a025f79ac0f989cc`
- Wheel clean-install forecast: **passed**
- Source-distribution clean-install forecast: **passed**
- JSON equivalence: **byte-identical**
- HTML equivalence: **byte-identical**

> This record proves packaging and deterministic execution in the stated environment. It is not a security audit, peer review, or prospective forecasting validation.
