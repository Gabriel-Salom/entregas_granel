from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pytz

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Init restful api
api = Api(app)

# App sessions
app.secret_key = 'jamiley'
#google auth
oauth = OAuth(app)
google = oauth.register(
    name = 'google',
    client_id = '189619289345-bpn7fia2e4jorfemul1l0gand9ru682d.apps.googleusercontent.com',
    client_secret = '1UcQQu-wpohZhe7nOlPzqY7n',
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    client_kwargs = {'scope': 'openid profile email'},
)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)

# Classes/Models for the database
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nome = db.Column(db.String(200))
    Endereco = db.Column(db.String(200))
    Email = db.Column(db.String(200), unique=True)
    Telefone = db.Column(db.String(20))
    pedidos = db.relationship('Pedido', backref='client')
    
    def __init__(self, Nome, Endereco, Email, Telefone):
        self.Nome = Nome
        self.Endereco = Endereco
        self.Email = Email
        self.Telefone = Telefone


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Status = db.Column(db.String(200))
    Date = db.Column(db.String(200), default=datetime.utcnow)
    TotalPagar = db.Column(db.Float)
    Entrega = db.Column(db.String(200))
    client_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    contem = db.relationship('Conteudo', backref='pedido')
    
    def __init__(self, Status, Date, TotalPagar, Entrega, client):
        self.Status = Status
        self.Date = Date
        self.TotalPagar = TotalPagar
        self.Entrega = Entrega
        self.client = client

class Conteudo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPedido = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    idProduto = db.Column(db.Integer, db.ForeignKey('produto.id'))
    produto = db.relationship('Produto', backref='contem')
    Quantidade = db.Column(db.Integer)

    def __init__(self, idPedido, idProduto, Quantidade):
        self.idPedido = idPedido
        self.idProduto = idProduto
        self.Quantidade = Quantidade

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UrlImagem = db.Column(db.String(200))
    Nome = db.Column(db.String(200), unique=True)
    ValorUnitario = db.Column(db.Float)
    Unidade = db.Column(db.String(200))
    PacoteMax = db.Column(db.Integer)
    PacoteMin = db.Column(db.Integer)
    
    def __init__(self, UrlImagem, Nome, ValorUnitario, Unidade, PacoteMax, PacoteMin):
        self.UrlImagem = UrlImagem
        self.Nome = Nome
        self.ValorUnitario = ValorUnitario
        self.Unidade = Unidade
        self.PacoteMax = PacoteMax
        self.PacoteMin = PacoteMin


@app.route('/')
def hello():
    return "hello world!"

@app.cli.command('initdb')
def reset_db():
    #drops and creates fresh database
    db.drop_all()
    db.create_all()
    print('Initialized default DB')

produto_fields = {
    "id": fields.String,
    'UrlImagem': fields.String,
    'Nome': fields.String,
    'ValorUnitario': fields.Float,
    'Unidade': fields.String,
    'PacoteMax': fields.Integer,
    'PacoteMin': fields.Integer
}

conteudo_fields = {
    'Quantidade': fields.Integer,
    'produto': fields.Nested(produto_fields)
}

pedido_fields = {
    'id': fields.Integer,
    'client_id': fields.Integer,
    'Status': fields.String,
    'Date': fields.String,
    'TotalPagar': fields.Float,
    'Entrega': fields.String,
    'contem': fields.Nested(conteudo_fields)
}

client_fields = {
    "id": fields.String,
    'Nome': fields.String,
    'Endereco': fields.String,
    'Email': fields.String,
    'Telefone': fields.String
}

client_orders_fields = {
    "id": fields.String,
    'Nome': fields.String,
    'Endereco': fields.String,
    'Email': fields.String,
    'Telefone': fields.String,
    'pedidos': fields.Nested(pedido_fields),
}


class Clientes(Resource):
    @marshal_with(client_fields)
    def get(self):
        result = Cliente.query.all()
        return result

    def post(self):
        Nome = request.json['Nome']
        Endereco = request.json['Endereco']
        Email = request.json['Email']
        Telefone = request.json['Telefone']
        new_client = Cliente(Nome, Endereco, Email, Telefone)
        db.session.add(new_client)
        db.session.commit()
        return 201

class Clientes_ordens(Resource):
    @marshal_with(client_orders_fields)
    def get(self):
        result = Cliente.query.all()
        return result

class Produtos(Resource):
    @marshal_with(produto_fields)
    def get(self):
        result = Produto.query.all()
        return result

    def post(self):
        UrlImagem = request.json['UrlImagem']
        Nome = request.json['Nome']
        ValorUnitario = request.json['ValorUnitario']
        Unidade = request.json['Unidade']
        PacoteMax = request.json['PacoteMax']
        PacoteMin = request.json['PacoteMin']
        new_produto = Produto(UrlImagem, Nome, ValorUnitario, Unidade, PacoteMax, PacoteMin)
        db.session.add(new_produto)
        db.session.commit()
        return 201

class Pedidos(Resource):
    @marshal_with(pedido_fields)
    def get(self):
        pedido = Pedido.query.all()
        return pedido

    def post(self):
        pedido = request.get_json()
        cliente = Cliente.query.filter_by(id=pedido['client_id']).first()
        if(cliente != None):
            pedido_id = request.json['id']
            tz = pytz.timezone('Brazil/East')
            now = datetime.now(tz)
            date_string = now.strftime("%d/%m/%Y %H:%M:%S")
            request.json['Date'] = date_string
            Status = request.json['Status']
            Date = request.json['Date']
            TotalPagar = request.json['TotalPagar']
            Entrega = request.json['Entrega']
            new_pedido = Pedido(Status, Date, TotalPagar, Entrega, client=cliente)
            db.session.add(new_pedido)
            db.session.commit() 
            for conteudo in pedido['contem']:
                quantidade = conteudo['Quantidade']
                idProduto = conteudo['idProduto']
                new_conteudo = Conteudo(pedido_id, idProduto, quantidade)
                db.session.add(new_conteudo)
                db.session.commit() 
        else:
            return 204

        return 201

api.add_resource(Clientes, '/clientes')
api.add_resource(Clientes_ordens, '/clientes_ordens')
api.add_resource(Pedidos, '/pedidos')
api.add_resource(Produtos, '/produtos')


if __name__ == '__main__':
    app.run(debug=True)