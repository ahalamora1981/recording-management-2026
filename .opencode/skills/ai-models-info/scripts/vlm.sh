curl -X POST \
  https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.6v-flash",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
              "url": "the image url or base64 encoded image"
            }
          },
          {
            "type": "text",
            "text": "Where is the second bottle of beer from the right on the table?  Provide coordinates in [[xmin,ymin,xmax,ymax]] format"
          }
        ]
      }
    ],
    "thinking": {
      "type":"enabled"
    }
  }'