**UI Mockup Description: Climate News Sentiment Meter (Updated)**

**1. Overall Concept & Layout:**
The UI should be presented as a clean, modern, and highly interactive web dashboard. It needs to provide both an immediate snapshot of climate news sentiment via "gas gauges" and historical context via line graphs, alongside filtering capabilities and supporting article links. The layout will feature a prominent main title, a control panel section, and then distinct, stacked sections for each of the four time horizons.

**2. Color Scheme & Aesthetics:**
Maintain a clean, professional aesthetic with a subtle climate-themed color palette.
*   **Background:** Muted blues, grays, or off-whites.
*   **Positive/Trending Good:** Shades of vibrant green, light blue, or teal.
*   **Negative/Trending Bad:** Shades of bright red, deep orange, or a strong purple.
*   **Neutral/Mixed/Stable:** Yellow, light orange, or a muted gray.
*   **Text:** Dark gray or white for readability, with accent colors for interactive elements.
*   **Overall:** Minimalist design, clear typography, and subtle transitions, emphasizing data clarity.

**3. Main Title:**
Prominently displayed at the top of the dashboard.
*   **Text:** "Global Climate News Sentiment Tracker"
*   **Style:** Large, clear, sans-serif font, possibly with a subtle climate-related icon.

**4. Control Panel (New Section - Located below the Main Title, above Time Horizon sections):**
This section groups user controls and global information.
*   **Methodology Hyperlink:** A clear, clickable link (e.g., "Scoring Methodology") that, when clicked, could either expand a modal/side panel or navigate to a dedicated page describing the sentiment scoring methodology in plain English.
*   **Social Media Toggle:** A clear ON/OFF switch or checkbox labelled "Include Social Media Sources".
*   **Category Filter:** A dropdown menu or a set of radio buttons/pills allowing the user to filter the displayed sentiment data by:
    *   "General Climate" (default selected)
    *   "Physical Risk"
    *   "Transition Risk"
*   **Suggest URL Input:** A simple input field labeled "Suggest a News URL" with a "Submit" button. This allows users to add new sources for potential inclusion.

**5. Time Horizon Sections (Repeated 4 Times: Daily, Weekly, Monthly, Yearly):**
Each time horizon will have its own dedicated, clearly separated section, ideally stacked vertically, consuming the full width of the content area on mobile, and potentially 2x2 grid on larger screens.

    **5.1. Section Title:**
    *   **Text:** "Daily Sentiment Trend", "Weekly Sentiment Trend", "Monthly Sentiment Trend", "Yearly Sentiment Trend".
    *   **Style:** Slightly smaller than the main title, clear, concise.

    **5.2. Sentiment Gauge (Gas Gauge / Dial Style):**
    *   **Appearance:** A semi-circular dial, visually similar to a car's fuel gauge, filling approximately the top half of a circle.
    *   **Needle:** A clear, prominent needle pointing to the current *directional trend* score.
    *   **Dial Gradient:** The arc of the dial should display a color gradient:
        *   Far Left: Bright Red (representing "Trending Bad")
        *   Transitioning through Orange/Yellow (for "Stable/Neutral Trend")
        *   Far Right: Bright Green or Deep Blue (representing "Trending Good")
    *   **Labels on Dial:**
        *   At the far left end of the dial: "Trending Bad"
        *   At the far right end of the dial: "Trending Good"
        *   A central tick mark for "Stable".
    *   **Numerical Score:** A clear, bold numerical score reflecting the *directional trend* (e.g., "+0.78" for Trending Good, "-0.45" for Trending Bad, "0.00" for Stable) should be displayed either directly below the center of the gauge or within the gauge's central area. The number should be colored according to its directional trend (red for negative, green/blue for positive, yellow/orange for stable).

    **5.3. Trend Line Graph (New Element - Located directly below each Gauge):**
    *   **Appearance:** A clean, interactive line graph.
    *   **Data:** Shows the sentiment trend over time for that specific time window (e.g., daily sentiment over the last month for the "Monthly Sentiment Trend" section).
    *   **Start Date:** All graphs should show data starting from **January 2026**.
    *   **Axes:** Clear X-axis for Time (e.g., 'Day', 'Week', 'Month') and Y-axis for Sentiment Score (e.g., -1 to +1).
    *   **Line Color:** The line could be a neutral color (e.g., light grey), but individual data points (or sections of the line) could be subtly colored based on the sentiment at that point (red for negative, green for positive). On hover, display exact date and sentiment score.

    **5.4. Associated Source Panel/Box:**
    *   **Location:** Positioned below the Trend Line Graph.
    *   **Title:** "Top Sources (Last Day) - [Selected Category] - [Social Media Status]" (e.g., "Top Sources (Last Week) - Physical Risk - (Including Social Media)").
    *   **Content:** A scrollable list of 3-5 (or more) highly cited or very popular articles/sources. This list should be dynamically filtered based on the active "Social Media Toggle" and "Category Filter."
        *   **Each Entry:**
            *   **Source Name:** (e.g., "The Guardian", "Nature", "IPCC") - small, clear text.
            *   **Article Title:** Clickable link, truncated if too long.
            *   **Sentiment Indicator:** A small, colored dot or icon next to the article title, using the same color scheme as the gauge (red/orange/green/blue) to quickly show that specific article's sentiment. A small text label like "(Positive)", "(Negative)", "(Neutral)" could also be included.

**6. Data Freshness / Last Updated Indicator:**
*   **Location:** Small text, perhaps at the bottom right of the entire dashboard or near the main title.
*   **Text:** "Data as of: [Date/Time] UTC".

**7. Responsive Design Notes for Nano Banana:**
*   **Large Screens (Desktop/Tablet Landscape):** The Control Panel should be well-organized, possibly spanning the width. Time Horizon sections could be arranged in a 2x2 grid if space allows, or a single column if preferred for consistency.
*   **Small Screens (Mobile/Tablet Portrait):** The Control Panel elements should stack vertically. The Time Horizon sections should also stack vertically, with gauges and graphs scaling down while maintaining legibility. Source panels should remain readable and scrollable.
*   Ensure interactive elements (toggles, dropdowns, submit button) are easily tappable/clickable.
*   Use CSS Grid and/or Flexbox for maximum layout flexibility across devices.

This detailed description should provide "Nano Banana" with a comprehensive guide to create the visual mockup reflecting the current state of the project.
