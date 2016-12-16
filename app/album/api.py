from flask import render_template, Blueprint, request, send_from_directory, url_for, redirect, jsonify
from flask_login import login_required, current_user
from app.models import User, Photo, Tag
from app import db, app
from . import album
from werkzeug.utils import secure_filename
from .form import UploadForm, SearchForm, DeleteForm
from app.worker import autoTag, createThumbnail
from uuid import uuid4
import os, redis

@album.route('/')
@login_required
def myalbum():
    r = redis.StrictRedis(host=app.config['CACHE'], port=6379, db=1)
    cache = r.get(current_user.id)
    if cache:
        return cache
    user = User.query.get(current_user.id)
    r.set(current_user.id, render_template('list.jinja2', photos=sorted(user.album, key=lambda x: x.submit_at, reverse=True),  personal=True))
    returnr.get(current_user.id)

@album.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user = User.query.get(current_user.id)
    form = UploadForm()
    attrs = list(set(tag.attr for tag in Tag.query.all()))
    if request.method == 'POST':
        if form.validate_on_submit():
            file = form.photo.data
            if file:
                filename = uuid4().hex + '.jpg'
                imgPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(imgPath)

                with app.app_context():
                    url = url_for('album.uploaded_file', filename=filename, _external=True)
                    photo = Photo(url=url, tn_url=url, filename=filename)

                    for tag in form.tags.data.split('|'):
                        if tag:
                            photo.tags.append(Tag(attr=tag))

                    user.album.append(photo)
                    db.session.commit()

                    createThumbnail.delay(filename, photo.id)
                    autoTag.delay(imgPath, photo.id)

                    return redirect(url)
    return render_template('upload.jinja2', form=form, attrs=attrs)

@album.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@album.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    photo_id = request.form['photo_id']
    if request.method == 'POST':
        photo = Photo.query.get(photo_id)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'tn-' + photo.filename))
        db.session.delete(photo)
        db.session.commit()
        return "deleted"

@album.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if request.method == 'POST':
        #from click on tag
        if 'tag' in request.form:
            tag = request.form['tag']
        #from search page
        else:
            tag = form.tags.data
        attr = tag.strip()
        photos = []
        if attr:
            for tag in Tag.query.filter_by(attr=attr).all():
                photos.append(tag.photo)
            u = render_template('list.jinja2', photos=sorted(photos, key=lambda x: x.submit_at, reverse=True))
            return u
    attrs = list(set(tag.attr for tag in Tag.query.all()))
    return render_template('search.jinja2', form=form, attrs=attrs)
