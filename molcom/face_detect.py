import pickle
from dataclasses import dataclass
from threading import Event

import cv2


@dataclass
class Face:
    name: str
    _id: int
    probability: float


def detect_face(evt: Event) -> None:
    """
    카메라를 통해 얼굴을 인식해 관련 정보를 event-set합니다.
    """

    face_cascade = cv2.CascadeClassifier(
        "./cascade/haarcascade_frontalface_default.xml"
    )
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("model/face_model.yml")

    with open("face_ids.pickle", "rb") as f:
        stored_faces: dict[int, str] = pickle.load(f)

    print(stored_faces)
    names = ["Unknown"] + list(stored_faces.values())
    print(names)
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        is_there_unkown = False

        if not ret:
            raise RuntimeError("카메라를 찾을 수 없습니다.")

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            _id, confidence = recognizer.predict(gray[y : y + h, x : x + w])

            if confidence < 55:
                name = names[_id]
                confidence_str = f"{round(100 - confidence)}%"
            else:
                name = "Unknown"
                confidence_str = f"{round(100 - confidence)}%"
                is_there_unkown = True

            cv2.putText(
                frame,
                name,
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                frame,
                confidence_str,
                (x + 5, y + h - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 0),
                1,
            )

        if is_there_unkown:
            evt.set()

        # cv2.imshow("Face", frame)

        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

    cam.release()
    cv2.destroyAllWindows()
