# The Stack Overflow Cliff

**Stack Overflow got 969 new questions in September 2026. At its peak, in May 2020, it got 186,376.**

An interactive dashboard on what happened to public coding Q&A after ChatGPT, with a focus on the tools data analysts use every day: Python, pandas, SQL, Excel and Power BI.

**Live dashboard:** https://YOUR-USERNAME.github.io/stack-overflow-cliff/ · **Video walkthrough:** [assets/demo.mp4](assets/demo.mp4)

![Dashboard](assets/dashboard.png)

## What the data shows

- **It's speeding up, not levelling off.** Year on year, monthly questions fell 54%, 59%, 74%, then 81% (Sep 2025 → Sep 2026).
- **All of 2025 had 109,019 questions,** fewer than May 2020 on its own.
- **Code-first tools fell first.** Python, pandas and SQL all dropped below half of their 2021 level by Q2 2023, and pandas has 0.6% left. Power BI held out longest: it was still above its 2021 level in Q1 2023 and only fell below half in Q4 2024, six quarters after Python, pandas and SQL.
- **What it doesn't show:** where the questions went, or that people stopped coding. The timing points at AI chats, but that's an interpretation, not something this data proves.

## How it works

1. **Data:** `scripts/fetch_data.py` calls the Stack Exchange API once per month for the whole site and once per quarter for each tag, 280 requests in total, and writes the counts to `data/`.
2. **Calculations:** `js/app.js` derives every figure on the page from those raw counts: peaks, year-on-year change, indexes to the 2021 average, share of all questions and the quarter each tag crossed 50%, 25% and 10%. Nothing is typed in by hand.
3. **Charts:** every chart is drawn as SVG with plain JavaScript, with no charting library, and redraws to fit any screen size.

**Checks:** the 2020 total (1,854,929) matches an independent Stack Exchange Data Explorer analysis (about 1.86M), and every figure and table cell has been cross-checked against the raw data.

## What's on the dashboard

- **KPI strip:** latest month, peak, change since ChatGPT, 2025 total, each with a sparkline
- **Monthly trend** with a linear / log toggle and the ChatGPT launch marked
- **Questions per year**, with May 2020 drawn as a reference line
- **Year-on-year change** for every month since 2019
- **Heatmap** of every month, 2018–2026
- **Small multiples** for python, pandas, sql, excel and powerbi, indexed to 2021
- **Share of all questions** per tag, showing which tools fell slower than the site
- **When each tag fell:** the quarter each crossed 50%, 25% and 10% of its 2021 level
- Click a tag to highlight it across the toolkit charts, hover anything for exact numbers
- Light and dark mode, works on phones
- No frameworks or build step: plain HTML, CSS and hand-drawn SVG

## Run it locally

Just open `index.html` in a browser. The data ships as `data/so_counts.js`, so it works straight from disk with no server.

## Refresh the data

```bash
pip install -r scripts/requirements.txt
python scripts/fetch_data.py
```

This pulls Jan 2018 up to the last complete month and rewrites everything in `data/`. A full run is about 280 requests. The API allows 300 requests a day per IP without a key, so run it at most once a day, or register a free key at [stackapps.com](https://stackapps.com/apps/oauth/register) and set `STACKEXCHANGE_KEY` to get 10,000 a day. Keep `--start` at 2021 or earlier, because the dashboard indexes everything to the 2021 average.

## Put it online (free, GitHub Pages)

1. Create a public repo called `stack-overflow-cliff` and push this folder to it.
2. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → `main` / `(root)` → Save.**
3. After a minute it's live at `https://YOUR-USERNAME.github.io/stack-overflow-cliff/`.
4. Replace `YOUR-USERNAME` with your GitHub username in this README and in the `og:image` line of `index.html`, so link previews on LinkedIn show the right image.

## Method and caveats

- Source: Stack Exchange API v2.3, `/questions?filter=total`, filtered by creation date. One call per month for the whole site, one per quarter per tag. Pulled 29 Oct 2026.
- The API only counts questions that still exist, so deleted questions are excluded and older months read slightly low.
- A question can have several tags, so tag counts overlap and don't add up to the site total.
- "Last four quarters" means Q4 2025 to Q3 2026, compared with the 2021 quarterly average.

## Project structure

```
index.html              page markup
css/styles.css          design tokens, layout, light/dark themes
js/app.js               calculations, SVG charts, tooltips, tag filter
data/so_counts.json     raw counts (also so_counts.js for loading from disk)
data/*.csv              the same data as CSV, for Excel / Power BI
scripts/fetch_data.py   re-pulls the data from the Stack Exchange API
assets/                 screenshot, demo video, social images, self-hosted fonts
```

## Credits and licences

- Code: MIT licence (see `LICENSE`).
- Data: Stack Exchange, licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This project isn't affiliated with Stack Overflow.
- Fonts: Big Shoulders Display, Instrument Sans and JetBrains Mono, all under the SIL Open Font License 1.1.

Made by **Abdullah Butt**, Data Analyst, London · [LinkedIn](https://linkedin.com/in/abdullahb022)
