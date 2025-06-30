from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

document_groups = db.Table('document_groups',
    db.Column('document_id', db.Integer, db.ForeignKey('documents_document.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('auth_group.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'auth_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    role = db.Column(db.String(50), default='Usuario')
    department = db.relationship('Department')
    groups = db.relationship('Group', secondary='auth_user_groups')

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Group(db.Model):
    __tablename__ = 'auth_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

class Document(db.Model):
    __tablename__ = 'documents_document'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    pages = db.Column(db.Integer)
    archive_serial_number = db.Column(db.String(32))
    document_type_id = db.Column(db.Integer)
    correspondent_id = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    procedure = db.Column(db.String(100))
    path = db.Column(db.String(100))
    permissions = db.Column(db.String(50))
    department = db.relationship('Department')
    owner = db.relationship('User')
    groups = db.relationship('Group', secondary=document_groups)