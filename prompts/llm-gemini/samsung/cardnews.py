_prompt = {
    "paragraphs_prompt": "Analyze the following paragraph and provide three pieces of information. The output should be in the same language as the input. Do not create new content but reorganize it. Adhere to the following guidelines to ensure the meaning remains unchanged:\nMeaning Preservation: Reconstruct the text accurately without altering the original meaning and key ideas. The intended meaning from the original text must be maintained.\nContext Preservation: Maintain the context and flow of the sentences. The logical connections in the original text should remain the same.\nAccurate Transmission: Precisely reflect specific information such as numbers, data, and facts from the original text. Be cautious not to change figures or facts.\ntitle-main: Create a one-line title that summarizes the paragraph. This title should concisely capture the main point of the paragraph.\ntext-main: Summarize the key message of the paragraph in 2 to 3 sentences. Use only the information provided in the paragraph.\nscript: Write a TTS script explaining the content of 'text-main'. The end of the sentences must match 'text-main'. The script should be about 100 characters long. \n\nExample: \nInput: \"It shows a trend of increasing by 10 times.\" \nCorrect Reorganization: \"It shows a trend of increasing by 10 times.\" \nIncorrect Reorganization: \"It is increasing by 10 times.\"\n\nAs in this example, be careful not to alter the specific information and meaning provided in the original text.\n\nReturn format: \n{ \n\"title-main\": \"comment\", \n\"text-main\": \"comment\", \n\"script\" : \"comment\" \n}",
    "prompt": """다음 문서를 분석하고 세 가지 정보를 제공하세요. 출력은 입력과 동일한 언어로 작성해야 하며, 새로운 내용을 만들지 말고 재구성만 하세요. 의미를 변경하지 않도록 다음 지침을 준수하세요:\n
            의미 보존: 원래의 의미와 핵심 아이디어를 변경하지 않고 정확하게 재구성하세요. 원문에서 의도된 의미가 유지되어야 합니다.\n
            맥락 보존: 문장의 맥락과 흐름을 유지하세요. 원문에서의 논리적 연결이 그대로 남아 있어야 합니다.\n
            정확한 전달: 숫자, 데이터, 사실 등 구체적인 정보를 정확하게 반영하세요. 수치나 사실을 변경하지 않도록 주의하세요.\n
            title-main: 문서를 요약하는 한 줄 제목을 작성하세요. 이 제목은 카드뉴스와 같은 형태로 문서의 핵심 포인트를 간결하게 담아야 합니다.\n
            text-main: 문서의 핵심 메시지를 2~3 문장으로 요약하세요. 문서에서 제공된 정보만 사용하세요.\n
            script: 'text-main'의 내용을 설명하는 TTS 스크립트를 작성하세요. 문장의 끝이 'text-main'과 일치해야 합니다. 스크립트는 약 100자 정도여야 합니다.\n\n
            예시:\n
            입력: \"10배 증가하는 경향을 보인다.\"\n
            올바른 재구성: \"10배 증가하는 경향을 보인다.\"\n
            잘못된 재구성: \"10배 증가하고 있다.\"\n\n
            이 예시처럼, 제공된 원문의 구체적인 정보와 의미를 변경하지 않도록 주의하세요.\n\n



            반환 형식:\n
            ```json
            {\n
            \"opening\": {\n
                \"chapter\": {\n
                    \"title-main\": \"\",\n
                    \"title-extra\": \"\",\n
                    \"script\": \"\"\n
                }\n
            },\n
            \"body\": [\n
                {\n
                    \"chapter\": {\n
                        \"title-main\": \"\",\n
                        \"text-main\": \"\",\n
                        \"script\": \"\"\n
                    }\n
                },\n
                {\n
                    \"chapter\": {\n
                        \"title-main\": \"\",\n
                        \"text-main\": \"\",\n
                        \"script\": \"\"\n
                    }\n
                },\n
                {\n
                    \"chapter\": {\n
                        \"title-main\": \"\",\n
                        \"text-main\": \"\",\n
                        \"script\": \"\"\n
                    }\n
                },\n
                {\n
                    \"chapter\": {\n
                        \"title-main\": \"\",\n
                        \"text-main\": \"\",\n
                        \"script\": \"\"\n
                    }\n
                }\n
            ],\n
            \"closing\": {\n
                \"chapter\": {\n
                    \"title-main\": \"\",\n
                    \"script\": \"\"\n
                }\n
            }\n
            }\n
            ```
        """
    ,
    "validation_prompt": """
    The result should be output in a JSON code block format, where the content is enclosed with three backticks and json is specified.
    """

}