import gradio as gr
import google.generativeai as genai
import json
import os

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

SYSTEM_PROMPT = """You are a book cover quality inspector for BookLeaf Publishing.

COVER LAYOUT REFERENCE:
The cover has TWO sides — Front Cover (right side) and Back Cover (left side), with a thin spine in the middle.

FRONT COVER SAFE AREA RULES:
- There is a safe area inset approximately 3mm (printed) from the LEFT, RIGHT, and TOP edges of the front cover panel.
- VISUAL TEST for safe margin: Look at the gap between any text and the nearest edge. If the gap is very narrow — roughly the height of one line of small text or less — that is a margin violation. There should be a clearly visible, comfortable gap between all text and every edge.
- EXCEPTION — AUTHOR NAME ONLY: The author name is commonly placed near the top of the front cover. If the author name has a small but visible gap from the top edge, this is ACCEPTED. This exception does NOT apply to the book title or any other text.
- TITLE TEXT NEAR EDGES IS A VIOLATION: If the book title, subtitle, or any large display text starts very close to the top edge, or runs very close to the right or left edge of the front cover, this IS a safe margin violation (severity "minor"). 
  Example: A title like "Offline Sorrows" placed at the very top of the front cover with barely any gap, or words like "Online Ghosts" extending to near the right edge — these are violations because the title text has insufficient margin from the edge.
- The book title should ideally be placed with comfortable margins from the top, left, and right edges of the front cover panel.
- The BOTTOM approximately 9–10mm (roughly the bottom 8–10% of the front cover height) is RESERVED for the "Winner of 21st Century Emily Dickinson Award" badge strip. NO other text, author name, title, or design element should appear in this strip.

BACK COVER RULES:
- The back cover follows the same safe-area guide lines as the front — text must stay within the outermost 5% border on all sides.
- ACCEPTED LAYOUT: The "About the Book" body text commonly starts near the top of the back cover, just inside the safe-area guide line. This is NORMAL for BookLeaf covers — do NOT flag it unless the text literally touches or bleeds off the top edge of the image.
- "About the Author" section should be properly spaced from surrounding elements.
- BookLeaf Publishing logo typically appears at the bottom left, barcode at the bottom right.
- Only flag a back cover margin issue if text clearly falls within the outermost 5% strip (i.e., visually touching or extremely close to the physical edge).

CRITICAL CHECK (highest priority):
1. BADGE OVERLAP: Look at the very bottom strip of the FRONT COVER. 
   - The text "Winner of 21st Century Emily Dickinson Award" or similar award text BELONGS in the bottom zone — this is the badge itself. Do NOT flag this as an overlap.
   - What you ARE checking: does the AUTHOR NAME, BOOK TITLE, SUBTITLE, or any OTHER text or design element intrude into this bottom badge zone?
   - If only the award badge text is in the bottom zone, this is a PASS.
   - If the author name, title, or other text overlaps or is too close to the award badge text, this is a FAIL.
   - If the image shows ONLY the front cover (no back cover or spine visible), skip the back_cover_layout and text_border_spacing checks — mark them as PASS with description "Back cover not visible in image" and severity "none".
   - Short taglines or subtitles (e.g., "I Live and Write My Living", "Poems of Memory") positioned ABOVE the author name and ABOVE the badge text are acceptable — do not flag these unless they actually enter the bottom 5% badge zone.

SEVERITY RULES:
- "critical" — ONLY for badge overlap violations (text intruding into bottom badge zone)
- "minor" — for margin violations, spacing issues, slight alignment problems
- "none" — check passed cleanly

Do NOT mark safe margin or text spacing issues as "critical". These are "minor" issues that need review but are not showstoppers.

ADDITIONAL CHECKS:
2. SAFE MARGIN VIOLATIONS: Examine the FRONT COVER PANEL (not the full spread) and check each edge:
   - TOP edge: Is the book TITLE (not author name) positioned so close to the top edge that the gap is less than one line of small text? If yes, FAIL.
   - RIGHT edge: Does any title text extend so close to the right edge that the gap is very narrow (less than a character width)? If yes, FAIL.
   - LEFT edge: Same check for the left edge.
   REMEMBER: The full image shows back cover + spine + front cover. The front cover is the RIGHT HALF of the image. Check margins relative to the front cover panel edges, not the full image.
   IMPORTANT: The author name near the top edge gets a pass, but title text near ANY edge does NOT. Title text too close to the top or right edge is a genuine violation even with a tiny gap.
3. TEXT-TO-BORDER SPACING: On the back cover, does any text literally touch or bleed off the physical edge of the image? Text that is near the top but has any visible gap between it and the edge is NOT a violation. Apply the same 5% outer-strip rule as the front cover — only flag if text is within that outermost strip.
4. TEXT LEGIBILITY: Is all text clearly readable with no pixelation or blur?
5. IMAGE QUALITY: Is the overall image clear, high-resolution, and professional?
6. TEXT ALIGNMENT: Is text properly aligned and not crooked or misaligned?
7. BACK COVER LAYOUT: Is the back cover text (About the Book/About the Author) properly formatted? Only flag layout issues if text is outside the safe area guide lines (outermost 5% strip) or sections are missing entirely. Text starting near the top of the back cover within the safe area is an accepted BookLeaf layout — do NOT flag it.

RESPOND IN THIS EXACT JSON FORMAT AND NOTHING ELSE (no markdown, no code blocks, just raw JSON):
{
  "overall_status": "PASS" or "REVIEW_NEEDED",
  "overall_confidence": 0-100,
  "checks": {
    "badge_overlap": {
      "status": "PASS" or "FAIL",
      "confidence": 0-100,
      "description": "Brief description of finding",
      "severity": "critical" or "minor" or "none"
    },
    "safe_margin": {
      "status": "PASS" or "FAIL",
      "confidence": 0-100,
      "description": "Brief description",
      "severity": "critical" or "minor" or "none"
    },
    "text_border_spacing": {
      "status": "PASS" or "FAIL",
      "confidence": 0-100,
      "description": "Brief description",
      "severity": "critical" or "minor" or "none"
    },
    "text_legibility": {
      "status": "PASS" or "FAIL",
      "confidence": 0-100,
      "description": "Brief description",
      "severity": "critical" or "minor" or "none"
    },
    "image_quality": {
      "status": "PASS" or "FAIL",
      "confidence": 0-100,
      "description": "Brief description",
      "severity": "critical" or "minor" or "none"
    },
    "text_alignment": {
      "status": "PASS" or "FAIL",
      "confidence": 0-100,
      "description": "Brief description",
      "severity": "critical" or "minor" or "none"
    },
    "back_cover_layout": {
      "status": "PASS" or "FAIL",
      "confidence": 0-100,
      "description": "Brief description",
      "severity": "critical" or "minor" or "none"
    }
  },
  "author_name_detected": "Name found on cover or null",
  "author_name_position": "top/middle/bottom/bottom-edge",
  "title_detected": "Book title found or null",
  "issues_summary": ["List of specific issues found"],
  "correction_instructions": ["Step-by-step fix instructions for each issue"]
}

IMPORTANT:
- If ANY check has severity "critical", overall_status MUST be "REVIEW_NEEDED"
- If all checks pass with severity "none", overall_status is "PASS"
- If only "minor" issues exist, overall_status is "REVIEW_NEEDED"
- Be especially strict about badge overlap — this is the #1 issue BookLeaf faces
- For safe margin: flag as FAIL if text is clearly within the 5% border strip of the front cover panel. Do NOT suppress this flag — margin violations on title text are real issues that need correction.
- The cover image may show front cover only, or front + back + spine together. Analyze whatever is visible."""


def analyze_cover(image):
    if image is None:
        return "Please upload a book cover image.", "", ""

    try:
        response = model.generate_content(
            [
                SYSTEM_PROMPT,
                image,
                "Analyze this book cover for layout issues. Check all requirements carefully, especially the award badge overlap zone at the bottom. Respond ONLY with the JSON object, no markdown or code blocks.",
            ],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
        )

        result_text = response.text.strip()
        result = json.loads(result_text)

    except json.JSONDecodeError:
        return f"Error parsing AI response. Raw output:\n\n{result_text}", "", ""
    except Exception as e:
        return f"Error: {str(e)}", "", ""

    # Build status banner
    status = result.get("overall_status", "UNKNOWN")
    confidence = result.get("overall_confidence", 0)

    if status == "PASS":
        status_display = f"## ✅ PASS — Confidence: {confidence}%\nThis cover meets all BookLeaf publishing standards."
    else:
        status_display = f"## ⚠️ REVIEW NEEDED — Confidence: {confidence}%\nIssues detected that need attention before publishing."

    # Build check results
    checks = result.get("checks", {})
    check_lines = []
    for check_name, check_data in checks.items():
        icon = (
            "✅"
            if check_data["status"] == "PASS"
            else ("❌" if check_data["severity"] == "critical" else "⚠️")
        )
        label = check_name.replace("_", " ").title()
        check_lines.append(
            f"{icon} **{label}** ({check_data['confidence']}%) — {check_data['description']}"
        )

    checks_display = "\n\n".join(check_lines)

    # Build details
    details_parts = []

    author = result.get("author_name_detected")
    title = result.get("title_detected")
    position = result.get("author_name_position")

    if title:
        details_parts.append(f"**Book Title:** {title}")
    if author:
        details_parts.append(f"**Author:** {author}")
    if position:
        details_parts.append(f"**Author Name Position:** {position}")

    issues = result.get("issues_summary", [])
    if issues:
        details_parts.append("\n**Issues Found:**")
        for issue in issues:
            details_parts.append(f"- {issue}")

    corrections = result.get("correction_instructions", [])
    if corrections:
        details_parts.append("\n**Correction Instructions:**")
        for i, corr in enumerate(corrections, 1):
            details_parts.append(f"{i}. {corr}")

    details_display = "\n".join(details_parts)

    return status_display, checks_display, details_display


with gr.Blocks(
    title="BookLeaf Cover Validator",
    theme=gr.themes.Soft(primary_hue="red", secondary_hue="gray"),
) as app:
    gr.Markdown(
        """
    # 📚 BookLeaf — Book Cover Validation System
    
    Upload a book cover image to automatically check for layout issues, badge overlap violations, margin compliance, and quality standards.
    
    **How it works:** The system uses AI Vision to analyze the cover against BookLeaf's publishing specifications, with special focus on the "21st Century Emily Dickinson Award" badge placement zone.
    
    ---
    """
    )

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                label="Upload Book Cover",
                type="pil",
                height=500,
            )
            analyze_btn = gr.Button(
                "🔍 Analyze Cover", variant="primary", size="lg"
            )

            gr.Markdown(
                """
            **Supported formats:** PNG, JPG
            
            **What we check:**
            - ❌ Badge overlap (critical)
            - ⚠️ Safe margin violations
            - ⚠️ Text legibility & quality
            - ⚠️ Text alignment
            - ⚠️ Back cover layout
            """
            )

        with gr.Column(scale=1):
            status_output = gr.Markdown(label="Status")
            checks_output = gr.Markdown(label="Validation Checks")
            details_output = gr.Markdown(label="Details & Corrections")

    analyze_btn.click(
        fn=analyze_cover,
        inputs=[image_input],
        outputs=[status_output, checks_output, details_output],
    )

    gr.Markdown(
        """
    ---
    **Built by Achyuth Kumar P** | [GitHub](https://github.com/AK1-1/bookleaf-cover-validation) | Powered by n8n, Google Gemini, Airtable & Gmail
    
    *This is the interactive demo component. The full production system includes Google Drive monitoring, Airtable logging, and automated email notifications — see the GitHub repo for the complete n8n workflow.*
    """
    )

app.launch()