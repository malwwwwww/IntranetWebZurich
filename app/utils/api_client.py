import requests
import logging
from datetime import datetime
from dateutil import parser

class PaperlessAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)

    def get_token(self, username, password):
        try:
            response = requests.post(
                f"{self.base_url}/token/",
                data={'username': username, 'password': password}
            )
            response.raise_for_status()
            token = response.json().get('token')
            self.logger.debug(f"Token obtenido para usuario {username}")
            return token
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener token: {e}")
            return None

    def get_user_info(self, token, username):
        try:
            response = requests.get(
                f"{self.base_url}/users/",
                headers={'Authorization': f'Token {token}'},
                params={'username': username}
            )
            response.raise_for_status()
            users = response.json().get('results', [])
            if not users:
                self.logger.error(f"No se encontró usuario con username {username}")
                return None
            user_info = users[0]
            groups = self.get_group_names(token, user_info.get('groups', []))
            user_info['groups'] = groups
            self.logger.debug(f"Información del usuario obtenida: {user_info['username']}")
            return user_info
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener información del usuario: {e}")
            return None

    def get_group_names(self, token, group_ids):
        if isinstance(group_ids, int):
            group_ids = [group_ids]
        try:
            response = requests.get(
                f"{self.base_url}/groups/",
                headers={'Authorization': f'Token {token}'}
            )
            response.raise_for_status()
            groups = response.json().get('results', [])
            return [{'id': group['id'], 'name': group['name']} for group in groups if group['id'] in group_ids]
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener nombres de grupos: {e}")
            return []

    def get_tag_name(self, token, tag_id):
        try:
            response = requests.get(
                f"{self.base_url}/tags/{tag_id}/",
                headers={'Authorization': f'Token {token}'}
            )
            response.raise_for_status()
            tag = response.json()
            return tag.get('name', 'N/A')
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener etiqueta {tag_id}: {e}")
            return 'N/A'

    def get_user_name(self, token, user_id):
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}/",
                headers={'Authorization': f'Token {token}'}
            )
            response.raise_for_status()
            user = response.json()
            return user.get('username', 'N/A')
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener usuario {user_id}: {e}")
            return 'N/A'

    def get_departments(self):
        return [
            "Aseguramiento de Calidad",
            "Asuntos Regulatorios",
            "Control de Calidad",
            "Desarrollo e Investigación",
            "Exportaciones",
            "Factor Humano",
            "Farmacovigilancia",
            "Logística",
            "Mantenimiento",
            "Maquilas",
            "Planeación",
            "Producción",
            "Tecnologías de la Información y Sistemas",
            "Validación"
        ]

    def get_documents(self, token, search=None, tag=None, type=None, path=None, department=None):
        try:
            params = {}
            if search:
                params['query'] = search
            if tag:
                params['tags__id'] = tag
            if type:
                params['document_type__id'] = type
            if path:
                params['path'] = path
            if department:
                params['owner__username'] = department
            response = requests.get(
                f"{self.base_url}/documents/",
                headers={'Authorization': f'Token {token}'},
                params=params
            )
            response.raise_for_status()
            documents = response.json().get('results', [])
            return [{
                'id': doc['id'],
                'title': doc['title'],
                'created': parser.parse(doc['created']).strftime('%d/%m/%Y'),
                'created_date': parser.parse(doc['created']),
                'version': doc.get('version', ''),
                'procedure': doc.get('procedure', 'N/A'),
                'owner': self.get_user_name(token, doc.get('owner')) if doc.get('owner') else 'N/A',
                'tags': [self.get_tag_name(token, tag_id) for tag_id in doc.get('tags', [])],
                'path': doc.get('path', ''),
                'pages': doc.get('pages', 1),
                'permissions': doc.get('permissions', 'N/A')
            } for doc in documents]
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener documentos: {e}")
            return []

    def get_tags(self, token):
        try:
            response = requests.get(
                f"{self.base_url}/tags/",
                headers={'Authorization': f'Token {token}'}
            )
            response.raise_for_status()
            tags = response.json().get('results', [])
            return [{'id': tag['id'], 'name': tag['name']} for tag in tags]
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener etiquetas: {e}")
            return []