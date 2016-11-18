import base64, os, cv2
import numpy as np
import scipy
from scipy.sparse import linalg
from celery import Celery
from io import BytesIO
from app import db, app
from app.models import User, Photo, Tag
from flask import url_for
import requests
import os

worker = Celery('tasks',
              broker='amqp://guest@localhost//',
              backend='redis://localhost')

api_key = 'acc_bcaa852bcf36aeb'
api_secret = '26070208e4010423b321281902c5dd4f'

@worker.task
def poissonBlending(foreImgName, backImgName, maskName, writeName, user_id):
    foreImgPath = os.path.join(app.config['UPLOAD_FOLDER'], foreImgName)
    backImgPath = os.path.join(app.config['UPLOAD_FOLDER'], backImgName)
    maskPath = os.path.join(app.config['UPLOAD_FOLDER'], maskName)
    writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

    foreImg = cv2.imread(foreImgPath)
    backImg = cv2.imread(backImgPath)
    maskImg = cv2.imread(maskPath)

    result = solveEulerLagrange(foreImg, backImg, maskImg)
    cv2.imwrite(writePath, result)

    photo_id = addToDB(writeName, 'blending', user_id)
    createTumbnail(writeName, photo_id)

    autoTag.delay(writePath, photo_id)

    os.remove(foreImgPath)
    os.remove(backImgPath)
    os.remove(maskPath)

@worker.task
def gaussianBlur(imgName, writeName, user_id):
    imgPath = os.path.join(app.config['UPLOAD_FOLDER'], imgName)
    writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

    img = cv2.imread(imgPath)

    result = cv2.GaussianBlur(img, (5,5), 0)
    cv2.imwrite(writePath, result)

    photo_id = addToDB(writeName, 'blur', user_id)
    createTumbnail(writeName, photo_id)

    autoTag.delay(writePath, photo_id)

    os.remove(imgPath)

@worker.task
def laplacian(imgName, writeName, user_id):
    imgPath = os.path.join(app.config['UPLOAD_FOLDER'], imgName)
    writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

    img = cv2.imread(imgPath, 0)

    result = cv2.Laplacian(img, cv2.CV_64F)
    cv2.imwrite(writePath, result)

    photo_id = addToDB(writeName, 'edge', user_id)
    createTumbnail(writeName, photo_id)

    autoTag.delay(writePath, photo_id)

    os.remove(imgPath)

@worker.task
def hdr(imgNames, exposures, writeName, user_id):
    writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

    imgPaths = [os.path.join(app.config['UPLOAD_FOLDER'], imgName) for imgName in imgNames]

    images = [cv2.imread(imgPath) for imgPath in imgPaths]
    imgs = imageAlignment(images)

    merge_debvec = cv2.createMergeDebevec()

    exposures = np.array(exposures, dtype=np.float32)
    hdr_debvec = merge_debvec.process(imgs, times=exposures.copy())

    tonemap = cv2.createTonemapDurand(gamma=2)
    res = tonemap.process(hdr_debvec)

    cv2.imwrite(writePath, res * 255)
    photo_id = addToDB(writeName, 'HDR', user_id)
    createTumbnail(writeName, photo_id)

    autoTag.delay(writePath, photo_id)

    for path in imgPaths:
        os.remove(path)

@worker.task
def autoTag(imgPath, photo_id):
    content_res = requests.post('https://api.imagga.com/v1/content',
            files={'image': open(imgPath, 'rb')}, auth=(api_key, api_secret))
    content_id = content_res.json()['uploaded'][0]['id']

    tag_res = requests.get('https://api.imagga.com/v1/tagging',
            params={'content': content_id, 'limit': 5},
            auth=(api_key, api_secret))

    results = tag_res.json()['results']

    photo = Photo.query.get(photo_id)

    tags = results[0]['tags']

    for tag in tags:
        if float(tag['confidence']) >= 25:
            photo.tags.append(Tag(attr=tag['tag']))

    db.session.commit()

@worker.task
def createTumbnail(imgName, photo_id):
    tnName = 'tn-' + imgName

    imgPath = os.path.join(app.config['UPLOAD_FOLDER'], imgName)
    tnPath = os.path.join(app.config['UPLOAD_FOLDER'], tnName)

    img = cv2.imread(imgPath)

    H, W, _ = img.shape

    W = int(float(W) / H * 200)
    H = 200

    tn = cv2.resize(img, (W, H))
    cv2.imwrite(tnPath, tn)

    with app.app_context():
        url = url_for('album.uploaded_file', filename=tnName)
        photo = Photo.query.get(photo_id)
        photo.tn_url = url
        db.session.commit()

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

def addToDB(writeName, attr, user_id):
    with app.app_context():
        url = url_for('album.uploaded_file', filename=writeName)
        user = User.query.get(user_id)
        photo = Photo(url=url, tn_url=url, filename=writeName)
        user.album.append(photo)
        photo.tags.append(Tag(attr=attr))
        db.session.commit()
        return photo.id

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
