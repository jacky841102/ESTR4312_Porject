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

@effect.route('/edge', methods=['GET', 'POST'])
@login_required
def edge():
    task_id = laplacianOfGaussian.delay('/tmp/images/blended.png', '/tmp/images/edge.png').task_id
    return task_id
