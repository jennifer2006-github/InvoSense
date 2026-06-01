# InvoSense – Intelligent Invoice Processing & RAG Chatbot

A full-stack AI-powered application that automates invoice processing using OCR, intelligent document classification, invoice validation, and a Retrieval-Augmented Generation (RAG) chatbot.

## Overview

InvoSense helps organizations digitize and manage invoices efficiently. The system extracts important invoice information from uploaded documents, validates calculations, stores records in a database, and provides an AI-powered chatbot for answering questions from uploaded policy documents.

## Key Features

### OCR Data Extraction

Extracts invoice details from PDF and image files using Tesseract OCR.

### Document Classification

Automatically categorizes documents as:

* Valid Invoice
* Ambiguous
* Not an Invoice

### Invoice Validation

Checks invoice calculations and verifies total amounts for accuracy.

### Database Management

Stores extracted invoice data, classifications, and processing history using SQLite.

### Interactive Dashboard

Provides visual insights into:

* Spending trends
* Invoice statistics
* Upload history
* Processing performance

### RAG-Based Chatbot

Upload policy documents and ask questions in natural language. The chatbot retrieves relevant information from stored documents and generates accurate responses using Google Gemini.

## Technology Stack

### Frontend

* React.js
* Recharts
* Axios

### Backend

* FastAPI
* Python
* SQLite

### AI & Machine Learning

* Tesseract OCR
* Sentence Transformers
* ChromaDB
* Google Gemini Flash

## API Endpoints

| Endpoint       | Method | Description                                 |
| -------------- | ------ | ------------------------------------------- |
| /api/upload    | POST   | Upload and process invoice documents        |
| /api/invoices  | GET    | Retrieve processed invoice records          |
| /api/chat      | POST   | Interact with the AI chatbot                |
| /api/analytics | GET    | Retrieve dashboard analytics and statistics |

## Benefits

* Reduces manual invoice processing effort
* Improves data accuracy through automated validation
* Provides intelligent document classification
* Enables quick access to policy information through AI-powered search
* Centralizes invoice management and analytics
