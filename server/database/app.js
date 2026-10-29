/* jshint esversion: 8 */
const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');
const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

const reviews_file = fs.existsSync("reviews.json") ? "reviews.json" : "data/reviews.json";
const dealerships_file = fs.existsSync("dealerships.json") ? "dealerships.json" : "data/dealerships.json";

const reviews_data = JSON.parse(fs.readFileSync(reviews_file, 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync(dealerships_file, 'utf8'));

let memory_reviews = [...reviews_data.reviews];
let memory_dealers = [...dealerships_data.dealerships];
let mongoConnected = false;

const mongo_url = process.env.MONGO_URL || "mongodb://127.0.0.1:27017/";

const Reviews = require('./review');
const Dealerships = require('./dealership');

mongoose.connect(mongo_url, { 'dbName': 'dealershipsDB', serverSelectionTimeoutMS: 2000 })
  .then(() => {
    mongoConnected = true;
    console.log("Connected to MongoDB successfully.");
    Reviews.deleteMany({}).then(() => Reviews.insertMany(reviews_data.reviews));
    Dealerships.deleteMany({}).then(() => Dealerships.insertMany(dealerships_data.dealerships));
  })
  .catch((err) => {
    console.log("MongoDB connection failed or not running (" + err.message + "). Falling back to local in-memory JSON data.");
    mongoConnected = false;
  });

// Express route to home
app.get('/', async (req, res) => {
    res.send("Welcome to the Mongoose API");
});

// Express route to fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    if (mongoConnected) {
      const documents = await Reviews.find();
      res.json(documents);
    } else {
      res.json(memory_reviews);
    }
  } catch (error) {
    res.json(memory_reviews);
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const dealerId = parseInt(req.params.id, 10);
    if (mongoConnected) {
      const documents = await Reviews.find({ dealership: req.params.id });
      res.json(documents);
    } else {
      const filtered = memory_reviews.filter(r => r.dealership == req.params.id || r.dealership == dealerId);
      res.json(filtered);
    }
  } catch (error) {
    const dealerId = parseInt(req.params.id, 10);
    const filtered = memory_reviews.filter(r => r.dealership == req.params.id || r.dealership == dealerId);
    res.json(filtered);
  }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    if (mongoConnected) {
      const dealerships = await Dealerships.find();
      res.status(200).json(dealerships);
    } else {
      res.status(200).json(memory_dealers);
    }
  } catch (error) {
    res.status(200).json(memory_dealers);
  }
});

// Express route to fetch dealerships by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
    const state = req.params.state;
    try {
      if (mongoConnected) {
        const dealerships = await Dealerships.find({ state });
        if (dealerships.length === 0) {
            res.status(404).json({ error: `No dealerships found in state: ${state}` });
        } else {
            res.json(dealerships);
        }
      } else {
        const filtered = memory_dealers.filter(d => d.state.toLowerCase() === state.toLowerCase());
        if (filtered.length === 0) {
          res.status(404).json({ error: `No dealerships found in state: ${state}` });
        } else {
          res.json(filtered);
        }
      }
    } catch (error) {
        res.status(500).json({ error: 'Error fetching dealerships by state' });
    }
});

// Express route to fetch dealers by ID
app.get('/fetchDealer/:id', async (req, res) => {
    const id = parseInt(req.params.id, 10);
    try {
      if (mongoConnected) {
        const dealership = await Dealerships.findOne({ id });
        if (!dealership) {
            res.status(404).json({ error: `No dealership found with ID: ${id}` });
        } else {
            res.json(dealership);
        }
      } else {
        const found = memory_dealers.find(d => d.id === id);
        if (!found) {
          res.status(404).json({ error: `No dealership found with ID: ${id}` });
        } else {
          res.json(found);
        }
      }
    } catch (error) {
        res.status(500).json({ error: 'Error fetching dealership by ID' });
    }
});

// Express route to insert review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  try {
    const data = typeof req.body === 'string' ? JSON.parse(req.body) : JSON.parse(req.body.toString());
    let new_id = (memory_reviews.length ? Math.max(...memory_reviews.map(r => r.id || 0)) : 0) + 1;

    const reviewObj = {
      "id": new_id,
      "name": data.name,
      "dealership": data.dealership,
      "review": data.review,
      "purchase": data.purchase,
      "purchase_date": data.purchase_date,
      "car_make": data.car_make,
      "car_model": data.car_model,
      "car_year": data.car_year,
    };

    memory_reviews.unshift(reviewObj);

    if (mongoConnected) {
      const review = new Reviews(reviewObj);
      const savedReview = await review.save();
      return res.json(savedReview);
    }
    return res.json(reviewObj);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
