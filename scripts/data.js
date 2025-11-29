// Sample data for the "teachers" collection in MongoDB.
// This script can be executed using the mongo shell.

// Example: mongo your_database_name scripts/data.js

db.teachers.insertOne({
    "name": "M en CC Hararec Medina González",
    "email": "hararec.137@ciencias.unam.mx",
    "subject": "Álgebra Superior I",
    "otherSubjects": [
        "Lógica Matemática I",
        "Álgebra Superior II",
        "Conjuntos y Lógica",
        "Teoría de los Conjuntos I",
        "Teoría de los Conjuntos II",
        "Álgebra Lineal I"
    ],
    "infoAboutPersonalWork": "",
    "isComplexAnalysis": false,
    "wasEmailSend": false,
    "sourceUrl": "https://web.fciencias.unam.mx/directorio/72326",
    "scrapedAt": 1.764451269816237E+09
})

print("Sample teacher data inserted successfully.");
