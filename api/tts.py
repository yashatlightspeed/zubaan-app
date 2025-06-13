import io
from gtts import gTTS
from pydub import AudioSegment
from flask import Request, send_file

def handler(request: Request):
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'en')
    speed = float(data.get('speed', 1.0))
    pitch = float(data.get('pitch', 1.0))

    if not text.strip():
        return {"error": "No text provided"}, 400

    # Generate TTS audio
    tts = gTTS(text=text, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    audio = AudioSegment.from_file(buf, format="mp3")

    # Adjust speed
    if speed != 1.0:
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        }).set_frame_rate(audio.frame_rate)

    # Adjust pitch
    if pitch != 1.0:
        new_sample_rate = int(audio.frame_rate * pitch)
        audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        audio = audio.set_frame_rate(44100)

    # Export to BytesIO
    out_buf = io.BytesIO()
    audio.export(out_buf, format='mp3')
    out_buf.seek(0)
    return send_file(out_buf, mimetype='audio/mpeg', as_attachment=True, download_name='speech.mp3')
