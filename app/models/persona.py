from app.config.mysqlconnection import connectToMySQL
from app.init import app
from flask import flash, request, session
import pymysql

class Persona:
    def __init__( self , data ):
        self.id = data['id']
        self.rut = data['rut']
        self.dv = data['dv']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save_persona(cls, rut, dv):
        query = "SELECT * FROM persona WHERE rut = %(rut)s AND dv = %(dv)s"
        data = {
            "rut": rut,
            "dv": dv,
        }
        existing_persona = connectToMySQL('wspjud_py').query_db(query, data)

        if existing_persona:
            print("Persona already exists. Skipping save.")
        else:
            query = "INSERT INTO persona (rut, dv, created_at, updated_at) VALUES (%(rut)s, %(dv)s, NOW(), NOW())"
            connectToMySQL('wspjud_py').query_db(query, data)
            print("Persona saved successfully.")

    @classmethod
    def get_persona_id(cls, rut, dv):
        query = "SELECT id FROM persona WHERE rut = %(rut)s AND dv = %(dv)s LIMIT 1;"
        data = {
            'rut': rut,
            'dv': dv
        }
        result = connectToMySQL('wspjud_py').query_db(query, data)
        if result:
            return result[0]['id']
        else:
            return None