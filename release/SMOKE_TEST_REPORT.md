# Clean-Install Smoke-Test Report

**Package version:** 2.0.0  
**Deterministic record time:** 2026-07-28T16:00:00+00:00  

The wheel and source distribution were installed independently, each exposed a working CLI, and each produced byte-identical JSON and HTML forecast artifacts under the declared reproducibility environment.

## Results

- Wheel SHA-256: `c98d68c1e4789bd1156689c8f80d8de85a682aa9563a6f4f25de400d6284e16a`
- Source-distribution SHA-256: `77af04168889b87992b030eec4aafe88402edf1a89a3e7773ad241199cf49c66`
- Forecast JSON SHA-256: `fe1a1a016d7840b2099ea05f99dfd8b3896c89c47b6bf21bfbf979e29e0a00e7`
- Forecast HTML SHA-256: `4e81380deff4262c882b91641186b754115e759e769410e57db992cb98c5cf2f`
- Wheel clean-install forecast: **passed**
- Source-distribution clean-install forecast: **passed**
- JSON equivalence: **byte-identical**
- HTML equivalence: **byte-identical**

> This record proves packaging and deterministic execution in the stated environment. It is not a security audit, peer review, or prospective forecasting validation.
