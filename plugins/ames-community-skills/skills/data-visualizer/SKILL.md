---
name: data-visualizer
description: Render charts and graphs from data inline or from file attachments
metadata:
  author: Osaurus
  version: "1.0.0"
  category: productivity
  keywords: "chart, graph, plot, visualize, bar, line, pie, data, table, csv"
---

When the user's message contains data suitable for visualization:

## Choosing the right path

**If the data is in a file attachment:** call the `render_chart` tool.
Pass the full raw file content in the `data` field and use `xColumn` /
`series` to specify which columns to plot. The tool handles all parsing
and downsampling — you never need to format individual data points. Example:
```
render_chart(
  data: "<full raw CSV/TSV/JSON content>",
  format: "csv",
  chartType: "line",
  xColumn: "Month",
  series: ["Revenue", "Expenses"],
  title: "Monthly Financials"
)
```

**If the data is small and inline** (pasted table, computed values, fewer
than ~50 data points): emit a ```chart fenced block with the full spec:
```chart
{
  "chartType": "line",
  "title": "...",
  "categories": [...],
  "series": [{ "name": "...", "data": [...] }]
}
```

## Chart type selection
- **column / bar**: comparisons between categories
- **line / spline**: trends over time or ordered sequences
- **area / areaspline**: trends where cumulative volume matters
- **pie**: proportions (use only with ≤8 slices)
- **scatter**: correlations between two numeric variables
- **bubble**: correlations with a third size dimension
- **gauge**: single KPI value with a target range
- **waterfall**: cumulative effect of sequential values

## Quality guidelines
- Always set a meaningful `title`
- Set `tooltipSuffix` when data has units (USD, %, ms, kg, etc.)
- Use `stacking: "percent"` for part-to-whole comparisons across categories
- Keep series count ≤ 8 for readability
- For time series, put dates/times as `categories` on the x-axis