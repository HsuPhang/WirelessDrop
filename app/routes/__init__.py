from flask import Blueprint

# 创建蓝图对象
file_bp = Blueprint('file', __name__)
page_bp = Blueprint('page', __name__)
ws_bp = Blueprint('ws', __name__)

def register_blueprints(app):

    from .import file_routes,page_routes, ws_routes
    app.register_blueprint(file_routes.file_bp)
    app.register_blueprint(page_routes.page_bp)
    app.register_blueprint(ws_routes.ws_bp)
