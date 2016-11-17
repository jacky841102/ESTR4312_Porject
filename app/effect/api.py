from flask import request, render_template
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
            foreImgName, backImgName, maskName, writeName = uuid4().hex, uuid4().hex, uuid4().hex, uuid4().hex

            foreImgPath = os.path.join(app.config['UPLOAD_FOLDER'], foreImgName + '.jpg')
            backImgPath = os.path.join(app.config['UPLOAD_FOLDER'], backImgName + '.jpg')
            maskPath = os.path.join(app.config['UPLOAD_FOLDER'], maskName + '.jpg')
            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName + '.jpg')

            foreImg.save(foreImgPath)
            backImg.save(backImgPath)
            mask.save(maskPath)

            task_id = poissonBlending.delay(foreImgPath,
                                            backImgPath,
                                            maskPath,
                                            writePath,
                                            current_user.id).task_id
            return task_id
    return render_template('blending.jinja2', form=form)

@effect.route('/blur', methods=['GET', 'POST'])
@login_required
def blur():
    form = BlurForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            img = form.img.data
            imgName, writeName = uuid4().hex, uuid4().hex

            imgPath = os.path.join(app.config['UPLOAD_FOLDER'], imgName + '.jpg')
            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName + '.jpg')

            img.save(imgPath)

            task_id = gaussianBlur.delay(imgPath, writePath, current_user.id).task_id
            return task_id

    return render_template('blur.jinja2', form=form)


@effect.route('/edge', methods=['GET', 'POST'])
@login_required
def edge():
    form = EdgeForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            img = form.img.data
            imgName, writeName = uuid4().hex, uuid4().hex

            imgPath = os.path.join(app.config['UPLOAD_FOLDER'], imgName + '.jpg')
            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName + '.jpg')

            img.save(imgPath)

            task_id = laplacian.delay(imgPath, writePath, current_user.id).task_id

            return task_id
    return render_template('edge.jinja2', form=form)

@effect.route('/hdr', methods=['GET', 'POST'])
@login_required
def HDR():
    form = HDRForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            img1 = form.img1.data
            img2 = form.img2.data
            img3 = form.img3.data

            img1Name = uuid4().hex
            img2Name = uuid4().hex
            img3Name = uuid4().hex
            writeName = uuid4().hex

            imgPaths = [os.path.join(app.config['UPLOAD_FOLDER'], img1Name + '.jpg'),
                        os.path.join(app.config['UPLOAD_FOLDER'], img2Name + '.jpg'),
                        os.path.join(app.config['UPLOAD_FOLDER'], img3Name + '.jpg')]

            exposures = [float(form.expo1.data), float(form.expo2.data), float(form.expo3.data)]

            writePath = os.path.join(app.config['UPLOAD_FOLDER'], writeName + '.jpg')

            img1.save(imgPaths[0])
            img2.save(imgPaths[1])
            img3.save(imgPaths[2])

            task_id = hdr.delay(imgPaths, exposures, writePath, current_user.id).task_id
            return task_id

    return render_template('hdr.jinja2', form=form)
