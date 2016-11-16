from flask import render_template, Blueprint, request, send_from_directory, url_for, redirect, jsonify
from flask_login import login_required, current_user
from app.models import User, Photo, Tag
from app import db, app
from . import album
from werkzeug.utils import secure_filename
from .form import UploadForm
import os

@album.route('/')
@login_required
def list():
    user = User.query.get(current_user.id)
    urls = [p.url for p in user.album]
    return jsonify(urls=urls)

@album.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user = User.query.get(current_user.id)
    form = UploadForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            file = form.photo.data
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                url = url_for('album.uploaded_file', filename=filename)
                photo = Photo(url=url)

                for tag in form.tags.data.split():
                    photo.tags.append(Tag(attr=tag))

                user.album.append(photo)
                db.session.commit()
                return redirect(url)
    return render_template('upload.html', form=form)

@album.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@album.route('/delete')
@login_required
def delete():
    photo_id = request.args.get('photo_id')
    user = User.query.get(current_user.id)
    photo = Photo.query.get(photo_id)
    if photo:
        db.session.delete(photo)
        db.session.commit()
        return "delete succefully"
