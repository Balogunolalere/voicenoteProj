
Audio Note API
==============

This is an API for uploading and listening to audio notes, built with FastAPI and deployed on Deta.

Features
--------

*   Upload audio notes (mp3, wav, ogg, flac, m4a, wma, aac, opus, ogx, oga)
*   Get metadata for all notes
*   Get metadata for a specific note by ID
*   Stream and listen to a note by ID
*   Download a note by ID
*   Delete a note by ID

Endpoints
---------

### Upload Note



`POST /note`

Upload an audio file to create a new note.

Request body:

*   `file`: Audio file (required)

Returns:

*   `file_id`: Unique ID of the uploaded file
*   `upload_date`: Date when file was uploaded
*   `format`: Audio format
*   `duration_seconds`: Length of audio in seconds
*   `mime_type`: MIME type of audio file
*   `encoder`: Encoder used to encode the audio

### Get All Notes Metadata



`GET /notes/metadata`

Get metadata of all uploaded notes.

Returns array of:

*   `file_id`: Unique ID of the uploaded file
*   `upload_date`: Date when file was uploaded
*   `format`: Audio format
*   `duration_seconds`: Length of audio in seconds
*   `mime_type`: MIME type of audio file
*   `encoder`: Encoder used to encode the audio

### Get Note Metadata By ID



`GET /note/{file_id}/metadata`

Get metadata of a specific note by ID.

Path parameters:

*   `file_id`: ID of the note

Returns:

*   `file_id`: Unique ID of the uploaded file
*   `upload_date`: Date when file was uploaded
*   `format`: Audio format
*   `duration_seconds`: Length of audio in seconds
*   `mime_type`: MIME type of audio file
*   `encoder`: Encoder used to encode the audio

### Listen to Note By ID



`GET /note/listen/{file_id}`

Stream an audio note to listen by ID.

Path parameters:

*   `file_id`: ID of the note

Returns audio stream.

### Download Note By ID



`GET /note/download/{file_id}`

Download an audio note by ID.

Path parameters:

*   `file_id`: ID of the note

Returns audio file for download.

### Delete Note By ID



`DELETE /note/{file_id}`

Delete an audio note by ID.

Path parameters:

*   `file_id`: ID of the note

Returns:

*   `message`: Confirmation message that deletion is in progress.

Deployment
----------

This API is deployed on Deta. The following environment variables need to be configured:

*   `PROJECT_KEY`: Deta project key
*   `DRIVE_PROJECT_NAME`: Name of Deta Drive to store audio files
*   `BASE_PROJECT_NAME`: Name of Deta Base to store metadata

Local Development
-----------------

### Prerequisites

*   Python 3.6+
*   virtualenv

### Install Dependencies



`virtualenv env && source env/bin/activate && pip install -r requirements.txt`

### Run Server



`uvicorn main:app --reload`

This will start the API server on [http://localhost:8000](http://localhost:8000).

The API can be tested locally using Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) or any HTTP client like Postman or cURL.


