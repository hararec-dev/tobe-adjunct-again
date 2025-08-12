// Sample data for the "teachers" collection in MongoDB.
// This script can be executed using the mongo shell.

// Example: mongo your_database_name scripts/data.js

db.teachers.insertOne({
    name: "Hararec Medina",
    email: "hararec.medina@example.com",
    subject: "Cálculo Diferencial",
    otherSubjects: [
        "Cálculo Integral",
        "Ecuaciones Diferenciales",
        "Variable Compleja"
    ],
    infoAboutPersonalWork: "inteligencia artificial",
    isComplexAnalysis: true,
    wasEmailSend: false
});

print("Sample teacher data inserted successfully.");
