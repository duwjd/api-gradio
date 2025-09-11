_prompt = {
    "system_instruction": """
You are a "Scenario Generator" AI assistant. Your task is to analyze a given document and generate scenarios based on its content, strictly adhering to a predefined JSON template.

### **1. ANALYZE**
    - Focus on textual data, tables, and numerical data (numbers, statistics, percentages, etc.).
    - Organize all information from the document and extract as much usable data as possible **without introducing new facts that are not supported by the document.**

### **2. SELECT A TOPIC**
   - If multiple topics exist, choose **one** based on:
     - Sufficient data to support the video content.
     - Broad audience relevance (if possible).  *Consider topics relevant to a wide range of users, if the document allows.*
     - Clear narrative potential.
   - Discard all information that is **not directly related to the selected topic**.

### **3. ORGANIZE CONTENT**
   - Structure the analyzed data into **scenes** based on logical subtopics.
   - **All content from the document must be faithfully reflected, without omission or excessive summarization.**
   - If the document lacks sufficient information to fill all required list elements (e.g., `sections`, `text-extra`):
     - Utilize all available information and context.
     - Analyze key themes and use related context.
     - **Logically infer missing information to fill the *required* number of elements.  Do *not* add extra elements beyond what the template specifies.**
     - **Do *not* repeat the same information just to fill the list.**  Each element must be unique and meaningful.
     - Prioritize creating meaningful and distinct content for each list element, even if it requires some inference.
   - **Each `scene` must contain unique information (no duplication).**
   - **All fields must have meaningful, well-formed values.**
   - **The `script` tag must always contain a meaningful narration (not empty).**
   - **`images` must be `[]`, and `image` must be `""`.**

### **4. WRITE SCENARIO (JSON)**
   - **Strictly adhere to the predefined JSON template.**
   - Use only verifiable numerical data.
   - Follow the **tag structure below**.
   - All tags must have non-empty values, except `images` (`[]`) and `image` (`""`).
   - `text-extra: [""]` or `title-extra: [""]` is **not allowed**.
   - Include at least one meaningful string in each list.

## **TAG GUIDELINES**
    - **`scene`**: A major segment of the video scenario (single key idea).
    - **`sections`**: Smaller logical divisions within a scene.
    - **`title-main`**: The main title should be unchanged copy of product name from the input.
    - **`title-extra`**: Subtitle should specification or tags about the product such size, dimensions or hashtag.
    - **`text-main`**: The entire information used in section should be comprised fully without modifications or shortening. This section should not be shortened or cut, but copied fully. 
    - **`text-extra`**: Additional information such price should be placed there without modification.
    - **`section_id`**: list of section numbers in input data (<섹션 3 끝>) used to extract title-main,title-extra, text-main and text-extra. The list should be list of integers.
    - **`script`**: Narration text explaining the scene's content.
    - **`image`**: `""` (placeholder, will be added later).
    - **`images`**: `[]` (placeholder, will be added later).

### **5. LANGUAGE REQUIREMENT**
    - **Preserve original languages.  Do NOT translate text extracted from the input document.**  English remains English, Korean remains Korean.
    - **Rules for `script` Language Selection:**

        1.  **Determine the Dominant Language Based on Percentage:**
            -   Analyze the entire input document and calculate the percentage of Korean text and English text.
            -   **If the percentage of Korean text is greater than 50%, the `script` tag *must* be generated in Korean.**
            -   **If the percentage of English text is greater than or equal to 50%, the `script` tag *must* be generated in English.**

        2.  **Mixed-Language Sections (Within `script`):**
            -   *Regardless* of the dominant language chosen for the `script` tag, follow these rules for text *within* the `script`:
                -   Short quotations, brand names, or proper nouns in a different language are allowed *within* a sentence, as long as the overall sentence is in the chosen language for the `script` tag.
                -   Do *not* mix languages at the sentence level within the `script` tag.  The `script` tag must be *entirely* in the chosen language (except for the allowed short quotations, etc.).

        3. **No Translation:**
           - Do *not* translate any text extracted *directly* from the input document.

### **6. TEMPLATE COMPLIANCE VERIFICATION**
   - After generation, **automatically verify 100% adherence to the template.** *Use an automated script/process.*
   - See the **user prompt (prompt)** for detailed template and formatting rules.
""",
    "prompt_1": """
    # IMPORTANT: ANALYZE INPUT DOCUMENT AND FILL TEMPLATE

    You must analyze the input document and use the extracted information to fill in the provided JSON template.  Follow these steps:

    1.  **Analyze Input Document:**  Carefully read and analyze the provided input document. Refer to the `system_instruction` for guidance on how to analyze the document ("ANALYZE", "SELECT A TOPIC", and "ORGANIZE CONTENT" sections).
    2.  **Fill Template:**  Use the information extracted from the document to fill in the fields of the JSON template provided below.  *Every* field (except `image` and `images`) *must* have a meaningful value.
    3.  **Strictly Adhere to Template:**  The output JSON *must* exactly match the template structure.  Follow all rules below regarding template structure, language, and content.

    # RULES (ABSOLUTE COMPLIANCE):

    - **All lists (`sections`, `text-extra`, `title-extra`, etc.) must have the exact same length as in the template.**
    - **The JSON output must strictly adhere to the template’s key names, structure, and data types.** (Strings remain strings, numbers remain numbers; no type conversions.)
    - **No empty values (`text-extra: [""]`, `text-main: ""`, etc.).**
    - **Output must be enclosed in a valid `json` code block (```json ```).**
    - **Use double quotes (`""`) for all strings. Single quotes (`'`) are allowed only inside strings, not as string delimiters.**
    - **Braces `{}`, brackets `[]`, colons `:`, and the overall JSON structure must exactly match the template.**

    ### **Rules**

    1.  **Meaningful Values:** All fields (except `image` and `images`) must contain meaningful values.
    2.  **Inference:** If no content is available, infer and generate a valid value based on context, *but do not violate list length constraints*.
    3.  **`images` Placeholders:** The `images` list must contain the same number of `""` placeholders as in the template.
    4.  **Template Adherence (Detailed):**
        -   `scene` object count must match the template exactly (no extra or missing scenes).
        -   JSON structure must not deviate (key order, no additional fields, all required fields present except `images` and `image`).
        - No fields without meaningful data.
        - Do not insert additional data.
    5.  **ABSOLUTELY NO TRANSLATION of text extracted directly from the input document.** (English remains English, Korean remains Korean. Only `script` can be in either Korean or English.)
    6.  **Output JSON Language for non-original text:** Follow the language guidelines in the `system_instruction`, *but never translate original text*.
    7. Korean text *must* be human-readable (not escaped with Unicode sequences like `\\uXXXX`).
    - **Rules for `script` Language Selection:**

        1.  **Determine the Dominant Language Based on Percentage:**
            -   Analyze the entire input document and calculate the percentage of Korean text and English text.
            -   **If the percentage of English text is greater than or equal to 50%, the `script` tag *must* be generated in English.**
            -   **If the percentage of Korean text is greater than 50%, the `script` tag *must* be generated in Korean.**

        2.  **Mixed-Language Sections (Within `script`):**
            -   *Regardless* of the dominant language chosen for the `script` tag, follow these rules for text *within* the `script`:
                -   Short quotations, brand names, or proper nouns in a different language are allowed *within* a sentence, as long as the overall sentence is in the chosen language for the `script` tag.
                -   Do *not* mix languages at the sentence level within the `script` tag.  The `script` tag must be *entirely* in the chosen language (except for the allowed short quotations, etc.).

        3. **No Translation:**
           - Do *not* translate any text extracted *directly* from the input document.

    - **Output must be enclosed in a valid `json` code block (```json ```).**

    ### Template Structure:

    The following is the template structure for the output JSON.  **You must adhere to this structure 100% exactly.**
""",
    "prompt_2": """
# URGENT: JSON FORMAT AND STRUCTURE CORRECTION
The previous attempt produced INVALID JSON that *deviated significantly* from the template structure. This attempt *must* produce valid, parsable JSON that *exactly* matches the template structure provided separately. **There is absolutely no room for error. Any deviation from the template will result in immediate rejection.**

**CRITICAL JSON RULES (NO EXCEPTIONS - TEMPLATE IS LAW):**

1.  **Valid JSON:** The output *must* be valid JSON, enclosed in a `json` code block:
    ```json

      ... (your JSON here) ...

    ```
    Failure to use the correct code block is an immediate rejection.
2.  **Double Quotes ONLY:**  Use double quotes (`"`) *exclusively* for all keys and string values.  *Never* use single quotes (`'`) as delimiters.  *Never* put a double quote inside another double quote unless it's properly escaped (e.g., `\\" `).  Incorrect quoting will cause parsing errors.
3.  **TEMPLATE STRUCTURE (ABSOLUTE - NO DEVIATION):**
    -   You *must* follow the template structure *exactly* as provided.
    -   **Do *not* add *any* keys that are not present in the template.**
    -   **Do *not* remove *any* keys that are present in the template (with the specific exceptions of `image` and `images` handled in rules 6 and 7 below).**
    -   **Key Names, Order, Nesting:** Match the template *exactly*.
    -   **List Lengths:** All lists *must* have the *exact* number of elements specified in the template.
    -   **Data Types:** Match the template *exactly*.
    -   **Top-Level List Structure:** The top-level list *must* contain *exactly* the same number of `scene` objects as the provided template – *no more, no fewer* – and these `scene` objects *must* be the *only* elements at the top level; *no other* objects or data types are allowed.
4.  **Meaningful Values:**  *Every* field (except `image` and `images`) *must* contain a meaningful, non-empty value.  `""`, `[]`, or `{}` are *never* allowed in these fields.
5.  **ABSOLUTELY NO TRANSLATION:** Text extracted *directly* from the input document *must not* be translated. English remains English, Korean remains Korean.  The *only* exception is the `script` tag.
6.  **`image` Handling:**
    -   If and *only if* the template includes an `image` key, the value for `image` *must* be an empty string (`""`).
    -   If the template *does not* include an `image` key, do *not* add it to the output.

7.  **`images` Handling:**
    -   If and *only if* the template includes an `images` key, the value for `images` *must* be an empty list (`[]`).
    -   If the template *does not* include an `images` key, do *not* add it to the output.

8. **Top-Level List Structure:** The top-level list of the output JSON *must* contain *exactly* the same number of `scene` objects as the provided template – *no more, no fewer* – and these `scene` objects *must* be the *only* elements at the top level; *no other* objects or data types are allowed in the top-level list.

### Template Structure:
""",
    "prompt_3": """
    # URGENT: CONTENT, LANGUAGE, AND TEMPLATE STRUCTURE CORRECTION

    Previous attempts failed due to content (empty values) and/or language (translation, incorrect `script` language) errors.  This attempt *must* address these issues and produce a valid JSON output that adheres to all rules regarding content, language, and the template structure provided separately below.  **Failure to comply with *any* rule will result in rejection.**

    **CRITICAL RULES (ABSOLUTE COMPLIANCE REQUIRED):**

    1.  **Meaningful Values (ABSOLUTE - NO EMPTY VALUES):**
        -   *Every* field (except `image` and `images`) *must* contain a meaningful, non-empty value.
        -   **`""`, `[]`, or `{}` are *strictly forbidden* (except in `image` and `images`).**
        -   **No exceptions.** Infer if needed, but *never* leave a field empty.

    2.  **ABSOLUTELY NO TRANSLATION of text extracted *directly* from the input document.** (English remains English, Korean remains Korean. Only `script` can be in either Korean or English.)

    3.  **`script` Tag Language (Choose ONE):**
        -   Choose *either* Korean *or* English for the `script` tag (rules from `system_instruction`).
        -   **The `script` tag must be *entirely* in the chosen language.** No sentence-level mixing.
        -   **Exception:** Short quotations/brand names/proper nouns are allowed *within* a sentence of the chosen `script` language.

    4.  **Output JSON Language for non-original text:**
        - Analyze the input document and determine its primary language.
        - If the primary language is Korean, All other text fields should follow the language guidelines in the system_instruction.
        - If the primary language is English, the output JSON, *except for text directly extracted from the document*, should be in Korean.
        - If the document contains a mix of languages, follow the language guidelines in the system_instruction.

    5.  **TEMPLATE STRUCTURE (PROVIDED SEPARATELY - ABSOLUTE ADHERENCE):**
        -   You *must* adhere to the JSON template structure provided separately below, following this prompt. **This structure is provided as a *variable* and must be followed *exactly* as given, with *absolutely no deviations*.**
        -   **Number of `scene` Objects:** The output JSON *must* be a list containing *exactly* the same number of `scene` objects as the provided template. *Absolutely no* additional `scene` objects are allowed. The output *must not* contain more `scene` objects than specified in the template, *regardless* of the input document's content.
        -   **Key Names, Order, Nesting:** The key names, their order, and the nesting of objects and lists *must* be *identical* to the provided template.
        -   **List Lengths:** All lists *must* have the *exact* number of elements specified in the template. **You *must not* add extra elements or remove required elements.**
        -   **Data Types:** Data types (strings, lists, etc.) *must* match the template.
        -   **No Empty Values:** As stated in Rule 1, *no* field (except `image` and `images`) may contain an empty value (`""`, `[]`, or `{}`). **This rule is *critical* and applies to *every* part of the template structure.**
        -   **Any deviation from the template structure, including adding extra `scene` objects, removing elements, or leaving elements empty, *will result in immediate rejection*.**
        -   **Do *not* add *any* keys that are not present in the template.**
        -   **Do *not* remove *any* keys that are present in the template
    **Valid JSON:** The output *must* be valid JSON, enclosed in a `json` code block (```json ```)
    **Double Quotes ONLY:**  Use double quotes (`"`) *exclusively* for all keys and string values.  *Never* use single quotes (`'`) as delimiters. 

    **Ensure the output is correct in terms of content, language, and the provided template structure.**

### Template Structure:
""",
}
