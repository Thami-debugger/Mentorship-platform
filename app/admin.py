import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from .decorators import admin_required
from .models import Post, Program, Application, User, LiveSession, ContentItem, Quote
from . import db

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/")
@login_required
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        posts=Post.query.count(),
        programs=Program.query.count(),
        applications=Application.query.count(),
        users=User.query.count(),
        live_sessions=LiveSession.query.count(),
        content_items=ContentItem.query.count(),
        quotes=Quote.query.count()
    )

@admin.route("/posts")
@login_required
@admin_required
def posts():
    return render_template("admin/posts.html", posts=Post.query.order_by(Post.created_at.desc()).all())

@admin.route("/posts/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_post():
    if request.method == "POST":
        post = Post(
            title=request.form["title"],
            content=request.form["content"]
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("admin.posts"))
    return render_template("admin/create_post.html")

@admin.route("/posts/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("admin.posts"))
    return render_template("admin/edit_post.html", post=post)

@admin.route("/posts/delete/<int:post_id>")
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("admin.posts"))

@admin.route("/programs")
@login_required
@admin_required
def programs():
    return render_template("admin/programs.html", programs=Program.query.all())

@admin.route("/programs/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_program():
    if request.method == "POST":
        program = Program(
            title=request.form["title"],
            description=request.form["description"],
            duration=request.form["duration"]
        )
        db.session.add(program)
        db.session.commit()
        return redirect(url_for("admin.programs"))
    return render_template("admin/create_program.html")

@admin.route("/programs/edit/<int:program_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_program(program_id):
    program = Program.query.get_or_404(program_id)
    if request.method == "POST":
        program.title = request.form["title"]
        program.description = request.form["description"]
        program.duration = request.form["duration"]
        db.session.commit()
        return redirect(url_for("admin.programs"))
    return render_template("admin/edit_program.html", program=program)

@admin.route("/programs/delete/<int:program_id>")
@login_required
@admin_required
def delete_program(program_id):
    program = Program.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    return redirect(url_for("admin.programs"))

@admin.route("/applications")
@login_required
@admin_required
def applications():
    apps = Application.query.all()
    return render_template("admin/applications.html", applications=apps)

@admin.route("/live")
@login_required
@admin_required
def live():
    sessions = LiveSession.query.order_by(LiveSession.scheduled_at.desc()).all()
    return render_template("admin/live.html", sessions=sessions, now=datetime.now())

@admin.route("/live/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_live():
    if request.method == "POST":
        scheduled_at = request.form.get("scheduled_at")
        scheduled_value = None
        if scheduled_at:
            scheduled_value = datetime.strptime(scheduled_at, "%Y-%m-%dT%H:%M")
        session = LiveSession(
            title=request.form["title"],
            embed_url=request.form["embed_url"],
            scheduled_at=scheduled_value
        )
        db.session.add(session)
        db.session.commit()
        return redirect(url_for("admin.live"))
    return render_template("admin/create_live.html")

@admin.route("/live/edit/<int:session_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_live(session_id):
    session = LiveSession.query.get_or_404(session_id)
    if request.method == "POST":
        scheduled_at = request.form.get("scheduled_at")
        scheduled_value = None
        if scheduled_at:
            scheduled_value = datetime.strptime(scheduled_at, "%Y-%m-%dT%H:%M")
        session.title = request.form["title"]
        session.embed_url = request.form["embed_url"]
        session.scheduled_at = scheduled_value
        db.session.commit()
        return redirect(url_for("admin.live"))
    return render_template("admin/edit_live.html", session=session)

@admin.route("/live/start/<int:session_id>")
@login_required
@admin_required
def start_live(session_id):
    session = LiveSession.query.get_or_404(session_id)
    session.scheduled_at = datetime.now()
    db.session.commit()
    return redirect(url_for("admin.live"))

@admin.route("/live/delete/<int:session_id>")
@login_required
@admin_required
def delete_live(session_id):
    session = LiveSession.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    return redirect(url_for("admin.live"))

@admin.route("/content")
@login_required
@admin_required
def content():
    content_items = ContentItem.query.order_by(ContentItem.created_at.desc()).all()
    return render_template("admin/content.html", content_items=content_items)

@admin.route("/content/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_content():
    if request.method == "POST":
        file = request.files.get("file")
        file_url = request.form.get("file_url")
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(upload_path)
            file_url = url_for("main.uploaded_file", filename=filename)
        item = ContentItem(
            title=request.form["title"],
            description=request.form.get("description"),
            content_type=request.form["content_type"],
            file_url=file_url
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for("admin.content"))
    return render_template("admin/create_content.html")

@admin.route("/content/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_content(item_id):
    item = ContentItem.query.get_or_404(item_id)
    if request.method == "POST":
        file = request.files.get("file")
        file_url = request.form.get("file_url")
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(upload_path)
            file_url = url_for("main.uploaded_file", filename=filename)
        if not file_url:
            file_url = item.file_url
        item.title = request.form["title"]
        item.description = request.form.get("description")
        item.content_type = request.form["content_type"]
        item.file_url = file_url
        db.session.commit()
        return redirect(url_for("admin.content"))
    return render_template("admin/edit_content.html", item=item)

@admin.route("/content/delete/<int:item_id>")
@login_required
@admin_required
def delete_content(item_id):
    item = ContentItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("admin.content"))

@admin.route("/quotes")
@login_required
@admin_required
def quotes():
    quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return render_template("admin/quotes.html", quotes=quotes)

@admin.route("/quotes/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_quote():
    if request.method == "POST":
        quote = Quote(
            text=request.form["text"],
            author=request.form.get("author")
        )
        db.session.add(quote)
        db.session.commit()
        return redirect(url_for("admin.quotes"))
    return render_template("admin/create_quote.html")

@admin.route("/quotes/edit/<int:quote_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if request.method == "POST":
        quote.text = request.form["text"]
        quote.author = request.form.get("author")
        db.session.commit()
        return redirect(url_for("admin.quotes"))
    return render_template("admin/edit_quote.html", quote=quote)

@admin.route("/quotes/delete/<int:quote_id>")
@login_required
@admin_required
def delete_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    db.session.delete(quote)
    db.session.commit()
    return redirect(url_for("admin.quotes"))
