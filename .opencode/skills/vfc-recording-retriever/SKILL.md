---
name: vfc-recording-retriever
description: Retrieves media recordings' metadata and media from VFC Capture (Verba) system. Use when user needs to get media recordings based on time frame(mandatory) and participant name(optional). Supports searching calls, retrieving metadata, and downloading actual media files (audio/video recordings).
---

# VFC(Verba) Call Recorder

## When to use

- User requests call metadata or recordings from Verba VFC Capture system based on a time frame
- User wants to search for calls involving a specific participant
- User needs to download audio or video recordings of calls

## Default Configuration

This skill is configured for Verint Training environment:
- **Host**: `https://mst-vfc.verint.training`
- **Username**: `jonnytaodemo`
- **Password**: `Jun@7895123`
- **API Key**: `D466035F-CE26-4E6A-BD4E-891A3BD58807`

## Required parameters

The user must provide:
- **apiKey**: API key for authentication (D466035F-CE26-4E6A-BD4E-891A3BD58807)
- **userName**: VFC username (jonnytaodemo)
- **password**: VFC password (Jun@7895123)
- **start_time**: Start of search period - MANDATORY (format: `YYYY-MM-DD hh:mm` or `YYYY-MM-DD hh:mm:ss`)
- **end_time**: End of search period - MANDATORY (format: `YYYY-MM-DD hh:mm` or `YYYY-MM-DD hh:mm:ss`)
- **participant_name**: Name of call participant to search for - OPTIONAL

## Process

### Step 1: Authenticate with VFC API

- Description: Obtain an authentication token required for subsequent API calls.
- Input Parameters:
  - **apiKey**: API key for authentication (D466035F-CE26-4E6A-BD4E-891A3BD58807)
  - **userName**: VFC username (jonnytaodemo)
  - **password**: VFC password (Jun@7895123)
- Output:
  - **token**: Authentication token for subsequent API calls

- CURL command to get response which contain the token
```bash
curl --location 'https://mst-vfc.verint.training/verba/api?action=RequestToken&apiKey=D466035F-CE26-4E6A-BD4E-891A3BD58807&userName=jonnytaodemo&password=Jun%407895123' \
    --header 'Cookie: JSESSIONID=FBC3385B4BAC7BCAE49AE86047C63EE5'
```

- Get token from the XML response, this is the XML response sample (not real data)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<VerbaApi>
    <Response
        code="0"
        type="RequestToken"
        token="W7XIdoOnOjWY7HTRzKsw8hWBZXMyexo6"
        
    />
    <SessionId>8950D82B76341AA93CC7C26CD3B6B88E</SessionId>
    <SessionParameterName>jsessionid</SessionParameterName>
    <SessionCookieName>JSESSIONID</SessionCookieName>
    <Remote>false</Remote>
</VerbaApi>
```

### Step 2: Search for Calls

- Description: Search for calls based on a time frame and optional participant name. Returns call metadata including `ccdr_id`.
- Input Parameters:
  - **token**: Authentication token from Step 1
  - **pagelen**: Number of results per page (default: 100)
  - **returnMetadata**: Whether to return call metadata (1 for yes)
  - **start**: Start of search period (format: `YYYY-MM-DD hh:mm` or `YYYY-MM-DD hh:mm:ss`)
  - **end**: End of search period (format: `YYYY-MM-DD hh:mm` or `YYYY-MM-DD hh:mm:ss`)
  - **participant_name**: Name of call participant to search for - OPTIONAL
- Output:
  - **verbacdrlist**: List of calls matching the search criteria, each with metadata including `ccdr_id`

- CURL command to search for calls
```bash
curl --location 'https://mst-vfc.verint.training/verba/api?action=SearchCalls&apiKey=D466035F-CE26-4E6A-BD4E-891A3BD58807&token={token}&pagelen=100&returnMetadata=1&start={start_time}&end={end_time}' \
    --header 'Authorization: Bearer {token}' \
    --header 'Cookie: JSESSIONID=FBC3385B4BAC7BCAE49AE86047C63EE5'
```

- Format of `start_time` and `end_time` parameters:
  - `YYYY-MM-DD hh:mm` or `YYYY-MM-DD hh:mm:ss`

- Token is the value of `token` attribute in the XML response of Step 1.

### Step 3: Retrieve MP3 File

- Description: Retrieve the audio file of a call in mp3 format.
- Input Parameters:
  - **token**: Authentication token from Step 1
  - **cid**: Call ID (ccdr_id) of the call to retrieve
  - **format**: Audio format to retrieve (mp3)
- Output:
  - **audio_file**: Audio file of the call in mp3 format

- CURL command to retrieve MP3 file of a call
```bash
curl --location 'https://mst-vfc.verint.training/verba/api?action=GetMediaEncoded&apiKey=D466035F-CE26-4E6A-BD4E-891A3BD58807&token={token}&cid={ccdr_id}&format=mp3' \
    --header 'Cookie: JSESSIONID=FBC3385B4BAC7BCAE49AE86047C63EE5'
```

- Token is the value of `token` attribute in the XML response of Step 1.

- `ccdr_id` is the value of `ccdr_id` in XML from Step 2, its path is `verbacdrlist` -> `verbacdr` -> `ccdr_id`

- Returns the audio file in the mp3 format.