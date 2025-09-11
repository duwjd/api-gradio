_prompt = {
    "system_instruction": """You are a helpful assistant.""",
    "prompt_1": """
Extract all visible information from the image in the format of the JSON example below.

Specifically:

- Detect and list all visible cars in the image under the `object` section. For each car:
  - `year`: The year of the car, if visible. If not visible, leave as an empty string.
  - `name`: Full name including manufacturer and model only (e.g., "Hyundai Sonata"). Remove any trim level or variant words like "Hybrid", "TrailSport", "Sport", "XLE" etc. **Always try to identify the exact model name (e.g., "Honda Accord") based on the vehicle’s visual appearance and design details, using common car databases and known designs.** Only if you are completely unsure of the model, fallback to manufacturer + type (e.g., "Honda SUV"). If even the manufacturer is not clear, just include the general type (e.g., "SUV" or "Sedan").
  - `color`: Select the closest color from the **color_list** that best matches the visible color of the car. If the color is not listed, use the closest match.
    - **color_list**: [red, blue, green, black, white, silver, gray, yellow, orange, gold, beige, pearl, azure]

- Extract all visible text and include under the `sections` array.
  - Escape sequences such as `\\n`, `\\t`, `\\r`, or `\\\\` must not appear in any output field. Normalize the text to a flat, single-line format.
  - Each entry should include:
    - `text-main`: One continuous segment of text. If parts of the segment differ in font size or visual style (e.g., bold, italic, font-size), split them into separate `text-main` entries. Elsewhere, keep them as one segment.
    - `position_ratio`: x/y position normalized to a 9:16 canvas
    - `font-size-ratio`: Height of the text as a ratio of the image height
    - `font-color`: Text color in hex
    - `bold`, `italic`: Whether the text is bold or italic
  - After computing all `"x"` positions, linearly normalize them so that the leftmost `"x"` becomes 0 and the rightmost becomes 0.4 (maintaining relative distance).
  - Align the text to the left side of the image, and not to overlap each other.
  - Finally, **sort the extracted text entries from top to bottom (based on y-position) to match the natural reading order.**
  - **If the text entries extend beyond the bottom of the canvas, start a new vertical column at `"x"=0.5, "y"=0.1` and arrange the remaining text top-to-bottom again. Repeat as needed for overflowing text.**

**Make sure to extract all visible text and objects from the image.**
**Output valid JSON only, wrapped in triple backticks (`).**
**Assume a 9:16 virtual canvas for all coordinates.**

JSON example:
```json
[
    {
        "scene": {
            "sections": [
                {
                    "text-main": "text extracted from the image",
                    "position_ratio": {
                        "x": float,
                        "y": float
                    },
                    "font-size-ratio": float,
                    "font-color": "#000000",
                    "bold": boolean,
                    "italic": boolean
                },
                {
                    "text-main": "text extracted from the image",
                    "position_ratio": {
                        "x": float,
                        "y": float
                    },
                    "font-size-ratio": float,
                    "font-color": "#000000",
                    "bold": boolean,
                    "italic": boolean
                },
                {
                    "text-main": "text extracted from the image",
                    "position_ratio": {
                        "x": float,
                        "y": float
                    },
                    "font-size-ratio": float,
                    "font-color": "#000000",
                    "bold": boolean,
                    "italic": boolean
                }
            ],
            "object": [
                {
                    "year": "the year of the car",
                    "name": "an object name",
                    "color": "color of the object"
                }
            ]
        }
    }
]
```
""",
    "prompt_image": """
Create a new commercial like scene featuring the same number of visible cars with no living things, no visible text or digital elements.
The car should be fully visible within the frame.
It's okay if natural elements are present in the environment.
""",
}
