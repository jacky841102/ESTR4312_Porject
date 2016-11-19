from flask import render_template, request, redirect
from flask_login import login_required, current_user
from app import db
from app.models import User, Following
from . import users
from sqlalchemy import exists

@users.route('/', methods=['GET', 'POST'])
@login_required
def func():
    user = User.query.get(current_user.id)
    if request.method == 'POST':
        followed_id = request.form['followed_id']
        if db.session.query(exists().where(User.id == int(followed_id))) and \
            len(Following.query.filter(followed_id == Following.followed_id and \
                                        Following.follower_id == user.id).all()) == 0:

            following = Following(followed_id=int(followed_id),
                                    follower_id=current_user.id)
            user.followings.append(following)
            db.session.commit()
            return 'follow'
        else:
            unfollowed_id = followed_id
            following = Following.query.filter(
                        unfollowed_id == Following.followed_id and \
                        Following.follower_id == user.id).delete()
            db.session.commit()
            return 'unfollow'

    all_users = User.query.filter(User.id != user.id).all()
    followed = set([f.followed_id for f in user.followings])
    return render_template('follow.jinja2', all_users=all_users, followed=followed)
