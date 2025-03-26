from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from .models import Post, User, Comment
from werkzeug.utils import secure_filename
from . import create_app, db
import os
from datetime import datetime
from base64 import b64encode
import base64
from io import BytesIO


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required

def home():
    app = create_app()

    posts = Post.query.order_by(Post.date_created.desc()).all()
    pr_det = User.query.filter_by(username=current_user.username).first()

    return render_template("home.html", user=current_user, posts=posts, pr_det=pr_det )

@views.route("/profile/<username>", methods=['GET','POST'])
@login_required

def profileDetails(username):
    if request.method == "GET":
        pr_det = User.query.filter_by(username=username).first()
        return render_template("profile.html", user=current_user, pr_det=pr_det)


    elif request.method == "POST":
        pic = request.files['pic']
        if pic:
            print('check passed')
            imgname = secure_filename(pic.filename)
            print("-------" + imgname)
            app = create_app()
            picture = pic.read()
            render_file = render_picture(picture)

            print(os.path.join(app.config['UPLOAD_FOLDER'], imgname))
            pic.seek(0)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], imgname))
            num_rows_updated = User.query.filter_by(username=username).update(dict(profilepicname=imgname))
            db.session.commit()

            flash('Profile Photo Added!', category='success')
            return redirect(url_for('views.home'))

        else:
            print('Pic hi nahi hai bhaiyax')
    return render_template('base.html', user=current_user)

@views.route("/", methods=['GET', 'POST'])
@views.route("/home", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        pic = request.files['pic']
        text = request.form.get('text')
        if pic and not text:

            print('check passed')
            imgname = secure_filename(pic.filename)
            mimetype = pic.mimetype
            app = create_app()
            picture = pic.read()
            render_file = render_picture(picture)

            print(os.path.join(app.config['UPLOAD_FOLDER'], imgname))
            pic.seek(0)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], imgname))
            post = Post(img=picture, mimetype=mimetype, img_name=imgname,rendered_data=render_file,
            author=current_user.id )
            db.session.add(post)
            db.session.commit()

            flash('Photo Added!', category='success')
            return redirect(url_for('views.home'))

            return render_template('base.html', user=current_user)
        elif text and not pic:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()

            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

        elif text and pic:
            text = request.form.get('text')
            pic = request.files['pic']
            imgname = secure_filename(pic.filename)
            mimetype = pic.mimetype
            app = create_app()
            picture = pic.read()
            render_file = render_picture(picture)

            print(os.path.join(app.config['UPLOAD_FOLDER'], imgname))
            pic.seek(0)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], imgname))
            post = Post(text=text, img=picture, mimetype=mimetype, img_name=imgname,rendered_data=render_file, author=current_user.id )
            db.session.add(post)
            db.session.commit()

            flash('Photo Added!', category='success')
            return redirect(url_for('views.home'))

            return render_template('base.html', user=current_user)

    return render_template('base.html', user=current_user)



def render_picture(pic):

    render_pic = base64.b64encode(pic).decode('ascii')
    return render_pic




@views.route('/<int:id>')
def get_img(id):
    img = Post.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()


    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.query(Comment).filter_by(post_id=id).delete()
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))

@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()
    pr_det = User.query.filter_by(username=current_user.username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username, pr_det=pr_det)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/chat/<id>", methods=['GET', 'POST'])
@login_required
def chat(id):
    return(render_template("chat.html"))
