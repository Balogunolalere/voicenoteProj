import mutagen
from datetime import timedelta, datetime

# Replace 'example.mp3' with the path to your audio file
audio = mutagen.File("/home/doombuggy_/Downloads/Human.mp3")

# Get the duration in seconds
duration_seconds = audio.info.length

# Convert the duration from seconds to a timedelta object
duration_timedelta = timedelta(seconds=duration_seconds)

# Convert the timedelta object to a datetime object
duration_datetime = datetime(1, 1, 1) + duration_timedelta

# Format the duration as "minutes:seconds"
song_duration = duration_datetime.strftime('%M:%S')

print(f"Song Duration: {song_duration}")