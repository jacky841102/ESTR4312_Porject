from flask import render_template, Blueprint, request, send_from_directory, url_for, redirect, jsonify
from flask_login import login_required, current_user
from app.models import User, Photo
from app import db, app
from . import album
from werkzeug.utils import secure_filename
from .form import UploadForm
import os

@album.route('/')
@login_required
def list(id=0):
    if not id:
        id = current_user.id
    user = User.query.get(id)
    if user and current_user.id == id:
        urls = [p.url for p in user.album]
        return jsonify(urls=urls)
    return 'noop'

@album.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    id = current_user.id
    user = User.query.get(id)
    form = UploadForm()
    if request.method == 'POST':
        if user and form.validate_on_submit():
            file = form.photo.data
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                url = url_for('album.uploaded_file', filename=filename)
                photo = Photo(url=url)
                user.album.append(photo)
                db.session.add(photo)
                db.session.commit()
                return redirect(url)
    return render_template('upload.html', form=form)

@album.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
