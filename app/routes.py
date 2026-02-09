from datetime import datetime
from flask import Blueprint, render_template, request, send_from_directory, current_app
from flask_login import login_required
from .models import Post, Program, Application, LiveSession, ContentItem, Quote
from . import db

main = Blueprint("main", __name__)

@main.route("/")
def index():
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
    programs = Program.query.all()
    quotes = Quote.query.order_by(Quote.created_at.desc()).limit(5).all()
    return render_template("index.html", posts=recent_posts, programs=programs, quotes=quotes)

@main.route("/blog")
def blog():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("blog.html", posts=posts)

@main.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)

@main.route("/programs")
def programs():
    programs = Program.query.all()
    return render_template("programs.html", programs=programs)

@main.route("/apply/<int:program_id>", methods=["GET", "POST"])
def apply(program_id):
    program = Program.query.get_or_404(program_id)
    if request.method == "POST":
        application = Application(
            name=request.form["name"],
            email=request.form["email"],
            goals=request.form["goals"],
            program_id=program_id
        )
        db.session.add(application)
        db.session.commit()
        return render_template("apply.html", program=program, submitted=True)
    return render_template("apply.html", program=program, submitted=False)

@main.route("/dashboard")
@login_required
def dashboard():
    content_items = ContentItem.query.order_by(ContentItem.created_at.desc()).limit(6).all()
    live_sessions = LiveSession.query.order_by(LiveSession.scheduled_at.desc()).limit(3).all()
    posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
    return render_template(
        "dashboard.html",
        content_items=content_items,
        live_sessions=live_sessions,
        posts=posts
    )

@main.route("/content")
@login_required
def content():
    content_items = ContentItem.query.order_by(ContentItem.created_at.desc()).all()
    return render_template("content.html", content_items=content_items)

@main.route("/live")
@login_required
def live():
    sessions = LiveSession.query.order_by(LiveSession.scheduled_at.desc()).all()
    return render_template("live.html", sessions=sessions, now=datetime.now())

@main.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
