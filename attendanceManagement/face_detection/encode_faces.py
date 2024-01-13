from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
from django.conf import settings
from django.core.files.storage import default_storage

dataset_path = os.path.join(settings.MEDIA_ROOT, "datasets")
encodings_path = "attendanceManagement/face_detection/encodings.pickle"
detection_method = "hog"  # or "hog"


def quantify_faces():
    print("[INFO] quantifying faces...")
    image_paths = list(paths.list_images(dataset_path))
    # initialize the list of known encodings and known names
    known_encodings = []
    known_names = []

    # loop over the image paths
    for (i, imagePath) in enumerate(image_paths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1, len(image_paths)))
        name = imagePath.split(os.path.sep)[-2]
        # load the input image and convert it from BGR (OpenCV ordering)
        # to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb, model=detection_method)
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)
        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and
            # encodings
            known_encodings.append(encoding)
            known_names.append(name)

    # dump the facial encodings + names to disk
    print("[INFO] serializing encodings...")
    data = {"encodings": known_encodings, "names": known_names}
    f = open(encodings_path, "wb")
    f.write(pickle.dumps(data))
    f.close()
    print("[INFO] finished serializing encodings...")
    return "Finished serializing encodings"
