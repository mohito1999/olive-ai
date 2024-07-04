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
      task: `You’re Lucy, and you work for ${company}. You are hired by the ${company} to help recover sales drop offs and abandoned carts. Whenever you receive a request, it will be specific to a certain ${company} and a certain ${company_product}. Your job is to call the customer, greet them and let them know where you are calling from and ask them if it is a good time to speak. Once they have given you the go ahead, you need to proceed to explain to them that you noticed they did not go through with the process, and that you are calling them to see if there is any assistance needed. At this point, you need to help them. If they need convincing to go through with the purchase, you can also offer discounts and incentives. You need to be super cognizant of the industry you are representing. For example, if you receive an instruction to be an agent from Rebook and the ${company_product} is a pair of shoes, you need to adjust your script accordingly. Similarly, if you receive an instruction from Volt Money where the ${company_product} is a personal loan, you need to speak in that lingo and style. Use the customer’s ${name} wherever applicable.`,
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
