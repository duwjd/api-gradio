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
- Subtopics must not be **reused across multiple topics**.
- There can be **multiple topics with the same title**, as long as the content they contain is **distinct**.
- **Preserve the original order** of subtopics and topics as they appear in the source document. Do **not shuffle** them.
- Preserve all original content. Avoid paraphrasing, summarizing, or duplicating information.
- Each `"scene"` in the final output must be based on **only one** `"main topic"`. Do **not** merge or blend multiple topics into a single scene.

## 3. Language Handling
- Preserve the **original language** of all extracted content (titles, descriptions, subtopics). Do **not translate** or alter original wording.
- For the generated **"script"** field:
  -- If the **majority of the document content** (including titles, subtopics, and body text) is in **Korean**, write the script entirely in **Korean**.
  -- If the **majority** is in **English**, write the script in **English**.
  -- Do not mix full sentences from different languages within the script.
  -- You may include proper nouns, short brand names, or phrases in another language within a sentence when they appear that way in the original content.
  -- Avoid automatic fallback to English if Korean is dominant in the original content.

## 4. Template and Formatting Compliance
- Follow the JSON structure **exactly**. Use correct key names, data types, and nesting.
- All fields (except "image" and "images") must be filled with meaningful, non-empty values.
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
- Do **not reuse the same subtopic** under different main topics.
- Maintain the **original order** of main topics and subtopics as they appear in the input document.
- Preserve the **original grammar, structure, and language** of the input. **Do not paraphrase, summarize, or translate**.
- Do not treat short or decorative lines (e.g., headings, slogans, or UI labels) as topics or subtopics **unless they are clearly supported by surrounding content**.
- Only extract topic titles that represent **meaningful sections** or logical groupings of related information.


---

### 2. Output Template Structure (JSON)

Fill the following fields **exactly as structured**:
- `"script"`: A video-ready script narrating the section’s content, written in the **dominant language** (Korean or English) from the document. This should be distinct for each `"scene"`.
- `"title-main"`: The main topic or section headline.
- `"title-extra"`: Subtitle or complementary information that clarifies or enriches the main topic. Follow the input's original syntax and wording.
- `"images"`: A list of integers indicating image indices relevant to this topic. Image indices must correspond to those provided in the "LIST OF IMAGES" section. Images must be valid and contextually related to the content.
- `"sections"`: Subtopics related to the main topic, each with:
  -- `"text-main"`: The main topic of the section. It should be a short, clear phrase that can serve as the section’s title.  
  -- `"text-extra"`: The **full body content** related to the **`"text-main"`** with preserved original structure. This includes descriptions, details, data, and anything associated with the section.
  -- `"image"`: An integer index of image relevant to this subtopic. Image index must correspond to those provided in the "LIST OF IMAGES" section. Image must be valid and contextually related to the content.
- Ensure all key names match the template JSON **exactly**. Do not create new keys or alter the structure.

---

### 3. Scene Generation
- The **first scene** should provide a **summary of the overall topic and subtopic** of the input document.
  -- This scene **does not contain** `"sections"` but gives a high-level overview.
  -- Assign the **most impactful image of the product**—the one that best conveys the core message of the document—to the `"images"` field for this scene.
- Each subsequent **"scene"** must represent a **single main topic** and its subtopics.
- Do **not merge** content from multiple main topics into one scene.
- Write the script in the dominant language of the source document:
  -- Use **Korean** if more than 50% of the document is in Korean.
  -- Use **English** otherwise.
  -- Do not mix full sentences from different languages; short proper nouns or terms in another language are acceptable.
- Avoid placing any `"text-main"` value that **duplicates or closely resembles any `"title-main"`** across scenes. These should be separated.
- Do not infer continuity across sections unless explicitly indicated by **shared styling, numbering, or grouping**. Visually separated titles or boxed content likely indicate new scenes.

---

### 4. Image Matching

- Match the most relevant cropped images (provided in the "LIST OF IMAGES") to each topic and subtopic.
- Insert the indices of matching images into the `"images"` field as a list of integers (e.g., `[1, 4, 6]`).
- The order of image indices should reflect **relevance or importance** to the associated content.
- If the "LIST OF IMAGES" contains `N` images, valid indices are integers from `0` to `N-1`.
- Double-check all image references to ensure they are **within bounds**.
- `"images"` must **not be empty** when images are provided.

---

### 5. General Constraints

- **Do not add extra keys** or modify the JSON format.
- All fields must be completed with valid, non-empty values.
- Maintain accurate formatting and follow structural requirements.
""",
}
