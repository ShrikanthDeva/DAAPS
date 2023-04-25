import cv2
import os
from os import listdir
import sys
import numpy
from enhance import image_enhance
from skimage.morphology import skeletonize, thin

# os.chdir("/app/")

def removedot(invertThin):
    temp0 = numpy.array(invertThin[:])
    temp0 = numpy.array(temp0)
    temp1 = temp0/255
    temp2 = numpy.array(temp1)
    temp3 = numpy.array(temp2)

    enhanced_img = numpy.array(temp0)
    filter0 = numpy.zeros((10,10))
    W,H = temp0.shape[:2]
    filtersize = 6

    for i in range(W - filtersize):
        for j in range(H - filtersize):
            filter0 = temp1[i:i + filtersize,j:j + filtersize]

            flag = 0
            if sum(filter0[:,0]) == 0:
                flag +=1
            if sum(filter0[:,filtersize - 1]) == 0:
                flag +=1
            if sum(filter0[0,:]) == 0:
                flag +=1
            if sum(filter0[filtersize - 1,:]) == 0:
                flag +=1
            if flag > 3:
                temp2[i:i + filtersize, j:j + filtersize] = numpy.zeros((filtersize, filtersize))
    return temp2


def get_descriptors(img):
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	img = clahe.apply(img)
	img = image_enhance.image_enhance(img)
	img = numpy.array(img, dtype=numpy.uint8)
	# Threshold
	ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
	# Normalize to 0 and 1 range
	img[img == 255] = 1

	#Thinning
	skeleton = skeletonize(img)
	skeleton = numpy.array(skeleton, dtype=numpy.uint8)
	skeleton = removedot(skeleton)
	# Harris corners
	harris_corners = cv2.cornerHarris(img, 3, 3, 0.04)
	harris_normalized = cv2.normalize(harris_corners, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32FC1)
	threshold_harris = 125
	# Extract keypoints
	keypoints = []
	for x in range(0, harris_normalized.shape[0]):
		for y in range(0, harris_normalized.shape[1]):
			if harris_normalized[x][y] > threshold_harris:
				keypoints.append(cv2.KeyPoint(y, x, 1))
	# Define descriptor
	orb = cv2.ORB_create()
	# Compute descriptors
	_, des = orb.compute(img, keypoints)
	return (keypoints, des)


def finger_find():

	test_image = r"C:/Users/shri1/sih/sih-project-2022/sih-project-final/finger_function/database/fingerprint.tif"
	print(test_image)
	img1 = cv2.imread(test_image, cv2.IMREAD_GRAYSCALE)
	# cv2.imshow("vhvg",img1)
	kp1, des1 = get_descriptors(img1)


	folder_dir = r"C:/Users/shri1/sih/sih-project-2022/sih-project-final/finger_function/fingerprints"
	temp_fingerprints = []
	for images in os.listdir(folder_dir):
    # check if the image ends with tif
		if (images.endswith(".tif")):
			temp_fingerprints.append(images)

	for i in range(len(temp_fingerprints)):

		image_name = r"C:/Users/shri1/sih/sih-project-2022/sih-project-final/finger_function/fingerprints/" + temp_fingerprints[i]
		img2 = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
		kp2, des2 = get_descriptors(img2)

		# Matching between descriptors
		bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
		matches = sorted(bf.match(des1, des2), key= lambda match:match.distance)
		
		# Calculate score
		score = 0
		for match in matches:
			score += match.distance
		score_threshold = 33
		if score/len(matches) < score_threshold:
			person_name = temp_fingerprints[i]
			person_name = person_name.rsplit(".",1)[0]
			print("owner of finger print =",person_name)
			return person_name
			break
	else :
		print("Fingerprint does not match.")

# if __name__ == "__main__":
# 	try:
# 		main()
# 	except:
# 		raise
