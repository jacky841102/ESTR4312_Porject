from flask import request, render_template, redirect, url_for
from flask_login import login_required, current_user
from . import effect
from app.worker import *
from .form import *
from werkzeug.utils import secure_filename
from app import app
from uuid import uuid4

@effect.route('/blending', methods=['GET', 'POST'])
@login_required
def blending():
    form = BlendingForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            foreImg, backImg, mask = form.foreImg.data, form.backImg.data, form.mask.data
            foreImgName, backImgName, maskName, writeName = uniqueName(), uniqueName(), uniqueName(), uniqueName()

            foreImgPath = os.path.join(app.config['UPLOAD_FOLDER'], foreImgName)
            backImgPath = os.path.join(app.config['UPLOAD_FOLDER'], backImgName)
            maskPath = os.path.join(app.config['UPLOAD_FOLDER'], maskName)
            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

            foreImg.save(foreImgPath)
            backImg.save(backImgPath)
            mask.save(maskPath)

            task_id = poissonBlending.delay(foreImgName,
                                            backImgName,
                                            maskName,
                                            writeName,
                                            current_user.id).task_id
            return task_id
    return render_template('effect.jinja2', form=form, effect='blending')

@effect.route('/blur', methods=['GET', 'POST'])
@login_required
def blur():
    form = BlurForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            img = form.img.data
            imgName, writeName = uniqueName(), uniqueName()

            imgPath = os.path.join(app.config['UPLOAD_FOLDER'], imgName)
            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

            img.save(imgPath)

            task_id = gaussianBlur.delay(imgName, writeName, current_user.id).task_id
            return task_id

    return render_template('effect.jinja2', form=form, effect='blur')

@effect.route('/edge', methods=['GET', 'POST'])
@login_required
def edge():
    form = EdgeForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            img = form.img.data
            imgName, writeName = uniqueName(), uniqueName()

            imgPath = os.path.join(app.config['UPLOAD_FOLDER'], imgName)
            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

            img.save(imgPath)

            task_id = laplacian.delay(imgName, writeName, current_user.id).task_id

            return task_id
    return render_template('effect.jinja2', form=form, effect='edge')

@effect.route('/hdr', methods=['GET', 'POST'])
@login_required
def HDR():
    form = HDRForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            img1 = form.img1.data
            img2 = form.img2.data
            img3 = form.img3.data

            img1Name = uniqueName()
            img2Name = uniqueName()
            img3Name = uniqueName()
            writeName = uniqueName()

            imgNames = [img1Name, img2Name, img3Name]

            imgPaths = [os.path.join(app.config['UPLOAD_FOLDER'], img1Name),
                        os.path.join(app.config['UPLOAD_FOLDER'], img2Name),
                        os.path.join(app.config['UPLOAD_FOLDER'], img3Name)]

            exposures = [float(form.expo1.data), float(form.expo2.data), float(form.expo3.data)]

            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName)

            img1.save(imgPaths[0])
            img2.save(imgPaths[1])
            img3.save(imgPaths[2])

            task_id = hdr.delay(imgNames, exposures, writeName, current_user.id).task_id
            return task_id


    return render_template('effect.jinja2', form=form, effect='hdr')

def uniqueName():
    return uuid4().hex + '.jpg'
