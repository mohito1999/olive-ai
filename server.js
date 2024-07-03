const express = require('express');
const bodyParser = require('body-parser');
const { google } = require('googleapis');
const axios = require('axios');

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));

// Google Sheets setup
const sheets = google.sheets('v4');
const SPREADSHEET_ID = '16WU-3s-coYQ6ff4eD9_LJaW5ovyi0zxTbKRNJQt1bGU';
const SHEET_NAME = 'Sheet1';

// Parse the credentials JSON string from environment variable
const credentials = JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS);
const auth = new google.auth.GoogleAuth({
  credentials: credentials,
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});

// Webhook endpoint
app.post('/api/webhook', async (req, res) => {
  try {
    const name = req.body['Name'];
    const phone = req.body['Phone Number'];
    const email = req.body['Email'];
    const company = req.body['Company/Organization Name'];
    const company_product = req.body['What does your company sell?'];

    // Append data to Google Sheets
    const authClient = await auth.getClient();
    const request = {
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_NAME}!A:E`,
      valueInputOption: 'RAW',
      insertDataOption: 'INSERT_ROWS',
      resource: {
        values: [[name, email, phone, company, company_product]],
      },
      auth: authClient,
    };
    await sheets.spreadsheets.values.append(request);

    // Prepare JSON for Bland
    const blandData = {
      phone_number: `+91${phone}`,
      task: `You're Lucy, a relationship manager at ${company}. Your job is to call the customer who has not completed their application or finished making a purchase and try to convince them to go through with it. You have the ability to offer incentives like cashback for loans or coupon codes for products if you think they might help. You need to gauge which industry you are calling on behalf of based on the name of the company and the product they sell. For example, Volt Money, which sells personal loans, is clearly a financial services company, so you should adjust your script accordingly. Similarly, Rebook, which sells shoes, is a footwear company, so you should also adjust your approach accordingly. Here's an example scenario: Start the call by introducing yourself: "Hi ${name}, this is Lucy from ${company}. Is this a good time to speak?" Confirm the customer's name and mention the abandoned application or purchase: "I noticed that you recently left your ${company_product} application/purchase incomplete on our website." Ask if they have any questions or need assistance: "I wanted to reach out and see if you had any questions or needed any assistance with completing your ${company_product}." Offer an incentive based on the industry: "If it helps, I can offer you an incentive, such as cashback for loans or a discount code for products." If the customer needs more time or has to confirm details, offer to follow up: "Would it be helpful if I follow up with you tomorrow? How about 10 AM or 3 PM?" Schedule a follow-up call and ask if there's anything specific they need help with: "Great, I'll call you at 10 AM tomorrow. Is there anything specific you need help with in the meantime?" End the call politely: "Perfect. I look forward to speaking with you tomorrow. Have a great day!" Remember, the core goal is to convince the customer to go through with their purchase or application, whether it be a loan, buying shoes, or booking a class.`,
      voice: 'maya',
      wait_for_greeting: false,
      block_interruptions: false,
      interruption_threshold: 50,
      model: 'enhanced',
      keywords: ['discount', 'offer', 'purchase'],
      language: 'en',
      record: true,
      answered_by_enabled: true,
    };

    // Send data to Bland's API
    const blandResponse = await axios.post('https://api.bland.ai/v1/calls', blandData, {
      headers: {
        'Authorization': `${process.env.BLAND_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });
    res.status(200).send(blandResponse.data);
  } catch (error) {
    // Log the full error object and response data for debugging
    console.error('Error response data:', error.response ? error.response.data : 'No response data');
    console.error('Error status:', error.response ? error.response.status : 'No status');
    console.error("Request body: ", req.body)
    console.error("Request headers: ", JSON.stringify(req.headers))

    // Send a 500 Internal Server Error response
    res.status(500).send('Internal Server Error: ' + error.message);
  }
});

// For Vercel, we need to export the Express app as a module
module.exports = app;
