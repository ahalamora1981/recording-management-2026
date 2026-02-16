---
name: ai-models-info
description: Retrieves AI models information including API endpoints, model names, and credentials; when agent needs to (1) Generate LLM responses, (2) Understand images, (3) Transcribe audio, (4) Generate images based on text descriptions.
---

# AI Models Information

This skill provides access to AI model configuration details for making API calls.

## When to Use

- When agent needs to generate text responses
- When agent needs to understand images
- When agent needs to transcribe audio
- When agent needs to generate images based on text descriptions

## Available Models

### OpenAI Compatible API

- GLM API:
  - **API URL**: https://open.bigmodel.cn/api/paas/v4
  - **API KEY**: c660899f0ae74d6391059e4683a6ffe9.hAtP5SQGPPucjeI1

- Minimax API:
  - **API URL**: https://api.minimaxi.com/v1
  - **API KEY**: sk-api-C0vjaZJDr8akqhZfFBRpT0YdwC3U1I062WxX0X95ZqT_s0_Y5t35Pa_xkWTxjJZae9tTkjppjcaT6BUuicaX3pHosNTQ5fMgTdozZs03T5og34mu0GRRrKw

### Model Types

| Type | Model Provider | Model Name | Purpose |
|------|----------------|------------|---------|
| LLM | GLM | glm-4.7-flash | Text response / text generation |
| VLM | GLM | glm-4.6v-flash | Vision understanding / image analysis |
| ASR | GLM | glm-asr-2512 | Speech recognition / audio transcription |
| Image | Minimax | image-01 | Image generation based on text descriptions |

## Instructions

- Use OpenAI-compatible format with the provided API URL and KEY
- For text generation with GLM: use model `glm-4.7-flash`
- For vision tasks with GLM: use model `glm-4.6v-flash` with image URLs or base64 encoded images
- For speech recognition with GLM: use model `glm-asr-2512` with multipart/form-data format for audio files
- For image generation with Minimax: use model `image-01` with text descriptions and aspect ratio

## Examples

1. LLM (text generation):

Refer to the [LLM script](./scripts/llm.sh) for the full example.

2. VLM (vision/image understanding):

Refer to the [VLm script](./scripts/vlm.sh) for the full example.

3. ASR (speech recognition):

Refer to the [ASR script](./scripts/asr.sh) for the full example.

4. Image (image generation):

Refer to the [Image script](./scripts/image_generation.py) for the full example.