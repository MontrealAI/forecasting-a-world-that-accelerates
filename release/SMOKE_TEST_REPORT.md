# Clean-Install Smoke-Test Report

**Package version:** 2.0.0  
**Deterministic record time:** 2026-07-28T16:00:00+00:00  

The wheel and source distribution were installed independently, each exposed a working CLI, and each produced byte-identical JSON and HTML forecast artifacts under the declared reproducibility environment.

## Results

- Wheel SHA-256: `43842de54d1532ff5307d116b95f1c2f74cb52bef63a3b36c87e674b263cb152`
- Source-distribution SHA-256: `d07ac114e884eb6a2f1f89ebd7a1907f712d4310c75b6c0ead1535b9957b9052`
- Forecast JSON SHA-256: `6ea7880d6a97838a7ffce1185b2043e5d88d3b843bdff8a752c120de4c779d2f`
- Forecast HTML SHA-256: `7ac424232c17cce100ff20b0863b9a02195bbec8545fae49e0e27381a01566ac`
- Wheel clean-install forecast: **passed**
- Source-distribution clean-install forecast: **passed**
- JSON equivalence: **byte-identical**
- HTML equivalence: **byte-identical**

> This record proves packaging and deterministic execution in the stated environment. It is not a security audit, peer review, or prospective forecasting validation.
