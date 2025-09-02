from fileinput import filename
from flask import Flask, render_template, request, redirect, send_from_directory, send_file
# from werkzeug import secure_filename
import wave, os, time, zipfile
import tempfile

from steno import encode, decode, phase_encode, phase_decode
from img_en import lsbimg_decode, lsbimg_encode, mask
from text_en import txt_encode, txt_decode
from vid import encode_video, decode_video

app = Flask(__name__)

uploads_dir = tempfile.gettempdir()

os.makedirs(os.path.join(uploads_dir, "steno"), exist_ok=True)
uploads_dir = os.path.join(uploads_dir, "steno")

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return render_template('./index.html')
    elif request.method == 'POST':
        return redirect('/')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        
        profile = request.files['file']
        # Use secure filename or just the filename directly
        path = os.path.join(uploads_dir, profile.filename)

        print(list(request.form.keys()))
        type = request.form['type']
 
        profile.save(path)
        
        # IMAGE STEGANOGRAPHY
        if(type in ["lsbimg", "mask", "enimg"]):
            if(type == "lsbimg"):
                message = request.form['message']
                lsbimg_encode(path, message)
                # Return the encoded image
                return send_file(
                    os.path.join(uploads_dir, profile.filename),
                    # mimetype='image/png',
                    as_attachment=True,
                    download_name=profile.filename[:-4] + "_encoded" + profile.filename[-4:]
                )
            elif(type == "mask"):        
                maskpath = os.path.join(uploads_dir, request.files['maskfile'].filename)
                request.files['maskfile'].save(maskpath)
                mask(path, maskpath)
                return send_file(
                    os.path.join(uploads_dir, profile.filename),
                    as_attachment=True,
                    download_name=profile.filename[:-4] + "_masked" + profile.filename[-4:]
                )
            else:
                pass
                   
        # AUDIO STEGANOGRAPHY   
        elif(type in ["phase", "lsb", "parity"]):
            audio = wave.open(path, mode="rb")
            
            if(type == "phase"):
                message = request.form['message']
                phase_encode(audio, path, profile.filename, message)
            elif(type == "lsb"):
                message = request.form['message']
                encode(audio, profile.filename, message)
            
            return send_file(os.path.join(uploads_dir, profile.filename + "encoded"),
                mimetype='audio/wav',
                as_attachment=True,
                download_name=profile.filename + "_encoded.wav"
            )
            
        # TEXT STEGANOGRAPHY
        elif(type in ["snow", "lookalike", "zw"]):
            f = open(path, "r", encoding="utf-8")
            data = f.read()
            f.close()
            message = request.form['message']
            
            if(type == "zw"):  # Fixed this - was "zero" in original
                new_data = txt_encode(data, message.encode("ascii"), "zw", binary=True)
            elif(type == "snow"):
                new_data = txt_encode(data, message.encode("ascii"), "snow", binary=True)
            else:  # lookalike
                new_data = txt_encode(data, message.encode("ascii"), "lookalike", binary=True)
                
            with open(path + "_encoded", "w", encoding="utf-8") as f:
                f.write(new_data)
                f.close()
                
            return send_file(os.path.join(uploads_dir, profile.filename + "_encoded"),
                mimetype='text/plain',
                as_attachment=True,
                download_name=profile.filename + "_encoded.txt"
            )
    else:
        return redirect('/')

@app.route('/decode', methods=['POST'])
def decoder():
    if request.method == 'POST':
        
        profile = request.files['file']
        type = request.form['type']

        path = os.path.join(uploads_dir, profile.filename)
        
        profile.save(path)
        
        # IMAGE STEGANOGRAPHY
        if(type in ["lsbimg", "rpeimg", "enimg"]):
            if(type == "lsbimg"):
                text = lsbimg_decode(path)
                print("got text", text)
            elif(type == "mask"):
                text = "Mask decoding not implemented"
            else:
                text = "Method not implemented"
                
        # AUDIO STEGANOGRAPHY
        elif(type in ["phase", "lsb", "parity"]):
            audio = wave.open(path, mode="rb")
            if(type == "phase"):
                text = phase_decode(audio, profile.filename, path)
            elif(type == "lsb"):
                text = decode(audio, profile.filename)
            else:
                text = "Method not implemented"

        # TEXT STEGANOGRAPHY
        elif(type in ["snow", "lookalike", "zw"]):
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
                f.close()
            text = txt_decode(data, type, binary=True)
            print("decoded==> ", str(text))
        else:
            text = "Unknown method"
            
        return render_template('./index.html', deciphered=text)
    else:
        return redirect('/')