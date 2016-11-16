from flask import render_template, Blueprint, request, send_from_directory, url_for, redirect, jsonify
from flask_login import login_required, current_user
from app.models import User, Photo, Tag
from app import db, app
from . import album
from werkzeug.utils import secure_filename
from .form import UploadForm, SearchForm, DeleteForm
import os

@album.route('/')
@login_required
def list():
    user = User.query.get(current_user.id)
    urls = [p.url for p in user.album]
    return render_template('list.jinja2', urls=urls)

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

@album.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    form = DeleteForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            photo_id = int(form.photo_id.data)
            photo = Photo.query.get(photo_id)
            db.session.delete(photo)
            db.session.commit()
            return 'delete succesfully'
    return render_template('delete.html', form=form)

@album.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            attr = form.tag.data
            urls = []
            if attr:
                for tag in Tag.query.filter_by(attr=attr).all():
                    urls.append(tag.photo.url)
            return jsonify(urls=urls)
    return render_template('search.html', form=form)
