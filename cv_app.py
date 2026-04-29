from flask import Flask, render_template
import os
from services.cv_service import CVService

cv_app = Flask(__name__)
cv_app.config['CV_DATABASE'] = os.path.join(cv_app.root_path, 'storage', 'cv_data.db')
cv_service = CVService(cv_app.config['CV_DATABASE'])

@cv_app.route('/')
def index():
    cv_data = cv_service.get_all_cv_data()
    showcase = cv_service.get_showcase()
    return render_template(
        'cv.html', 
        profile=cv_data['profile'],
        about=cv_data['about'],
        languages=cv_data['languages'],
        metadata=cv_data['metadata'],
        skills=cv_data['skills'],
        keywords=cv_data['keywords'],
        experience=cv_data['experience'],
        education=cv_data['education'],
        volunteer=cv_data['volunteer'],
        references=cv_data['references'],
        showcase=showcase
    )