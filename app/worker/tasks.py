import base64, os, cv2
import numpy as np
import scipy
from scipy.sparse import linalg
from celery import Celery
from io import BytesIO
from app import db
from app.models import User, Photo, Tag

worker = Celery('tasks',
              broker='amqp://guest@localhost//',
              backend='redis://localhost')

@worker.task
def poissonBlending(foreImgPath, backImgPath, maskPath, writePath, user_id):
    foreImg = cv2.imread(foreImgPath)
    backImg = cv2.imread(backImgPath)
    maskImg = cv2.imread(maskPath)
    result = solveEulerLagrange(foreImg, backImg, maskImg)
    cv2.imwrite(writePath, result)
    addToDB(writePath, 'blending', user_id)

@worker.task
def gaussianBlur(imgPath, writePath, user_id):
    img = cv2.imread(imgPath)
    result = cv2.GaussianBlur(img, (5,5), 0)
    cv2.imwrite(writePath, result)
    addToDB(writePath, 'blur', user_id)

@worker.task
def laplacian(imgPath, writePath, user_id):
    img = cv2.imread(imgPath, 0)
    result = cv2.Laplacian(img, cv2.CV_64F)
    cv2.imwrite(writePath, result)
    addToDB(writePath, 'edge', user_id)

@worker.task
def hdr(imgPaths, exposures, writePath, user_id):
    images = [cv2.imread(imgPath) for imgPath in imgPaths]

    imgs = imageAlignment(images)

    merge_debvec = cv2.createMergeDebevec()

    exposures = np.array(exposures, dtype=np.float32)
    hdr_debvec = merge_debvec.process(imgs, times=exposures.copy())

    tonemap = cv2.createTonemapDurand(gamma=2)
    res = tonemap.process(hdr_debvec)

    cv2.imwrite(writePath, res * 255)
    addToDB(writePath, 'HDR', user_id)

def solveEulerLagrange(foreImg, backImg, mask):

    laplacianFore = cv2.Laplacian(foreImg, cv2.CV_64F)
    laplacianBack = cv2.Laplacian(backImg, cv2.CV_64F)

    rows = backImg.shape[0]
    cols = backImg.shape[1]
    channels = backImg.shape[2]
    numRowsInA = alls = rows * cols

    R, C = len(mask), len(mask[0])
    result = np.zeros((R, C, channels))

    for c in range(channels):
        B = np.zeros((numRowsInA, 1))
        I = []
        J = []
        S = []
        for i in range(R):
            for j in range(C):
                n = i * C + j
                if mask[i, j, c] == 0:
                    B[n, 0] = backImg[i,j,c]
                    I.append(n)
                    J.append(n)
                    S.append(1)
                else:
                    #mixed gradient
                    B[n, 0] = laplacianFore[i, j, c] + laplacianBack[i,j,c]
                    I.append(n)
                    J.append(n)
                    S.append(-4)
                    for nn in [n+1, n-1, n+C, n-C]:
                        if 0 <= nn < alls:
                            I.append(n)
                            J.append(nn)
                            S.append(1)
        I = np.array(I)
        J = np.array(J)
        S = np.array(S)
        A = scipy.sparse.coo_matrix((S, (I, J)), shape=(numRowsInA, alls))
        # solve Ax=B with least square
        D = scipy.sparse.linalg.cg(A, B)

        img = D[0].reshape((R, C))
        result[:,:,c] = img
    return result

def addToDB(url, attr, user_id):
    user = User.query.get(user_id)
    photo = Photo(url=url)
    user.album.append(photo)
    photo.tags.append(Tag(attr=attr))
    db.session.commit()

def imageAlignment(images):

    MIN_MATCH_COUNT = 10
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    dst_img = images[0]
    src_imgs = images[1:]

    result = [dst_img]

    sift = cv2.xfeatures2d.SIFT_create()

    dst_kp, dst_des = sift.detectAndCompute(dst_img, None)
    for src_img in src_imgs:
        src_kp, src_des = sift.detectAndCompute(src_img, None)

        matches = flann.knnMatch(src_des, dst_des, k=2)

        good = []
        for m,n in matches:
            if m.distance <= 0.7*n.distance:
                good.append(m)

        src_pts = np.float32([src_kp[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([dst_kp[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()

        im_out = cv2.warpPerspective(src_img, M, (dst_img.shape[1], dst_img.shape[0]))

        result.append(im_out)
    return result
