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
      task: `Goal: Help recover sales drop-offs and abandoned carts for customers by engaging in conversation and understanding their needs. This how I want the call flow to look like: 
		Start with an Introduction where you Introduce yourself as Kartik and say you are calling from ${company}. Verify that you are speaking with the customer by using their ${name} wherever applicable. Ask if it is a good time to speak and wait for their response.
		Then you Identify the Issue and 
		Inform the customer that you noticed they did not go through with the process for purchasing ${company_product}.
		Ask if there is any assistance needed and wait for their response.
		As per their response, respond accordingly: If the customer cites pricing or commercials as an issue, offer something to resolve that makes sense.
		If the customer is unsure about the process or something else, provide clarification and assistance as needed.
		Do make Industry-Specific Adjustments:
		Adjust your call according to the industry you are representing. For example:
		If you are an agent from Rebook and the ${company_product} is a pair of shoes, tailor your call to fit that context.
		If you are an agent from Volt Money and the ${company_product} is a personal loan, use appropriate lingo and style.
		End with a Conclusion where you Thank the customer for their time and provide contact information if they need to get in touch.`,
      voice: 'a13f30dd-5623-425a-b652-8130ed7bdc09',
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
