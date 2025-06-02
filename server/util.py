import joblib
import json
import numpy as np
import base64
import cv2
import os
from wavelet import w2d

__class_name_to_number = {}
__class_number_to_name = {}
__model = None


def cleanup_class_name(raw_name):
    name = raw_name.lower().replace("croped", "").replace(" - google search", "").strip()
    name = name.replace(" ", "_")
    return name


def classify_image(image_base64_data, file_path=None):
    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)

    if not imgs:
        return [{"error": "No valid face with 2 eyes found in the image"}]

    result = []
    for img in imgs:
        try:
            scalled_raw_img = cv2.resize(img, (32, 32))
            img_har = w2d(img, "db1", 5)
            scalled_img_har = cv2.resize(img_har, (32, 32))
            combined_img = np.vstack(
                (scalled_raw_img.reshape(32 * 32 * 3, 1), scalled_img_har.reshape(32 * 32, 1))
            )

            final = combined_img.reshape(1, -1).astype(float)
            prediction = __model.predict(final)[0]
            probability = np.around(__model.predict_proba(final) * 100, 2).tolist()[0]

            result.append(
                {
                    "class": cleanup_class_name(class_number_to_name(prediction)),
                    "class_probability": probability,
                    "class_dictionary": {
                        cleanup_class_name(k): v for k, v in __class_name_to_number.items()
                    },
                }
            )
        except Exception as e:
            result.append({"error": str(e)})

    return result


def class_number_to_name(class_num):
    return __class_number_to_name.get(class_num, "Unknown")


def load_saved_artifacts():
    print("Loading saved artifacts...")

    global __class_name_to_number
    global __class_number_to_name
    global __model

    base_path = os.path.dirname(__file__)
    class_dict_path = os.path.join(base_path, "artifacts", "class_dictinary.json")
    model_path = os.path.join(base_path, "artifacts", "saved_model.pkl")

    with open(class_dict_path, "r") as f:
        __class_name_to_number = json.load(f)
        __class_number_to_name = {v: k for k, v in __class_name_to_number.items()}

    if __model is None:
        with open(model_path, "rb") as f:
            __model = joblib.load(f)

    print("Artifacts loaded successfully.")


def get_cv2_image_from_base64_string(b64str):
    try:
        encoded_data = b64str.split(",")[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None


def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    base_path = os.path.dirname(__file__)
    face_cascade_path = os.path.join(
        base_path, "..", "model", "open.ui", "haarcascade", "haarcascade_frontalface_default.xml"
    )
    eye_cascade_path = os.path.join(
        base_path, "..", "model", "open.ui", "haarcascade", "haarcascade_eye.xml"
    )

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)

    if img is None:
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    cropped_faces = []
    for x, y, w, h in faces:
        roi_gray = gray[y : y + h, x : x + w]
        roi_color = img[y : y + h, x : x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            cropped_faces.append(roi_color)

    return cropped_faces


def get_b64_test_image_for_virat():
    base_path = os.path.dirname(__file__)
    test_image_path = os.path.join(base_path, "b64.txt")
    with open(test_image_path) as f:
        return f.read()


if __name__ == "__main__":
    load_saved_artifacts()
    print(classify_image(None, "/home/ayush/ishu/Sport_person_classifier/ui/test_image/sharapova_3.jpg"))
