# Logistic Lab

A complete, offline-capable learning experience based on the supplied 68-slide
logistic-regression lecture. Follow the professor’s penguin examples, manipulate
scores and probabilities, investigate loss and gradients, and use the final
assessment to find concepts to revisit.

## Run

No package installation, API keys, accounts, backend, or database is required.
Use the existing checkout; cloud tasks are already isolated, so do not create a
Git worktree unless the user explicitly requests one.

```bash
cd /workspace/cs3
python3 -m http.server 8000 --bind 0.0.0.0
```

Open the server in a browser, or open `index.html` directly from disk. Every
essential asset and dataset is local. Progress and written reflections use browser
storage when available; clearing browser storage clears that progress.

## A single downloadable lesson

```bash
python3 scripts/build.py
```

The generated `dist/logistic-lab.html` contains all lessons, scripts, styles,
penguin data, all 68 slide images, and the original PDF. Open it in a browser
without a server or internet connection. The printed view contains the active
lesson; use the browser’s Print / Save as PDF function to print it.

## Verify

```bash
node --test tests/math.test.js
python3 scripts/build.py
```

The mathematical tests check the lecture’s worked numbers, numerical versus
analytical gradients, simultaneous updates, stable extreme-score losses,
confusion metrics, threshold ties, and reproducible full-data training.

The browser smoke test uses Playwright in an environment that already provides
its Python package and Chromium:

```bash
python3 tests/browser.py
```

It starts its own temporary server, checks all chapters and key interactions,
grades the assessment, tests mobile navigation, and checks the standalone version
with networking disabled after its initial load. The managed test browser blocks
file URLs; opening directly from disk is supported by the artifact but is not
verified in that browser.
It is optional for normal use of the site. There are no runtime dependencies to
install.

## What is taught

1. Feature-based numerical prediction, residuals, MSE/MAE, OLS, parameter-space
   search, and gradient descent step size.
2. Binary labels, sign decisions, flat classification error, and the sigmoid.
3. Penguin features, labels, mass overlap, and the limitations of binary OLS.
4. Score, probability, odds, log odds, and coefficient interpretation.
5. Recorded-class likelihood, log loss, confidence, and calculation practice.
6. Derivatives, row and average gradients, and simultaneous updates.
7. Training versus held-out evaluation, with an actual penguin-data fitting lab.
8. Decisions, confusion counts, accuracy, precision, recall, and cutoff changes.
9. The lecture’s Turing-test and modern authorship-detection examples, FNR, and
   limits of benchmark interpretation.
10. A 12-item final assessment, targeted review, teach-back challenges, and a
    self-explanation checklist.

Includes 22 embedded intuition checks with answer-specific explanations, a
formula field guide, and a slide-to-concept map. Additional examples are labeled.

## Source distinctions

- `assets/lecture.pdf` is the compressed lecture supplied by the user. The 68
  slide images are rendered from that PDF. Its content belongs to its respective
  authors; this repository does not relicense that material.
- `data/penguins.js` contains the 274 nonmissing Adélie/Gentoo body masses and
  species from the public [Palmer penguins dataset](https://github.com/allisonhorst/palmerpenguins),
  retrieved from `inst/extdata/penguins.csv`. Dataset: Allison Horst, Alison Hill,
  and Kristen Gorman; original observations: Gorman, Williams, and Fraser (2014).
  Palmer penguins data are distributed under CC0.
- The live fitting lab uses a Fisher–Yates shuffle driven by a 32-bit LCG with
  seed 42 (`state = 1664525 * state + 1013904223 mod 2^32`), then selects the first
  191 rows as training and the other 83 as test. This is not a claim to recreate
  the professor’s undisclosed split. The lecture’s reported coefficients and
  confusion matrix appear separately.
- The authorship-detection values are reported as shown in slides 67–68, not
  independently verified benchmarks. Missing protocol details are flagged.

## Files

`content.js` contains the learning narrative, quizzes, and assessment. `math.js`
contains reusable numerical functions. `app.js` renders the lessons and SVG
experiments. `styles.css` provides responsive layouts. `scripts/build.py` creates
the standalone file with Python’s standard library.
