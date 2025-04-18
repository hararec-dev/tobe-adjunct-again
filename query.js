db.production.aggregate([
    {
        $group: {
            _id: "$name",
            count: { $sum: 1 },
            docs: { $push: "$$ROOT" }
        }
    },
    {
        $match: {
            count: { $gt: 1 },
        }
    },
    {
        $project: {
            _id: 0,
            name: "$_id",
            duplicatedDocuments: "$docs"
        }
    }
]).pretty()