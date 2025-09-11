# gemgem-ai-test
ai 모델들의 기능 테스트를 위한 프로젝트

### 가상환경 activate
```
source venv/bin/activate
```


### GRADIO-IMAGE2VIDEO-000001 request_body 양식
```
{
    "userId": 1,
    "projectId": 1,
    "documentS3": [
        "s3://ai-10k1m/public/gradio/1/1/document/275afa4c-d533-4ac2-a358-828a43f1bfc1_01.jpg"
    ],
    "analysisS3": "s3://ai-10k1m/public/gradio/1/1/analysis/",
    "analysisHttps": "https://cdn.gemgem.video/private/development/1/1/analysis/",
    "group": "10k1m.com",
    "type": "AI-GRADIO-IMAGE2VIDEO-000001",
    "option": [
        {
            "src": "s3://ai-10k1m/public/gradio/1/1/document/84d0f107-54ea-407a-a3d2-15e740f64b9e_01.jpg",
            "video_type": "API or ENGINE",
            "model": {
                "name": "Wan2.2",
                "option": {
                    "prompt": "str",
                    "resolution": "512x512, etc...",
                    "aspect_ratio": "9:16 or 16:9",
                    "negative_prompt": "str or Null",
                    "total_second_length": 5,
                    "frames_per_second": 24,
                    "num_inference_steps": 20,
                    "guidance_scale": 5,
                    "shift": 5,
                    "seed": 42
                }
            }
        }
    ]
}
```