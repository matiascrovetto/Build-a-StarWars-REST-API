"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite_character, Favorite_planet


#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/') #GET
def sitemap():
    return generate_sitemap(app)

@app.route('/characters', methods=['GET'])
def getCharacters(): # Obtener personajes
    characters = Character.query.all()
    characters = list(map(lambda character: character.serialize(), characters))
    return jsonify(characters), 200 

@app.route('/characters', methods=['POST']) #crear personajes
def create_character():
    datos = request.get_json()

    character = Character()
    character.uid = datos ['uid']
    character.name = datos ['name']
    character.picture_url = datos['picture_url']
    character.description = datos['description']
    character.save()
    # db.session.add(character)
    # db.session.commit()

    return jsonify(character.serialize()), 201

@app.route('/characters/<int:uid>', methods=['GET'])
def getCharacter(uid): # Obtener personaje por id

    character = Character.query.get(uid) #Buscar el personaje en la base de datos

    if character is not None:
        return jsonify(character.serialize()), 200 
    else:
        return jsonify({"error":"Character not found"})

@app.route('/planets', methods=['GET'])
def get_all_planets(): # Obtener planetas
    planets = Planet.query.all()
    planets = list(map(lambda planet: planet.serialize(), planets))
    return jsonify(planets), 200 

@app.route('/planets', methods=['POST']) #crear planetas
def create_planet():
    datos = request.get_json()

    planet = Planet()
    planet.uid = datos ['uid']
    planet.name = datos ['name']
    planet.picture_url = datos['picture_url']
    planet.description = datos['description']
    planet.save()

    # db.session.add(planet)
    # db.session.commit()

    return jsonify(planet.serialize()), 201

@app.route('/planets/<int:uid>', methods=['GET'])
def getPlanet(uid): #Obtener Planeta por id

    planet = Planet.query.get(uid) #Buscar el planeta en la base de datos

    if planet is not None:
        return jsonify(planet.serialize()), 200 
    else:
        return jsonify({"error":"Planet not found"})

@app.route('/users', methods=['GET']) #Obtener usuarios
def get_all_users():
    users = User.query.all()
    users = list(map(lambda user: user.serialize(), users))
    return jsonify(users), 200 

@app.route('/users', methods=['POST']) #Crear usuarios
def create_user():
    datos = request.get_json()

    user = User()
    user.email = datos ['email']
    user.password = datos ['password']
    user.is_active = datos['is_active']
    characters = False
    planets = False
    user.save()
    # db.session.add(user)
    # db.session.commit()

    return jsonify(user.serialize()), 201

@app.route('/users', methods=['DELETE'])
def delete_all_users():
    users = User.query.all()

    if users:
        for user in users:
            db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "All users have been deleted."}), 200
    else:
        return jsonify({"error": "No users found."}), 404


@app.route('/user/favorites', methods=['GET'])
def getFavorites(): #Acceder a favoritos

    favorites_characters = Favorite_character.query.all()
    favorites_characters = list(map(lambda favorite_character: favorite_character.serialize(), favorites_characters))
    favorites_planets = Favorite_planet.query.all()
    favorites_planets = list(map(lambda favorite_planet: favorite_planet.serialize(), favorites_planets))
    return jsonify(favorites_characters, favorites_planets), 200

@app.route('/user/favorites/planet/<int:planet_id>', methods=['POST'])
def addPlanet(planet_id): #Agregar planeta
    datos = request.get_json()
    
    favorite_planet = Favorite_planet()
    favorite_planet.planet_id = planet_id
    favorite_planet.user_id = datos ['user_id']

    favorite_planet.save()
    # db.session.add(favorite_planet)
    # db.session.commit()

    return jsonify(favorite_planet.serialize()), 201

@app.route('/user/favorites/character/<int:character_id>', methods=['POST'])
def addCharacter(character_id): #Agregar personaje
    datos = request.get_json()
    
    favorite_character = Favorite_character()
    favorite_character.character_id = character_id
    favorite_character.user_id = datos ['user_id']
    favorite_character.save()
    # db.session.add(favorite_character)
    # db.session.commit()

    return jsonify(favorite_character.serialize()), 201


@app.route('/user/favorites/planet/<int:planet_id>', methods=['DELETE'])
def deletePlanet(planet_id): #Borrar planeta
    
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"error":"Planet not found"}), 404
    
    planet.delete()

    return jsonify({"message":f"Planet wit ID {planet_id} deleted"}), 200

@app.route('/user/favorites/character/<int:character_id>', methods=['DELETE'])
def deleteCharacter(character_id): #Borrar personaje
    
    character = Character.query.get(character_id)

    if character is None:
        return jsonify({"error":"Character not found"}), 404
    
    character.delete()

    return jsonify({"message":f"Character wit ID {character_id} deleted"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
