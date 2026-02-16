curl --request POST \
  --url https://open.bigmodel.cn/api/paas/v4/audio/transcriptions \
  --header 'Authorization: Bearer API_Key' \
  --header 'Content-Type: multipart/form-data' \
  --form model=glm-asr-2512 \
  --form stream=false \
  --form file=@example-file