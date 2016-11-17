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
