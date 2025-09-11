_prompt = {
    "prompt": '''
        Please analyze the PDF or Json provided and create a video scenario for a short-form video.

        Steps for Analyzing the JSON or PDF and Writing the Scenario:
            1. *RECEIVE INPUT FILE*:
               - Accept a file as input, which can be either a JSON or a PDF file.
            2. *ANALYZE THE FILE STRUCTURE*:
               - If the input file is JSON, analyze `text` and `table` tags.
               - If the input file is PDF, analyze the content and structure, focusing on textual and tables data.
            3. *ORGANIZE THE CONTENT INTO CHAPTERS AND SECTIONS*:
               - Segment the analyzed data into thematic chapters.
               - Further divide chapters into `sections` based on detailed insights or data types.
            4. *WRITE THE SCENARIO IN JSON FORMAT*:
               - Compile and write the scenario using the structured insights derived from the analysis.

        TAGS DESCRIPTION:
            - `chapter`: Groups of pages that are logically related are defined as one chapter.
            - `sections`: A unit within a chapter that is logically distinct. The "sections" array uses indexes starting from 0 and contains only two items. Therefore, the indexes are 0 and 1. No more than two items are included.
            - `opening`: The `opening` tag, which can only be used once, is the parent tag of the `chapter` tag and explains that the chapter is the introduction.
            - `body`: The `body` tag is the parent tag of the `chapter` tag and explains that the `chapter` is the main `body`.
            - `closing`: The `closing` tag, which can only be used once, is the parent tag of the `chapter` tag and explains that the chapter is the conclusion.

        SPECIFIC TAG DETAILS:
            - `title-main`: The main title, a statement representing that `chapter` or `sections` must be entered.
            - `title-extra`: The subtitle.
            - `text-main`: The main content.
            - `text-extra`: the subtext. It must appear only in the `opening.chapters`.
            - `script`: The script tag is the spoken script that describes the chapter. The `body.chapter.script` should include the contents of the `chapter.sections.text-main` and `chapter.sections.title-main`.

        *BODY DETAILS*:
            1. **Types of Coverage (body[0].chapter)**:
               - The types of coverage offered by the insurance policy should be extracted.
            2. **Premiums and Example Insurance Premium (body[1].chapter)**:
               - The example insurance premium should be extracted first, and if there is no example premium, information about premiums and their calculation should be extracted.
            3. **Coverage Limits and Deductibles (body[2].chapter)**:
               - Information about coverage limits (the maximum amount the insurer will pay) and deductibles (the amount the insured must pay before the insurer pays) should be extracted.
            4. **Eligibility Criteria and Product Specifics (body[3].chapter)**:
               - The eligibility criteria and specific information about the insurance product should be extracted.

            The `body.chapter` should be output in the specified order without including any extra information beyond these specified items.


        *IMPORTANT*:
            - The json must be based on numerical data provided. Discard any uncertain information.
            - `text-extra` must appear only in the `opening` chapters. It must never appear in the `body`.
            - *ALL TAGS' VALUES MUST BE IN THE LANGUAGE OF THE INPUT FILE*.
            - The `script` tag cannot be included in `sections`.
            - THE VALUES OF THE `script` TAG MUST BE 60 CHARACTERS OR LESS, AND THE VALUES OF THE OTHER SPECIFIC TAGS MUST BE 40 CHARACTERS OR LESS, INCLUDING SPACES.

        RETURN MESSAGE EXAMPLE:
            ```json
                {
                    "opening": {
                        "chapter": {
                            "title-main": "맹견배상책임보험",
                            "text-main": "상품요약서",
                            "script": "안녕하세요. 맹견배상책임보험 상품에 대해 알아보겠습니다"
                        }
                    },
                    "body": [
                        {
                            "chapter": {
                                "title-main": "보장의 종류",
                                "title-extra": "대인배상과 대동물배상",
                                "script": "맹견의 사고로 타인의 신체에 손해, 명견의 사고로 타인의 동물에 손해를 입혔을 경우 보상합니다",
                                "sections": [
                                    {
                                        "title-main": "대인배상",
                                        "text-main": "명견의 사고로 타인의 신체에 손해를 입혔을 때 보상"
                                    },
                                    {
                                        "title-main": "대동물배상",
                                        "text-main": "맹견의 사고로 타인의 동물에 손해를 입혔을 때 보상"
                                    }
                                ]
                            }
                        },
                        {
                            "chapter": {
                                "title-main": "보험료",
                                "script": "보험료의 경우 일시납기준 15,950원이며, 상기보험료는 요율변동 및 가입조건에 따라 변경될 수 있습니다",
                                "sections": [
                                    {
                                        "title-main": "15,950원",
                                        "text-main": "상기보험료는 요율변동 및 가입조건에 따라 변경"
                                    }
                                ]
                            }
                        },
                        {
                            "chapter": {
                                "title-main": "보상한도",
                                "title-extra": "대인, 대동물 각 1사고당 10만원",
                                "script": "대동물보상의 경우 1사고당 최대 200만원, 대인배상의 경우 1인당 최대 8천만원까지 보상합니다",
                                "sections": [
                                    {
                                        "title-main": "대동물배상",
                                        "text-main": "1사고당 최대 200만원"
                                    },
                                    {
                                        "title-main": "대인배상",
                                        "text-main": "사망 - 1인당 최대 8천만원"
                                    }
                                ]
                            }
                        },
                        {
                            "chapter": {
                                "title-main": "가입자격 및 상품특이사항",
                                "script": "동물보호법 시행규칙에서 정하는 맹견의 범위에 해당하는 맹견이 가입할 수 있으며 보험기간은 1년 입니다.",
                                "sections": [
                                    {
                                        "title-main": "가입자격",
                                        "text-main": "동물보호법 시행규칙에서 정하는 맹견의 범위에 해당"
                                    },
                                    {
                                        "title-main": "특이사항",
                                        "text-main": "보험기간 1년이며, 일시납 원칙 만기 시 환급급 없음"
                                    }
                                ]
                            }
                        }
                    ],
                    "closing": {
                        "chapter": {
                            "title-main": "삼성생명",
                            "script": "보험을 넘어서는 보험, 삼성생명"
                        }
                    }
                }
            ```
            *IMPORTANT*:
                - `text-extra` must appear only in the opening chapters. It must never appear in the `body`.
                - *ALL TAGS' VALUES MUST BE IN THE LANGUAGE OF THE INPUT FILE*.
                - The `script` tag cannot be included in `sections`.
                - THE VALUES OF THE `script` TAG MUST BE 60 CHARACTERS OR LESS, AND THE VALUES OF THE OTHER SPECIFIC TAGS MUST BE 40 CHARACTERS OR LESS, INCLUDING SPACES.
        '''
    ,
    "validation_prompt": """
        # GUIDELINES FOR VALIDATING JSON

        PERFORM THE FOLLOWING OPERATIONS ON THE JSON DATA IN THE GIVEN ORDER:
            1. *If there are more than 2 sections within a chapter, condense them meaningfully into 2 sections.*
            2. If a `sections` within the `body` contains a `text-extra` key, combine it with `text-main` into a single `text-main` value and remove the original `text-extra`.
            3. *`sections` must not include `script` tag. If `script` exists in `sections`, it must be removed.*
        
                    
        The result should be output in a JSON code block format, where the content is enclosed with three backticks and json is specified.
        """
}