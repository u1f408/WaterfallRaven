import os
import time
import multiprocessing

from PIL import Image
from pathlib import Path
from flask import Flask, request, Response, abort, jsonify

from wfraven.utils import generate_filename, generate_datehash_and_directory
from wfraven.process import process_image

app = Flask(__name__)

@app.route('/image/add', methods=['POST'])
def image_add():
    start_time = time.time()
    Path("tmp").mkdir(parents=True, exist_ok=True)

    image_type = 'image'
    if request.form.get("isArt"):
        image_type = 'art'
    elif request.form.get("isAudio"):
        image_type = 'audio'
    elif request.form.get("isAvatar"):
        image_type = 'avatar'

    base_dir = Path(app.config['RAVEN_CONFIG']['server']['base_dir'])
    (date_hash, directory) = generate_datehash_and_directory()
    complete_dir = Path('images') / directory
    (base_dir / complete_dir).mkdir(parents=True, exist_ok=True)

    manager = multiprocessing.Manager()
    image_data = manager.dict()

    for image_file in request.files.getlist('images'):
        image_filename = generate_filename()
        image_filename_tmp = Path("tmp") / image_filename

        try:
            image_file.save(image_filename_tmp)
            image = Image.open(image_filename_tmp)

            # Verify the image and get the sizes to use
            try:
                image.verify()
                sizes = process_image.calculate_sizes(image_type, image)
            except:
                image.close()
                return jsonify(
                    status = "failure",
                    reason = "Not a valid image",
                )
            finally:
                image.close()
            
            jobs = []
            for size in sizes:
                p = multiprocessing.Process(
                    target=process_image.process,
                    args=(
                        image_data, 
                        image_type,
                        image_filename_tmp, 
                        size,
                        date_hash,
                        base_dir,
                        complete_dir,
                    ),
                )

                jobs.append(p)
                p.start()


            for p in jobs:
                p.join()

        except Exception:
            pass

        finally:
            os.remove(image_filename_tmp)

    return jsonify(
        status = 'success',
        onServer = app.config['RAVEN_SERVER_ID'],
        imgData = image_data.copy(),
        executionTime = (time.time() - start_time),
        beginTime = start_time,
    )
