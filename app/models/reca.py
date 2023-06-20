from app.config.mysqlconnection import connectToMySQL
from app.init import app
from flask import flash, request, session
import pymysql

class Reca:
    def __init__( self , data ):
        self.id = data['id']
        self.persona_id = data['persona_id']
        self.rit = data['rit']
        self.n_causa = data['n_causa']
        self.caratulado = data['caratulado']
        self.competencia = data['competencia']
        self.tribunal = data['tribunal']
        self.corte = data['corte']
        self.fecha_ing_causa = data['fecha_ing_causa']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save_Reca(cls, persona_id, data):
        rit = data['RIT']
        query = "SELECT * FROM RECA WHERE rit = %(rit)s"
        existing_RECA = connectToMySQL('wspjud_py').query_db(query, {'rit': rit})

        if existing_RECA:
            print("RECA already exists for rit:", rit)
            return None

        data['persona_id'] = persona_id

        query = """
            INSERT INTO RECA (persona_id, rit, n_causa, caratulado, competencia, tribunal, corte, fecha_ing_causa, created_at, updated_at) 
            VALUES (%(persona_id)s, %(RIT)s, %(Nombre Interviniente en la Causa)s, %(Caratulado)s, %(Competencia)s, %(Tribunal)s, %(Corte)s, %(Fecha Ing. Causa)s, NOW(), NOW())
        """
        return connectToMySQL('wspjud_py').query_db(query, data)