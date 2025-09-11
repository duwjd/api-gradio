_prompt = {
    "system_instruction": """
## 1. Analyze
- Carefully extract **textual**, **numerical**, and **tabular** information from the document.
- Do **not** alter facts or introduce external knowledge.
- Identify the key content elements from the document that are useful for building a coherent scenario.
- Analyze content in the **natural order of reading**, considering visual and structural flow.
- Distinguish between **actual content structure** and **stylistic formatting**. Do not treat short, decorative, or non-informative lines (e.g., slogans, captions, UI labels) as meaningful topics or subtopics unless they are contextually central.
- Ensure that **each major heading or clearly distinguished label** (e.g., bold titles, large font text, boxed or underlined labels) is treated as a potential `"title-main"` **only if it is followed by supporting content**. Do not include such headings as `"text-main"` within other scenes.

## 2. Organize Content
- Group extracted information into **logical topics**, based on semantic and thematic coherence.
- Each topic contains multiple **subtopics**, which will form the structure of the scenario's "scenes" and "sections".
- Preserve all original content. Avoid paraphrasing, summarizing, or duplicating information.
- Each `"scene"` in the final output must be based on **only one** `"main topic"`. Do **not** merge or blend multiple topics into a single scene.

## 3. Language Handling
- Preserve the **original language** of all extracted content (titles, descriptions, subtopics). Do **not translate** or alter original wording.
- For the generated **"script"** field:
  - If the **majority of the document content** (including titles, subtopics, and body text) is in **Korean**, write the script entirely in **Korean**.
  - If the **majority** is in **English**, write the script in **English**.
  - Do not mix full sentences from different languages within the script.
  - You may include proper nouns, short brand names, or phrases in another language within a sentence when they appear that way in the original content.
  - Avoid automatic fallback to English if Korean is dominant in the original content.

## 4. Template and Formatting Compliance
- Follow the JSON structure **exactly**. Use correct key names, data types, and nesting.
- Do **not** insert extra keys or elements.
- Each list (e.g., "sections", "text-extra", "title-extra") must match the required length.
- Final output must be enclosed in a valid `json` code block.
""",
    "prompt_1": """
**IMPORTANT**: Analyze the input data and fill the provided JSON template accordingly.

---

### 1. Information Structuring Rules

- Extract and organize the input content into **main topics** and their related **subtopics**.
- Each **main topic** should focus on a specific concept or section clearly supported by the document.
- Subtopics represent logically grouped elements under the main topic (e.g., features, usage, specifications, etc.).
- Preserve the **original grammar, structure, and language** of the input. **Do not paraphrase, summarize, or translate**.
- Reuse identical subtopics under multiple main topics **if relevant**, without changing wording.

---

### 2. Output Template Structure (JSON)

Fill the following fields **exactly as structured in the template JSON** for each `"scene"`:
- `"script"`: A video-ready script narrating the section’s content, written in the **dominant language** (Korean or English) from the document.
- `"title-main"`:  The headline/main subject for this topic. It should match the product name exactly as it appears in the document.  
- `"title-extra"`: Product specifications such as dimension or hashtags only. Maintain original grammar and syntax.  
- `"images"`: empty list as []
- `"section"`: Contains detailed product-related information. Each section includes:  
  -- `"text-main"`: Original description or detailed content about the product. Avoid repeating any information already present in `"title-extra"` or `"text-extra"`.  
  -- `"text-extra"`:Price of product. Typically a list or short notes. Do **not** duplicate data from `"title-main"` or `"title-extra"`.  
  -- `"image"`: empty value as "".
---

### 3. Scene Generation

- Each **"scene"** must represent a **single main topic** and its subtopics as specified in **Output Template Structure** rules.
- **"script"** should be a narrated script for a video based on **only one main topic** and its subtopics.
- Do **not combine** multiple main topics into a single scene.
- The script can incorporate discarded or background information from subtopics, but must remain logically consistent.
- The language of the script must **match** the dominant language of the document (Korean or English).  
  - If over 50% of the document content is in **Korean**, write the scene in **Korean**.
  - Otherwise, use **English**.
  - Do not mix languages in full sentences; short terms in a different language are allowed **within** a sentence.

---

### 4. General Constraints

- **Do not add extra keys** or modify the JSON structure.
- All required fields must be filled with valid, meaningful values.
- Use consistent and accurate formatting.
    
""",
}
