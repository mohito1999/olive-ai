import { NextAuthConfig } from 'next-auth';
import CredentialProvider from 'next-auth/providers/credentials';
import { MongoDBAdapter } from '@auth/mongodb-adapter';
import mongoClientPromise from './lib/db';

const authConfig = {
    // adapter: MongoDBAdapter(mongoClientPromise),
    providers: [
        {
            id: 'my-provider', // signIn("my-provider") and will be part of the callback URL
            name: 'My Provider', // optional, used on the default login page as the button text.
            type: 'oauth', // or "oauth" for OAuth 2 providers
            issuer: 'http://localhost:3001', // to infer the .well-known/openid-configuration URL
            clientId: process.env.AUTH_CLIENT_ID, // from the provider's dashboard
            clientSecret: process.env.AUTH_CLIENT_SECRET // from the provider's dashboard
        }
    ],
    // providers: [
    //     CredentialProvider({
    //         credentials: {
    //             email: {
    //                 type: 'email'
    //             },
    //             password: {
    //                 type: 'password'
    //             }
    //         },
    //         async authorize(credentials, req) {
    //             console.log(credentials);
    //             const user = {
    //                 id: '1',
    //                 name: 'John',
    //                 email: credentials?.email as string
    //             };
    //             if (user) {
    //                 // Any object returned will be saved in `user` property of the JWT
    //                 return user;
    //             } else {
    //                 // If you return null then an error will be displayed advising the user to check their details.
    //                 return null;
    //
    //                 // You can also Reject this callback with an Error thus the user will be sent to the error page with the error message as a query parameter
    //             }
    //         }
    //     })
    // ],
    session: { strategy: 'jwt' },
    pages: {
        signIn: '/' //sigin page
    }
} satisfies NextAuthConfig;

export default authConfig;
