import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db')
# Render uses 'postgres://' but SQLAlchemy needs 'postgresql://'
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    technologies = db.Column(db.String(300))
    github_url = db.Column(db.String(500))
    live_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    featured = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Project {self.title}>'

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    featured = Project.query.filter_by(featured=True).first()
    return render_template('index.html', projects=projects, featured=featured)

@app.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)

@app.route('/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project = Project(
            title=request.form['title'],
            description=request.form['description'],
            image_url=request.form.get('image_url', ''),
            video_url=request.form.get('video_url', ''),
            technologies=request.form.get('technologies', ''),
            github_url=request.form.get('github_url', ''),
            live_url=request.form.get('live_url', ''),
            featured=bool(request.form.get('featured'))
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_project.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.title = request.form['title']
        project.description = request.form['description']
        project.image_url = request.form.get('image_url', '')
        project.video_url = request.form.get('video_url', '')
        project.technologies = request.form.get('technologies', '')
        project.github_url = request.form.get('github_url', '')
        project.live_url = request.form.get('live_url', '')
        project.featured = bool(request.form.get('featured'))
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_project.html', project=project, edit=True)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
