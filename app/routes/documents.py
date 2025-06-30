from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from flask_login import login_required, current_user
from ..utils.api_client import PaperlessAPIClient
from ..config import Config
import requests

documents_bp = Blueprint('documents', __name__)

def group_required(group_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
            token = session.get('token')
            username = session.get('username')
            user_info = api_client.get_user_info(token, username)
            if not user_info:
                flash('Error al verificar usuario.', 'error')
                return redirect(url_for('auth.login'))
            user_groups = [group['name'] for group in user_info.get('groups', [])]
            current_app.logger.debug(f"Verificando acceso para {group_name}. Grupos del usuario: {user_groups}")
            if group_name not in user_groups:
                flash('Acceso denegado.', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@documents_bp.route('/dashboard')
@login_required
def dashboard():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    username = session.get('username')
    user_info = api_client.get_user_info(token, username)
    current_app.logger.debug(f"user_info: {user_info}")
    if not user_info:
        flash('Error al verificar usuario.', 'error')
        return redirect(url_for('auth.login'))
    try:
        user_groups = [group['name'] for group in user_info.get('groups', [])]
        current_app.logger.debug(f"Grupos del usuario: {user_groups}")
    except (TypeError, KeyError) as e:
        current_app.logger.error(f"Error al procesar grupos: {e}")
        flash('Error al determinar los permisos del usuario.', 'error')
        return redirect(url_for('auth.login'))
    if 'Administradores' in user_groups:
        return redirect(url_for('documents.dashboard_admin'))
    elif 'Documentadores' in user_groups:
        return redirect(url_for('documents.dashboard_documentadores'))
    elif 'Departamentos' in user_groups:
        return redirect(url_for('documents.dashboard_departamentos'))
    elif 'Usuarios' in user_groups:
        return redirect(url_for('documents.dashboard_usuarios'))
    else:
        flash('No pertenece a ningún grupo autorizado.', 'error')
        return redirect(url_for('auth.login'))

@documents_bp.route('/dashboard_admin')
@login_required
@group_required('Administradores')
def dashboard_admin():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    if not token:
        flash('Sesión inválida.', 'error')
        return redirect(url_for('auth.login'))
    search = request.args.get('search')
    tag = request.args.get('tag')
    path = request.args.get('path')
    department = request.args.get('department')
    documents = api_client.get_documents(token, search=search, tag=tag, path=path, department=department)
    tags = api_client.get_tags(token)
    departments = api_client.get_departments()
    for doc in documents:
        current_app.logger.debug(f"Fecha cruda de documento {doc['id']}: {doc['created_date']}")
        current_app.logger.debug(f"Etiquetas crudas de documento {doc['id']}: {doc['tags']}")
    return render_template('dashboard_admin.html', 
                         documents=documents, 
                         tags=tags, 
                         departments=departments,
                         user=current_user, 
                         token=token)

@documents_bp.route('/dashboard_documentadores')
@login_required
@group_required('Documentadores')
def dashboard_documentadores():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    if not token:
        flash('Sesión inválida.', 'error')
        return redirect(url_for('auth.login'))
    search = request.args.get('search')
    tag = request.args.get('tag')
    path = request.args.get('path')
    department = request.args.get('department')
    documents = api_client.get_documents(token, search=search, tag=tag, path=path, department=department, owner=current_user.username)
    tags = api_client.get_tags(token)
    departments = api_client.get_departments()
    return render_template('dashboard_documentadores.html', 
                         documents=documents, 
                         tags=tags, 
                         departments=departments,
                         user=current_user, 
                         token=token)

@documents_bp.route('/dashboard_departamentos')
@login_required
@group_required('Departamentos')
def dashboard_departamentos():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    if not token:
        flash('Sesión inválida.', 'error')
        return redirect(url_for('auth.login'))
    search = request.args.get('search')
    tag = request.args.get('tag')
    path = request.args.get('path')
    department = request.args.get('department')
    documents = api_client.get_documents(token, search=search, tag=tag, path=path, department=department)
    tags = api_client.get_tags(token)
    departments = api_client.get_departments()
    return render_template('dashboard_departamentos.html', 
                         documents=documents, 
                         tags=tags, 
                         departments=departments,
                         user=current_user, 
                         token=token)

@documents_bp.route('/dashboard_usuarios')
@login_required
@group_required('Usuarios')
def dashboard_usuarios():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    if not token:
        flash('Sesión inválida.', 'error')
        return redirect(url_for('auth.login'))
    search = request.args.get('search')
    tag = request.args.get('tag')
    path = request.args.get('path')
    department = request.args.get('department')
    documents = api_client.get_documents(token, search=search, tag=tag, path=path, department=department, owner=current_user.username)
    tags = api_client.get_tags(token)
    departments = api_client.get_departments()
    return render_template('dashboard_usuarios.html', 
                         documents=documents, 
                         tags=tags, 
                         departments=departments,
                         user=current_user, 
                         token=token)

@documents_bp.route('/view_pdf/<int:doc_id>')
@login_required
def view_pdf(doc_id):
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    if not token:
        flash('Sesión inválida.', 'error')
        return redirect(url_for('auth.login'))
    try:
        response = requests.get(
            f"{Config.PAPERLESS_API_URL}/documents/{doc_id}/download/",
            headers={'Authorization': f'Token {token}'}
        )
        response.raise_for_status()
        pdf_url = f"{Config.PAPERLESS_API_URL}/documents/{doc_id}/download/"
        return render_template('view_pdf.html', pdf_url=pdf_url, token=token, doc_id=doc_id)
    except requests.RequestException as e:
        current_app.logger.error(f"Error al obtener PDF {doc_id}: {e}")
        flash('Error al cargar el documento.', 'error')
        return redirect(request.referrer or url_for('documents.dashboard'))

@documents_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
@group_required('Administradores')
def delete_document(doc_id):
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    current_app.logger.debug(f"Intentando eliminar documento {doc_id} con token {token}")
    try:
        response = requests.delete(
            f"{Config.PAPERLESS_API_URL}/documents/{doc_id}/",
            headers={'Authorization': f'Token {token}'}
        )
        response.raise_for_status()
        current_app.logger.debug("Documento eliminado con éxito")
        flash('Documento movido a la papelera.', 'success')
        return redirect(request.referrer or url_for('documents.dashboard_admin'))
    except requests.RequestException as e:
        current_app.logger.error(f"Error al eliminar documento {doc_id}: {e}")
        flash(f'Error al eliminar el documento: {str(e)}', 'error')
        return redirect(request.referrer or url_for('documents.dashboard_admin'))

@documents_bp.route('/edit/<int:doc_id>', methods=['GET', 'POST'])
@login_required
@group_required('Administradores')
def edit_document(doc_id):
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    token = session.get('token')
    if not token:
        flash('Sesión inválida.', 'error')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        title = request.form.get('title')
        procedure = request.form.get('procedure')
        tags = request.form.getlist('tags')
        owner = request.form.get('owner')
        try:
            data = {'title': title, 'procedure': procedure}
            if tags:
                data['tags'] = tags
            if owner:
                data['owner'] = owner
            response = requests.patch(
                f"{Config.PAPERLESS_API_URL}/documents/{doc_id}/",
                headers={'Authorization': f'Token {token}'},
                json=data
            )
            response.raise_for_status()
            current_app.logger.debug(f"Documento {doc_id} editado con éxito")
            flash('Documento actualizado correctamente.', 'success')
            return redirect(url_for('documents.dashboard_admin'))
        except requests.RequestException as e:
            current_app.logger.error(f"Error al editar documento {doc_id}: {e}")
            flash(f'Error al editar el documento: {str(e)}', 'error')
    try:
        response = requests.get(
            f"{Config.PAPERLESS_API_URL}/documents/{doc_id}/",
            headers={'Authorization': f'Token {token}'}
        )
        response.raise_for_status()
        document = response.json()
        tags = api_client.get_tags(token)
        departments = api_client.get_departments()
        return render_template('edit_document.html', 
                             document=document, 
                             tags=tags, 
                             departments=departments,
                             user=current_user, 
                             token=token)
    except requests.RequestException as e:
        current_app.logger.error(f"Error al obtener documento {doc_id}: {e}")
        flash('Error al cargar el documento.', 'error')
        return redirect(url_for('documents.dashboard_admin'))