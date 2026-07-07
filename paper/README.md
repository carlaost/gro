# paper/

A short, readable paper digesting this work — problem, the metrics program, the negative result, the affordance gap, the GRO design, limitations, and next steps.

- **[`gro-paper.pdf`](gro-paper.pdf)** — the paper (5pp, A4).
- **`gro-paper.html`** — the source; the PDF is rendered from it.

It is a *digest*: where it summarises, the rest of the repository carries the full text (the complete GRO spec in [`../SPEC.md`](../SPEC.md), the metrics program in [`../metrics/`](../metrics/), the tournaments in [`../metrics/tournaments/`](../metrics/tournaments/)). The limitations section folds in the honest gaps from the author's Astera and SPRU research programs (validation, scale, trust-relocation, adoption).

## Regenerate the PDF

No LaTeX/pandoc needed — rendered with headless Chrome:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="paper/gro-paper.pdf" \
  "file://$PWD/paper/gro-paper.html"
```
