# Dealerships Review Portal - Fullstack Software Developer Capstone Project
by Sierra Ripoche

## Overview

This project is the final capstone for the **Fullstack Software Developer** certification course. The goal of this project is to develop a web application for a national car dealership with branches across the United States, enabling users to view dealership information and leave reviews for each branch. This project leverages various technologies including **Django**, **React**, **Node.js**, **MongoDB**, **Docker**, and **IBM Cloud**.

### Project Background

A market survey conducted by the car dealership company revealed a strong interest from customers in a centralized platform where they could view reviews of dealerships nationwide. The goal is to provide transparency and increase customer trust in the dealership network by enabling users to read reviews and submit their own.

### Key Features

- **Anonymous Users**: View dealership details and reviews.
- **Authorized Users**: Log in, submit reviews, and view reviews for each dealership.
- **Admin Users**: Manage dealership information, including adding car makes, models, and other attributes.
- **Sentiment Analysis**: Analyze the sentiment of customer reviews using an IBM Cloud-based sentiment analyzer service.

## Technologies Used

- **Django**: Backend web framework to manage dealership data, user authentication, and reviews.
- **React**: Frontend framework for building dynamic user interfaces.
- **Node.js**: Server to handle dealership and review data with MongoDB.
- **MongoDB**: Database used to store dealership and review data.
- **Docker**: Containerization technology for packaging the application and services.
- **IBM Cloud Code Engine**: Cloud platform to deploy the sentiment analysis service.
- **CI/CD**: Continuous Integration and Continuous Deployment pipeline for efficient code management and delivery.

## Architecture

The solution architecture consists of the following components:

1. **Dealerships Website (Django)**:
   - Microservices for managing dealerships, car models, reviews, and user authentication.
   - Interaction with a MongoDB database through a proxy service.

2. **Dealerships and Reviews Service (Node.js/Express)**:
   - Microservice to handle CRUD operations for dealers and reviews.
   - Hosted in a Docker container for easy deployment.

3. **Sentiment Analyzer (IBM Cloud Code Engine)**:
   - Analyzes the sentiment of review text (positive, negative, or neutral).

4. **Database**:
   - **SQLite** for storing car make and model data in Django.
   - **MongoDB** for storing dealer and review data in the Node.js service.

## User Stories

### Anonymous Users
- View the **Contact Us** and **About Us** pages.
- View a list of dealerships across the United States, with the ability to filter by state.
- View reviews for each dealership.

### Authorized Users
- In addition to anonymous features, authorized users can:
  - Submit reviews for any dealership.
  - Submit a review which will appear at the top of the list of reviews on the dealership detail page.

### Admin Users
- Log into the admin interface to manage dealership data.
- Add new makes, models, and other attributes for dealerships.

## Installation Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/SiRipo92/Fullstack_Dev_Capstone_Project
   cd Fullstack_Dev_Capstone_Project
   ```
2. **Set up virtual environment**
   ```bash
   cd Fullstack_Dev_Capstone_Project/server
   pip install virtualenv
   virtualenv djangoenv
   source djangoenv/bin/activate
   ```
3. **Set up Django Backend**
   - Install Python dependencies :
   ```bash
   python3 -m pip install -U -r requirements.txt 
   ```
   - Run migrations to set up the database and start development server:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   python3 manage.py runserver
   ```
4. **Set up the Backend Mongo Express server**
   - Navigate to the Database directory
   ```bash
   cd server/database
   ```
   - Build the nodeapp:
   ```bash
   docker build . -t nodeapp
   ```
   - Start the server:
   ```bash
   docker-compose up
   ```
5. **Frontend (React):**
   - Navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```
   - Run the React app:
   ```bash
   npm run build
   ```
6. **Code Engine**:
   To run the Cloud Code Engine service to access Sentiment Analyzer Microservice:
   - Navigate to Skills Network Toolbox, and under Cloud, find Code Engine.
   - Start code engine by creating a project.
   - Once the code engine set up is complete, you can see that it is active. Click on Code Engine CLI to begin the pre-configured CLI in the terminal below.
   - You will observe that the pre-configured CLI statrup and the home directory is set to the current directory.
     As a part of the pre-configuration, the project has been set up and Kubeconfig is set up. The details that are shown on the terminal.
   - Navigate to cd server/djangoapp/microservices
   - Docker build the sentiment analyzer ap:
   ```bash
   docker build . -t us.icr.io/${SN_ICR_NAMESPACE}/senti_analyzer
   ```
   - Push the docker image:
   ```bash
   docker push us.icr.io/${SN_ICR_NAMESPACE}/senti_analyzer
   ```
   - Deploy the Senti_analyzer application on code engine
   - Obtain the URL and add to .env file (no / backslashes) (do the same for the backend after running MongoDB server (Port 3030)
   ```bash
   sentiment_analyzer_url=your code engine deployment url
   backend_url = your backend url
   ```

## CI / CD
- Workflow is created to lint files to meet PEP8 guidelines. When code is pushed to the repository, the workflow will automatically begin to lint the Python and JavaScript files.

## Deployment 
1. Kubernetes: Deploy the application and its microservices on Kubernetes for scalability.
2. IBM Cloud: Deploy the Sentiment Analyzer microservice on IBM Cloud Code Engine.

### Contributors: 
- Upkar Lidder - Lead Full-Stack Software Developer
- Lavanya - Full-Stack Developer
- Yan Luo - Backend Developer
- Priya - Frontend Developer
- **Sierra Ripoche - Full-Stack Developer**
