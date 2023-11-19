# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, options
from firebase_admin import initialize_app, storage, credentials
import numpy as np
import cv2
from pbn_gen import PbnGen
import json

cred = credentials.Certificate("credentials.json")
app = initialize_app(cred, {"storageBucket": "paint-by-number-21987.appspot.com"})
bucket = storage.bucket()


@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["post"]))
def get_pbn(req: https_fn.Request) -> https_fn.Response:
    object_id = req.args.get("id")

    if not object_id:
        return https_fn.Response(status=400, response="Did not provide object id.")

    try:
        blob = bucket.blob(object_id)
        contents = blob.download_as_string()
    except Exception as e:
        print(e)
        return https_fn.Response(status=405, response="Failed to find image")

    try:
        base_id, _ = object_id.split(".")
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        pbn = PbnGen(img)
        pbn.set_final_pbn()
        svg_output, palette = pbn.output_to_svg()
        palette_str = json.dumps(palette)

        svg_blob = bucket.blob(f"{base_id}.svg")

        svg_blob.upload_from_string(
            str.encode(svg_output), content_type="image/svg+xml"
        )

        json_blob = bucket.blob(f"{base_id}.json")

        json_blob.upload_from_string(
            str.encode(palette_str), content_type="application/json"
        )
    except Exception as e:
        print(e)
        return https_fn.Response(status=500, response="Failed to process image")

    return https_fn.Response("OK")
