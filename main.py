from fastapi import FastAPI, File, UploadFile, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from deta import Deta
import uuid
from datetime import datetime
import mutagen
from io import BytesIO
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

DETA_PROJECT_KEY = os.getenv("PROJECT_KEY")
DRIVE_PROJECT_NAME = os.getenv("DRIVE_PROJECT_NAME")
BASE_PROJECT_NAME = os.getenv("BASE_PROJECT_NAME")


app = FastAPI(
    title="Note API🎤",
    description="A simple API to upload and listen to audio notes",
    version="0.1.0"
)
deta = Deta(DETA_PROJECT_KEY)


drive = deta.Drive(DRIVE_PROJECT_NAME)
base = deta.Base(BASE_PROJECT_NAME)



async def upload_file_to_drive(file_id: str, file_content: BytesIO):
    drive.put(file_id, file_content)


async def upload_file_metadata_to_base(file_id: str, file_upload_date: str, audio_format: str, audio_duration: float, audio_mime_type: str, audio_encoder: str, file_size: int):
    base.put({
        "file_id": file_id,
        "upload_date": file_upload_date,
        "format": audio_format,
        "duration_seconds": audio_duration,
        "mime_type": audio_mime_type,
        "encoder": audio_encoder,
        "file_size_in_bytes": file_size
    })


@app.post("/note")
async def create_note(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
    # make sure the file is an audio file
    supported_audio_formats = ["mp3", "wav", "ogg", "flac", "m4a", "wma", "aac", "opus", "ogx", "oga"]
    if file.filename.split(".")[-1] not in supported_audio_formats:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported audio format")
    file_id = str(uuid.uuid4())
    file_upload_date = datetime.now().date().strftime("%Y-%m-%d")
    try:
        # create two in-memory file-like objects from the uploaded file bytes
        content1 = BytesIO(await file.read())
        content2 = BytesIO(content1.getbuffer())
        # get the audio file duration from the first object
        audio = mutagen.File(content1)
        # get pprint data from mutagen 
        audio_pprint = audio.pprint()
        # extract required information from audio_pprint
        audio_pprint_lines = audio_pprint.split("\n")
        audio_format = audio_pprint_lines[0].split(",")[0]
        audio_duration = float(audio_pprint_lines[0].split(",")[1].split()[0])
        audio_mime_type = audio_pprint_lines[0].split("(")[1].split(")")[0]
        audio_encoder = audio_pprint_lines[1].split("=")[1]

        # calculate file size
        file_size = content1.getbuffer().nbytes

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'File upload failed: {e}')

    # add background tasks to upload file to Drive and metadata to Base
    background_tasks.add_task(upload_file_to_drive, file_id, content2)
    background_tasks.add_task(upload_file_metadata_to_base, file_id, file_upload_date, audio_format, audio_duration, audio_mime_type, audio_encoder, file_size)

    return {
        "file_id": file_id,
        "upload_date": file_upload_date,
        "format": audio_format,
        "duration_seconds": audio_duration,
        "mime_type": audio_mime_type,
        "encoder": audio_encoder,
        "file_size_in_bytes": file_size
    }

@app.get("/notes/metadata")
async def get_notes():
    try:
        notes = base.fetch()
        if not notes:
            return []
        return notes
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/note/{file_id}/metadata")
async def get_note_by_id(file_id: str):
    if not drive.get(file_id):
        raise HTTPException(status_code=404, detail="File with id not found")    
    try:
        note = base.fetch({"file_id": file_id})
        return note
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/note/listen/{file_id}")
async def listen_to_note_by_id(file_id: str):
    if not drive.get(file_id):
        raise HTTPException(status_code=404, detail="File with id not found")
    try:
        note = drive.get(file_id)
        return StreamingResponse(note.iter_chunks(1024), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/note/download/{file_id}")
async def download_note_by_id(file_id: str):
    if not drive.get(file_id):
        raise HTTPException(status_code=404, detail="File with id not found")
    try:
        note = drive.get(file_id)
        metadeta = base.fetch({"file_id": file_id}).items[0]
        return StreamingResponse(note.iter_chunks(1024), media_type="audio/mpeg", headers={"Content-Disposition": f"attachment; filename={metadeta['file_id']}.{metadeta['format']}"})
    except Exception as e:
        return {"error": str(e)}
    
@app.delete("/notes/{file_id}")
async def delete_note(background_tasks: BackgroundTasks, file_id: str):
    if not drive.get(file_id):
        raise HTTPException(status_code=404, detail="File with id not found")
    id = base.fetch({"file_id": file_id}).items[0]['key']
    try:
        # add background task to delete file from Drive and metadata from Base
        background_tasks.add_task(drive.delete, file_id)
        background_tasks.add_task(base.delete, id)
        return {"message": "File deletion in progress"}
    except Exception as e:
        return {"error": str(e)}
    
# end point to search by date
@app.get("/notes/search/{date}")
async def search_by_date(date: str):
    try:
        notes = base.fetch({"upload_date": date})
        if not notes:
            return []
        return notes
    except Exception as e:
        return {"error": str(e)}
