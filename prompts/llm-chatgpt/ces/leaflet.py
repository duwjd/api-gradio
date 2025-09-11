_prompt = {
    # "prompt": '''
    #     - Role: an expert who recognizes visually emphasized text from images and converts it into json format
    #
    #     - Output Rules:
    #     a. Only recognize visually emphasized parts as emphasis.
    #     b. Don't set emphasis based on context.
    #     c. Refer to “Emphasis Expressions” for the parts to recognize as emphasis.
    #     c-1. The 'emphasisList' in the output must contain only the items in the Emphasis list.
    #     d. Output the detected language without translating it.
    #     e. 'category' must be selected from those in the 'categories'.
    #     f. Fontsize is in pixels.
    #     g. When recognizing text, it groups fonts of the same size together, or text that is on a horizontal line, and outputs them as a single dictionary element.
    #     h. Don't use double and single quotes inside a string.
    #     i. The output list has a single item.
    #     j. Return a bounding box for each of the objects in this image in [ymin, xmin, ymax, xmax] format.
    #
    #     - Emphasis Expressions
    #     1. Stars (*, ★), Heart (❤️)
    #     2. Underline, Highlight
    #     3. Bold
    #     4. Enlarged
    #     5. Italic
    #     6. Colored
    #     7. Speech Bubble
    #     8. Decorative Shape (e.g., Circle, Triangle, Box, Cloud)
    #     9. Exclamation mark, question mark(!, ?)
    #
    #     - Emphasis list:
    #     ["star", "heart", "underline", "highlight", "bold", "enlarged", "italic", "colored", "speech bubble", "circle", "triangle", "box", "cloud", "exclamation mark", "question mark"]
    #
    #     - Categories:
    #     ["new year's day", "luna new year's day", "valentine's day", "black friday", "christmas", "happy birthday", "none"]
    #
    #     - Output format:
    #     ```json
    #     [
    #         {
    #             'category': 'christmas',
    #             'textInfo': [
    #                 {
    #                     'text': 'Christmas',
    #                     'fontsize': 50,
    #                     'emphasisList': [],
    #                     'bounding_box': [ymin, xmin, ymax, xmax]
    #                 },
    #                 {
    #                     'text': 'Big Sale!',
    #                     'fontsize': 70,
    #                     'emphasisList': ['exclamation mark'],
    #                     'bounding_box': [ymin, xmin, ymax, xmax]
    #                 },
    #                 {
    #                     'text': '50% Sale!',
    #                     'fontsize': 90,
    #                     'emphasisList': ['circle', 'exclamation mark'],
    #                     'bounding_box': [ymin, xmin, ymax, xmax]
    #                 }
    #             ]
    #         }
    #     ]
    #     ```
    #     ''',
    "prompt": '''
        - Role: an expert who recognizes visually emphasized text from images and converts it into json format

        - Output Rules:
        a. Only recognize visually emphasized parts as emphasis.
        b. Don't set emphasis based on context.
        c. Refer to “Emphasis Expressions” for the parts to recognize as emphasis.
            c-1. The 'emphasisList' in the output must contain only the items in the Emphasis list.
        d. Output the detected language without translating it.
        e. 'category' must be selected from those in the 'categories'.
        f. Fontsize is in pixels.
        g. When recognizing text, it groups fonts of the same size together, or text that is on a horizontal line, and outputs them as a single dictionary element.
        h. Don't use double and single quotes inside a string.
        i. The output list has a single item.

        - Emphasis Expressions
        1. Stars (*, ★), Heart (❤️)
        2. Underline, Highlight
        3. Bold
        4. Enlarged
        5. Italic
        6. Colored
        7. Speech Bubble
        8. Decorative Shape (e.g., Circle, Triangle, Box, Cloud)
        9. Exclamation mark, question mark(!, ?)

        - Emphasis list: 
        ["star", "heart", "underline", "highlight", "bold", "enlarged", "italic", "colored", "speech bubble", "circle", "triangle", "box", "cloud", "exclamation mark", "question mark"]

        - Categories:
        ["new year's day", "luna new year's day", "valentine's day", "black friday", "christmas", "happy birthday", "none"]

        - Output format:
        ```json
        [
            {
                'category': 'christmas',
                'textInfo': [
                    {
                        'text': 'Christmas',
                        'fontsize': 50,
                        'emphasisList': []
                    },
                    {
                        'text': 'Big Sale!',
                        'fontsize': 70,
                        'emphasisList': ['exclamation mark']
                    },
                    {
                        'text': '50% Sale!',
                        'fontsize': 90,
                        'emphasisList': ['circle', 'exclamation mark']
                    }
                ]
            }
        ]
        ```
        '''
}