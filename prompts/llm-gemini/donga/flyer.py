_prompt = {
    "prompt":
        """
        광고용 팜플렛을 만들기 위한 정보를 추출하고 JSON 구조를 생성해주세요. 팜플렛은 고객 프로모션용 전단지로, 아래의 지침과 조건을 따라주세요.
    
        **태그 설명:**
        - `opening`, `body`, `closing`: 서론, 본론, 결론에 해당하는 **형식적인 태그**입니다. 각 태그 안에는 `chapter` 가 포함되어 특정 주제에 대한 정보를 제시합니다.
        - `chapter`: 해당 문서에는 뉴스기사가 존재합니다.. 이러한 뉴스기사를 다양한 주제로 나누며, 하나의 주제가 chapter로 정의됩니다.
             * `opening.chapter`, `body[0].chapter`, `body[1].chapter`, `closing.chapter` 모두 **기사에 대한 정보** 를 담아야 합니다.
        - `sections`: `chpater` 내에 존재하며, 해당 주제를 설명한다. sections 리스트 안에 2개의 객체가 포함되도록 해. 각 객체는 'title-main'과 'text-main' 속성을 가지고 있어야 해.
        - `title-main`: 각 챕터 또는 섹션의 주요 제목입니다. 모든 chapter의 title-main은 *뉴스기사 제목이* 됩니다.
        - `title-extra`: 부가적인 제목 또는 부제입니다. 모든 chapter의 title-extra는 *발간일 또는 저자*가 출력됩니다.
        - `text-main`: 각 챕터 또는 섹션의 주요 내용을 나타냅니다. 모든 chpater의 text-main은 *뉴스 서브주제의* 타이틀이 입력되어야합니다. 또한 sections 내의 text-main는 150자 미만이어야합니다.
        - `script`: 해당 대그는 해당 chapter를 설명하는 음성 스크립트 입니다.
    
        **중요 사항:**
        1. **JSON 포맷으로 출력되어야 합니다.**
        2. 톤 앤 매너는 신뢰감 있고 전문적인 어조를 사용해야합니다.
        3. **타겟 고객:** 뉴스를 보는 소비자.
    
        **주의 사항:**
        - **사실 기반 정보만 사용:** 문서에 명시된 정보만을 사용하고, 문서에 없는 정보는 추정하거나 임의로 추가하지 마세요.
        - **태그 확인:** 정의된 태그만 사용해야합니다.
        - **출력:** 결과는 출력 예시에 있는 json 형태로 나와야한다.
        
        - opening.chpater, body[0].chapter, body[1].chapter, closing.chapter 총 4장 분랑이 나와야한다.
        **출력 예시**:
        ```json
        {
            \"opening\": {
                \"chapter\": {
                    \"title-main\": \"뉴스기사 제목\",
                    \"title-extra\": \"발간일 또는 저자\",
                    \"text-main\": \"보장플랜 또는 보장특약 제목\",
                    \"sections\": [
                        {
                        \"title-main\": \"보장 플랜에 대한 타이틀1\",
                        \"text-main\": \"보장 플랜에 대한 부가설명1\",
                        },
                        {
                        \"title-main\": \"보장 플랜에 대한 타이틀2\",
                        \"text-main\": \"보장 플랜에 대한 부가설명2\",
                        }
                    ]
                }
            },
            \"body\": [ 
                {
                    "\chapter\": {
                        \"title-main\": \"뉴스기사 제목\",
                        \"title-extra\": \"발간일 또는 저자\",
                        \"text-main\": \"보장플랜 또는 보장특약 제목\",
                        \"sections\": [
                            {
                            \"title-main\": \"보장 플랜에 대한 타이틀1\",
                            \"text-main\": \"보장 플랜에 대한 부가설명1\",
                            },
                            {
                            \"title-main\": \"보장 플랜에 대한 타이틀2\",
                            \"text-main\": \"보장 플랜에 대한 부가설명2\",
                            }
                        ],
                    }
                },
                {
                    \"chapter\": {
                        \"title-main\": \"뉴스기사 제목\",
                        \"title-extra\": \"발간일 또는 저자\",
                        \"text-main\": \"보장플랜 또는 보장특약 제목\",
                        \"sections\": [
                            {
                            \"title-main\": \"보장 플랜에 대한 타이틀1\",
                            \"text-main\": \"보장 플랜에 대한 부가설명1\",
                            },
                            {
                            \"title-main\": \"보장 플랜에 대한 타이틀2\",
                            \"text-main\": \"보장 플랜에 대한 부가설명2\",
                            }
                        ],
                    }
                }
            ],
            \"closing\": {
                \"chapter\": {
                    \"title-main\": \"뉴스기사 제목\",
                    \"title-extra\": \"발간일 또는 저자\",
                    \"text-main\": \"보장플랜 또는 보장특약 제목\",
                    \"sections\": [
                        {
                        \"title-main\": \"보장 플랜에 대한 타이틀1\",
                        \"text-main\": \"보장 플랜에 대한 부가설명1\",
                        },
                        {
                        \"title-main\": \"보장 플랜에 대한 타이틀2\",
                        \"text-main\": \"보장 플랜에 대한 부가설명2\",
                        }
                    ],
                }
            }
        }
            ...
    
        ```
        """

}

# **예시**:
# ```
#     [
#         "chapter": {
#             {
#                 "title-main": "'암치료 끝판왕' 다모은 S3 신담보 핵심 포인트",
#                 "title-extra": "프리미엄 암직접치료 보장",
#                 "text-main": "여러 번 받는 항암 치료, 비용은 '억' 소리",
#                 "sections": [
#                     {
#                         "title-main": "앙성자 방사선",
#                         "text-main": "급여 100만/비급여 2~3천만",
#                         "text-extra": "(폐/간/자궁/유방 암 등)",
#                     },
#                     {
#                         "title-main": "세기조정 방사선",
#                         "text-main": "급여 80만/비급여 1천만",
#                         "text-extra": "(대부분 암종, 부작용 최손)",
#                     },
#                     {
#                         "title-main": "면역 항암제",
#                         "text-main": "회당 300만 (격주) 1년 투약 7천만",
#                         "text-extra": "(옵디보주, 폐/식도암)",
#                     }
#                 ]
#                 "text-extra": "정확한 내용은 약관과 상품 설명서를 확인해야 함"
#             }
#         },
#         ...
#     ]
# ```
