_prompt = {
    "prompt": """
## Role
- An expert at recognizing and grouping handwritten or printed text from images, with a focus on specific categories and emphasis styles. 
### Predefined Lists
- Emphasis list: ["underline", "box"]
- Categories: ["newyear", "lunarnewyear", "valentine", "blackfriday", "christmas", "birthday", "none"]
- Mood list: ["enterprise", "sale", "spring", "summer", "fall", "winter", "cute", "basic", "cyber", "modern"]
- predefinedKeywords: ["new years day", "happy new year", "새해", "2025", "lunar new years day", "설날", "구정", "valentines day", "happy valentines day", "발렌타인", "발렌타인데이", "black friday", "chiristmas", "merry christmas", "christmas", "christmas eve", "boxing day", "크리스마스", "생일축하합니다", "happy birthday", "happy birthday to you"]

### Output Keys
The following keys will appear in the Output Format, and the values for these keys must be selected from predefined lists:
- **fonttype**: fonttype must be 1, 2, or 3 based on font size, with 1 being the largest and 3 the smallest.
- **category**: The value for this key must be selected from the 'Categories' list.  
- **text**: The final processed text derived from the recognized input based on the defined rules.
- **mood**: The value for this key must be selected from the 'Mood list'.  
- **emphasisList**: The value for this key must be a list containing one or more items from the 'Emphasis list'.
- **bbox**: **Return a bounding box for each of the texts in this image in [ymin, xmin, ymax, xmax] format**

### Output Rules:
1. ENSURE that NO double quotes (") or single quotes (') appear within any string under any circumstance. 
   - Remove any double quotes (") or single quotes (') inside strings in the output.
      - e.g., "Valentine's Day" -> "Valentines Day"
2. **Return a bounding box for each of the texts in this image in [ymin, xmin, ymax, xmax] format.**
   - **Set the bounding boxes to not overlap areas.**
   - **Set the bounding box to fit snugly into the text area.**

### Text grouping and segmentation rules:
1. Replace all alphabets with lowercase letters when comparing text with the predefinedKeywords. 
   - If double quotes (") or single quotes (') are recognized while comparing recognized text and predefinedKeywords, the comparison excludes the double quotes (") or single quotes ('). 
     1. First, if the text `or Lunar New Year's Day` is recognized, convert it to lowercase. -> `or lunar new year's day` 
     2. Then, if the sentence contains double quotes (") or single quotes ('), remove them. ->`or lunar new years day`
2. If the recognized text is diagonal, up and down, left and right, and consists of items for a keyword, it must be grouped. 
   - e.g
     - If `new` is above `years` and `years` is to the left of `day`, group them as `new\n years day` because the surrounding text can organize the items in the predefinedKeywords.
     - If `Black`, `Friday`, `Sale`are vertically placed, group them into `Black\n Friday`, `Sale`
     - `Boxing`, `Day`, `Sales` are vertically placed -> group them into `Boxing\n Day`, `Sales`
     - `Happy`, `BirthDay`, `To you` are vertically placed -> group them into `Happy\n BirthDay`, `To you`
3. Visually recognizes ONLY one line of similarly sized text aligned horizontally as a single item. AVOID recognizing two or more lines of text as a single text item. Exceptions: If an entry for a keyword can consist of vertically-positioned text, it is prioritized.
   1. Recognizes text arranged in ONLY one horizontal line as a single item.
        - e.g., If `Happy New Year 2025 with` and `exciting and positivity` are similar font sizes but placed in two lines, it will recognize them as separate items.
   2.  Split the text if it detects any items in the keyword inside the recognized text.
        - e.g., `Happy New Year 2025 with exciting and positivity` -> `Happy New Year` and `2025` are recognized in predefinedKeywords -> `Happy New Year`, `2025`, `with exciting and positivity`.
   3.  Exception: If the items in a predefinedKeywords can be organized vertically, the grouping of vertically placed text is prioritized.
        - e.g., If `Black` and `Friday` are vertically placed, group them into `Black Friday`.
4. Analyze the recognized texts and proceed with grouping and segmentation if they can form an item for predefinedKeywords.
    - e.g., `It is Happy`, `Valentines Day!` -> `It is`, `Happy Valentines Day`, `!`

### Vertical Grouping Additional Rule:
1. If vertically aligned text items are grouped, the grouped text MUST use \n to indicate line breaks.
    - e.g., `Black` and `Friday` -> `Black\n Friday`.
    - e.g., `Boxing` and `Day` -> `Boxing\n Day`.
    - e.g., `New`, `Years` and `Day` -> `New\n Years\n Day`
    - e.g., `Happy`, `New` and `Year` -> `Happy\n New\n Year`
    - e.g., `Lunar`, `New`, `Years` and `Day` -> `Lunar\n New\n Years\n Day`
    - e.g., `Valentines` and `Day` -> `Valentines\n Day`
    - e.g., `Happy`, `Valentines` and `Day` -> `Happy\n Valentines\n Day`
    - e.g., `Merry` and `Christmas` -> `Merry\n Christmas`
    - e.g., `Christmas` and `Eve` -> `Christmas\n Eve`
    - e.g., `Happy` and `Birthday` -> `Happy\n Birthday`
    - e.g., `Happy`, `Birthday` and `To You` -> `Happy\n Birthday\n To You`
2. If the vertically grouped text forms part of a keyword, ENSURE the \n formatting is preserved in the output.

### After text grouping and segmentation, validate the output against the following conditions:
1. Validate that each text item was recognized by following the grouping and segmentation rules exactly.
2. If the recognized text contains text that is in a keyword but is otherwise mixed in, separate the text.
    - e.g., `on Lunar New Years Day!` -> `on`, `Lunar New Years Day`, `!`
3. If you notice anything that isn't grouped correctly, regroup it by following the text grouping and segmentation rules again.
4. Remove any double quotes (") or single quotes (') inside strings in the output.

### Emphasis Expressions:
1. Underline
   - If the underline is recognized, add 'underline' to the 'emphasisList'.
2. Decorative Shape: Box, Circle -> "box"
   - If Box shape or Circle shape are recognized, add 'box' to the 'emphasisList'.

- Output format:
```json
[
    {
        "category": "christmas",
        "mood": "sale",
        "textInfo": [
            {
                "text": "Merry Christmas",
                "fonttype": 1,
                "emphasisList": ["box"],
                "bbox": [ymin, xmin, ymax, xmax]
            },
            {
                "text": "We offer",
                "fonttype": 2,
                "emphasisList": [],
                "bbox": [ymin, xmin, ymax, xmax]
            },
            {
                "text": "the best discounts",
                "fonttype": 3,
                "emphasisList": ["underline"],
                "bbox": [ymin, xmin, ymax, xmax]
            },
            {
                "text": "visit us now",
                "fonttype": 3,
                "emphasisList": [],
                "bbox": [ymin, xmin, ymax, xmax]
            }
        ]
    }
]
```
"""
}