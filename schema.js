db.createCollection("production", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            "required": [
                "name",
                "email",
                "subject",
                "otherSubjects",
                "isComplexAnalysis",
                "wasEmailSend"
            ],
            "properties": {
                "_id": {
                    "bsonType": "objectId"
                },
                "name": {
                    "bsonType": "string",
                    "description": "Nombre completo del profesor"
                },
                "email": {
                    "bsonType": "string",
                    "description": "Correo electrónico del profesor",
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                },
                "subject": {
                    "bsonType": "string",
                    "description": "Materia principal que imparte"
                },
                "otherSubjects": {
                    "bsonType": "array",
                    "description": "Otras materias que imparte el profesor",
                    "items": {
                        "bsonType": "string"
                    }
                },
                "infoAboutPersonalWork": {
                    "bsonType": "string",
                    "description": "Información adicional sobre el trabajo personal del profesor"
                },
                "isComplexAnalysis": {
                    "bsonType": "bool",
                    "description": "¿Imparte análisis complejo?"
                },
                "wasEmailSend": {
                    "bsonType": "bool",
                    "description": "¿Se le ha enviado un correo electrónico?"
                }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "warn"
})