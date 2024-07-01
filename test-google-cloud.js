// test-google-cloud.js
const { Storage } = require('@google-cloud/storage');

async function testGoogleCloud() {
  try {
    // Instantiate a client using the environment variable
    const storage = new Storage();

    // Try to list buckets to verify authentication
    const [buckets] = await storage.getBuckets();
    console.log('Buckets:');
    buckets.forEach(bucket => console.log(bucket.name));
  } catch (error) {
    console.error('Error:', error.message);
  }
}

testGoogleCloud();
