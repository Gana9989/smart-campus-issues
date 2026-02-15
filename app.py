"""Smart Campus Issue Reporting System - Flask Application."""
import os
from datetime import datetime, date
from sqlalchemy import func
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from extensions import db
from models import User, Issue


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login_page"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    # --- Page Routes ---

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("student_dashboard"))
        return redirect(url_for("login_page"))

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/signup")
    def signup_page():
        return render_template("signup.html")

    @app.route("/admin/login")
    def admin_login_page():
        return render_template("admin_login.html")

    @app.route("/student/dashboard")
    @login_required
    def student_dashboard():
        if current_user.role != "student":
            return redirect(url_for("admin_dashboard"))
        return render_template("student_dashboard.html", profile_link=True)

    @app.route("/student/profile")
    @login_required
    def student_profile():
        if current_user.role != "student":
            return redirect(url_for("admin_dashboard"))
        return render_template("student_profile.html", profile_link=True, user=current_user)

    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        if current_user.role != "admin":
            return redirect(url_for("student_dashboard"))

        total_issues = Issue.query.count()
        today = date.today()
        resolved_today = Issue.query.filter(
            Issue.status == "Resolved",
            func.date(Issue.updated_at) == today,
        ).count()
        pending_count = Issue.query.filter_by(status="Pending").count()
        category_results = (
            db.session.query(Issue.category, func.count(Issue.id))
            .group_by(Issue.category)
            .order_by(func.count(Issue.id).desc())
            .all()
        )
        category_labels = [r[0] for r in category_results]
        category_counts = [r[1] for r in category_results]

        return render_template(
            "admin_dashboard.html",
            total_issues=total_issues,
            resolved_today=resolved_today,
            pending_count=pending_count,
            category_labels=category_labels,
            category_counts=category_counts,
        )

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)

    # --- Auth API ---

    @app.route("/api/auth/signup", methods=["POST"])
    def api_signup():
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not name or len(name) < 2:
            return jsonify({"success": False, "message": "Name must be at least 2 characters"}), 400
        if not email or "@" not in email:
            return jsonify({"success": False, "message": "Invalid email"}), 400
        if not password or len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Email already registered"}), 400

        user = User(name=name, email=email, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return jsonify({"success": True, "user": user.to_dict()})

    @app.route("/api/auth/login", methods=["POST"])
    def api_login():
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        user = User.query.filter_by(email=email, role="student").first()
        if not user or not user.check_password(password):
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        login_user(user)
        return jsonify({"success": True, "user": user.to_dict()})

    @app.route("/api/auth/admin/login", methods=["POST"])
    def api_admin_login():
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        user = User.query.filter_by(email=email, role="admin").first()
        if not user or not user.check_password(password):
            return jsonify({"success": False, "message": "Invalid admin credentials"}), 401

        login_user(user)
        return jsonify({"success": True, "user": user.to_dict()})

    @app.route("/api/auth/logout", methods=["POST"])
    @login_required
    def api_logout():
        logout_user()
        return jsonify({"success": True})

    @app.route("/api/auth/me")
    def api_me():
        if not current_user.is_authenticated:
            return jsonify({"authenticated": False}), 401
        return jsonify({"authenticated": True, "user": current_user.to_dict()})

    @app.route("/api/student/profile")
    @login_required
    def api_student_profile():
        if current_user.role != "student":
            return jsonify({"success": False, "message": "Access denied"}), 403
        return jsonify({"success": True, "user": current_user.to_dict()})

    @app.route("/api/student/profile/update", methods=["POST"])
    @login_required
    def api_student_profile_update():
        if current_user.role != "student":
            return jsonify({"success": False, "message": "Only students can update profile"}), 403
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        name = (data.get("full_name") or data.get("name") or "").strip()
        if not name or len(name) < 2:
            return jsonify({"success": False, "message": "Full name must be at least 2 characters"}), 400

        current_user.name = name
        current_user.phone = (data.get("phone") or "").strip() or None
        current_user.department = (data.get("department") or "").strip() or None
        current_user.year = (data.get("year") or "").strip() or None
        current_user.hostel_or_block = (data.get("hostel_or_block") or "").strip() or None
        db.session.commit()

        return jsonify({"success": True, "message": "Profile updated successfully!", "user": current_user.to_dict()})

    # --- Issues API ---

    @app.route("/api/issues", methods=["GET"])
    @login_required
    def api_get_issues():
        category = request.args.get("category", "").strip()
        status_filter = request.args.get("status", "").strip()

        if current_user.role == "admin":
            q = Issue.query
        else:
            q = Issue.query.filter_by(user_id=current_user.id)

        if category:
            q = q.filter(Issue.category == category)
        if status_filter:
            q = q.filter(Issue.status == status_filter)

        issues = q.order_by(Issue.created_at.desc()).all()
        return jsonify({"success": True, "issues": [i.to_dict() for i in issues]})

    @app.route("/api/issues", methods=["POST"])
    @login_required
    def api_create_issue():
        if current_user.role != "student":
            return jsonify({"success": False, "message": "Only students can report issues"}), 403

        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        category = (request.form.get("category") or "").strip()

        if not title or len(title) < 3:
            return jsonify({"success": False, "message": "Title must be at least 3 characters"}), 400
        if not description or len(description) < 10:
            return jsonify({"success": False, "message": "Description must be at least 10 characters"}), 400

        valid_categories = ["Electricity", "Water", "Cleanliness", "Internet", "Classroom", "Other"]
        if category not in valid_categories:
            return jsonify({"success": False, "message": "Invalid category"}), 400

        image_path = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_path = filename

        issue = Issue(
            title=title,
            description=description,
            category=category,
            image_path=image_path,
            status="Pending",
            user_id=current_user.id,
        )
        db.session.add(issue)
        db.session.commit()

        return jsonify({"success": True, "message": "Issue submitted successfully!", "issue": issue.to_dict()})

    @app.route("/api/issues/<int:issue_id>/status", methods=["PATCH"])
    @login_required
    def api_update_status(issue_id):
        if current_user.role != "admin":
            return jsonify({"success": False, "message": "Only admins can update status"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON"}), 400

        status = (data.get("status") or "").strip()
        valid_statuses = ["Pending", "In Progress", "Resolved"]
        if status not in valid_statuses:
            return jsonify({"success": False, "message": "Invalid status"}), 400

        issue = Issue.query.get_or_404(issue_id)
        issue.status = status
        issue.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"success": True, "message": "Issue status updated successfully!", "issue": issue.to_dict()})

    @app.route("/api/issues/stats")
    @login_required
    def api_issues_stats():
        if current_user.role != "admin":
            return jsonify({"success": False, "message": "Admin only"}), 403

        total = Issue.query.count()
        pending = Issue.query.filter_by(status="Pending").count()
        in_progress = Issue.query.filter_by(status="In Progress").count()
        resolved = Issue.query.filter_by(status="Resolved").count()
        today = date.today()
        resolved_today = Issue.query.filter(
            Issue.status == "Resolved",
            func.date(Issue.updated_at) == today,
        ).count()

        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "pending": pending,
                "in_progress": in_progress,
                "resolved": resolved,
                "resolved_today": resolved_today,
            },
        })

    return app


app = create_app()

with app.app_context():
    db.create_all()
    # Migration: add updated_at to issues table if missing (existing DBs)
    try:
        from sqlalchemy import inspect, text
        insp = inspect(db.engine)
        if "issues" in insp.get_table_names():
            cols = [c["name"] for c in insp.get_columns("issues")]
            if "updated_at" not in cols:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE issues ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                    conn.commit()
        # Migration: add student profile columns to users table if missing
        if "users" in insp.get_table_names():
            user_cols = [c["name"] for c in insp.get_columns("users")]
            for col in ("phone", "department", "year", "hostel_or_block"):
                if col not in user_cols:
                    with db.engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} TEXT"))
                        conn.commit()
    except Exception:
        pass
    # Create default admin if none exists
    if not User.query.filter_by(role="admin").first():
        admin = User(name="Admin", email="admin@campus.edu", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
