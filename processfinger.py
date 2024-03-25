import os

import cv2
def finger():
    sample = cv2.imread("C:/Users/shri1/sih/sih-project-2022/sih-project-final/static/fingerprint.bmp")

    best_score = 0
    filename = None
    image = None
    kp1, kp2, mp = None, None, None
    for file in [file for file in os.listdir("C:/Users/shri1/sih/sih-project-2022/sih-project-final/fingerdata")]:
        fingerprint_image = cv2.imread("C:/Users/shri1/sih/sih-project-2022/sih-project-final/fingerdata" + file)
        sift = cv2.SIFT_create()

        keypoints_1, descriptors_1 = sift.detectAndCompute(sample, None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(fingerprint_image, None)

        matches = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 10},
                                        {}).knnMatch(descriptors_1, descriptors_2, k=2)

        match_points = []

        for p, q in matches:
            if p.distance < 0.1 * q.distance:
                match_points.append(p)

        keypoints = 0
        if len(keypoints_1) < len(keypoints_2):
            keypoints = len(keypoints_1)
        else:
            keypoints = len(keypoints_2)

        if len(match_points) / keypoints * 100 > best_score:
            best_score = len(match_points) / keypoints * 100
            filename = file
            image = fingerprint_image
            kp1, kp2, mp = keypoints_1, keypoints_2, match_points

    print("BEST MATCH: " + filename)
    print("SCORE: " + str(best_score))


    return filename
    