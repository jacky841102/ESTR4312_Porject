from flask import render_template, request, redirect
from flask_login import login_required, current_user
from app import db
from app.models import User, Following
from . import follow
from sqlalchemy import exists

@follow.route('/', methods=['GET', 'POST'])
@login_required
def func():
    user = User.query.get(current_user.id)
    if request.method == 'POST':
        followed_id = request.form['followed_id']
        if followed_id and followed_id != user.id and db.session.query(exists().where(User.id == int(followed_id))):
            user.followings.append(Following(followed_id=int(followed_id),
                                            follower_id=current_user.id))
            db.session.commit()
    all_users = User.query.all()
    followed = set([f.followed_id for f in user.followings])
    return render_template('follow.jinja2', all_users=all_users, followed=followed)
