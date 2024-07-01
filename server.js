const express = require('express');
const bodyParser = require('body-parser');
const { google } = require('googleapis');
const axios = require('axios');

const app = express();
app.use(bodyParser.json());

// Google Sheets setup
const sheets = google.sheets('v4');
const SPREADSHEET_ID = '16WU-3s-coYQ6ff4eD9_LJaW5ovyi0zxTbKRNJQt1bGU'; // Your Google Sheet ID
const SHEET_NAME = 'Sheet1'; // Your Google Sheet Name
const auth = new google.auth.GoogleAuth({
  keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS, // Path to your Service Account Key JSON file
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});

// Webhook endpoint
app.post('/webhook', async (req, res) => {
  try {
    const { name, phone, email, company, company_product } = req.body;

    // Adding a delay
    await new Promise(resolve => setTimeout(resolve, 5000));

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

    // Retrieve the last row
    const getLastRowRequest = {
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_NAME}!A:E`,
      auth: authClient,
    };
    const response = await sheets.spreadsheets.values.get(getLastRowRequest);
    const lastRow = response.data.values[response.data.values.length - 1];

    // Prepare JSON for Bland
    const blandData = {
      phone_number: `+91${lastRow[2]}`,
      task: `You’re Lucy, a relationship manager at ${lastRow[3]}. Your job is to call the customer who has abandoned items in their cart and try to convince them to go through with their order. You have the ability to offer discounts in the form of a coupon code if you think they might help. Here’s an example dialogue: Person: Hello? You: Hi, this is Lucy from ${lastRow[3]}. Could you confirm your name for me? Person: Oh hi, this is ${lastRow[0]}. You: Hi ${lastRow[0]}, great to meet you! I noticed that you recently left ${lastRow[4]} in your cart on our website. I wanted to reach out and see if you had any questions or needed any assistance with your order. Person: Oh, gotcha. Actually, I got busy and couldn’t complete the purchase. You: No worries at all. We just wanted to make sure everything is okay. If it helps, I can offer you a discount. How about a 10% off coupon code: SAVE10? Person: That sounds good, but I need to confirm a few details with my team before I can complete the purchase. You: I understand. Would it be helpful if I follow up with you tomorrow? How about 10 AM or 3 PM? Person: 10 AM works for me. You: Great, I’ve noted that down. I’ll call you at 10 AM tomorrow to assist with your purchase. Is there anything specific you need help with in the meantime? Person: No, that should be all for now. You: Perfect. I look forward to speaking with you tomorrow at 10 AM. Have a great day! Person: Thanks, you too! You: Goodbye!`,
      voice: 'maya',
      first_sentence: `Hello ${lastRow[0]}, this is a representative from ${lastRow[3]}. We noticed you added ${lastRow[4]} to your cart but haven't completed the purchase. We are offering you a special discount to complete your purchase.`,
      wait_for_greeting: true,
      block_interruptions: false,
      interruption_threshold: 50,
      model: 'enhanced',
      keywords: ['discount', 'offer', 'purchase'],
      language: 'en',
      record: true,
      webhook: process.env.BLAND_WEBHOOK_URL, // Update this URL after deploying
      voicemail_message: `Hi ${lastRow[0]}, this is a representative from ${lastRow[3]}. We noticed you added ${lastRow[4]} to your cart but haven't completed the purchase. We are offering you a special discount to complete your purchase. Please call us back at your earliest convenience.`,
      answered_by_enabled: true,
    };

    // Send data to Bland's API
    const blandResponse = await axios.post('https://api.bland.ai/v1/calls', blandData, {
      headers: {
        'Authorization': `Bearer ${process.env.BLAND_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });
    res.status(200).send(blandResponse.data);
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal Server Error');
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
