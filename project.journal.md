# Project Journal

Use this journal to track your progress each week. Write a short entry after each work session. This helps you stay on track and gives your instructor context when creating guides for you.

---

## Checkpoint 1: Planning and Scaffolding (Due April 16)

### What I did

> In helpers.py, I wrote 3 functions: load_raw(), clean_employers(), and load_clean(). load_raw() loads the original tab-separated CSV file from the USCIS website into a DataFrame. clean_employers() then cleans the dataset by renaming the long Excel headers, drops blank employers, coerces counts to numbers. load_clean() shortens the process by loading the cleaned data.

### What's next

> Completing my MVPs.

### Questions or blockers

> N/A.

---

## Checkpoint 2: Working MVP (Due April 28)

### What I did

> I created my business logic file, `search.py`, and moved the main database search work there. I added helper functions for industries, states, cities, employer search results, total approvals, top employers, and approvals by state. I also used `_build_where(filters)` so all of the search functions can reuse the same filtering logic instead of repeating the same SQL query conditions.

### What's next

> Finish the Flask pages, connect the quiz answers to the dashboard, and improve the visual design so the app is easier to present.

### Questions or blockers

> I needed to make sure the filters worked correctly when users selected multiple states or cities.

---

## Checkpoint 3: Final Polish and Presentation (Due May 2)

### What I did

> I polished the full OPT Pal user flow. The home page now explains what total H-1B approvals mean and why they relate to employer size. The quiz now supports multiple states and multiple cities, with cities grouped by state and alphabetized. The dashboard now shows matched employers, summary stats, bar charts, filter pills, and a 3D Globe.gl visualization with state labels, approval counts, Greenville as the starting point, and lighter arcs. I also fixed several display bugs, including raw Python lists showing in the filter line and the globe hover color getting stuck.

### What's next

> Practice the short demo, push the final changes to GitHub, and make sure the Render deployment updates correctly before presenting.

### Questions or blockers

> The hardest blocker was the 3D globe behavior. Hovering some parts of the globe caused a color overlay to get stuck, so I changed the hover behavior to update only the caption text and not force the globe materials to rerender.

---

## Additional Entries

Add more entries below as needed. Date each one.

### May 1

> Final polish session. I improved the explanation of total approvals, changed the city filter from a single dropdown to grouped multi-select checkboxes, made the dashboard filter display match the quiz style, adjusted the logo glow, improved the Globe.gl chart, restored hover captions, added top-state labels, and wrote a short presentation script. The project is ready for final testing and demo practice.
