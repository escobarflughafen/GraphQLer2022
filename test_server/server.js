import express from 'express';
import {ApolloServer} from 'apollo-server-express';
import {createServer} from 'http';
import cors from 'cors';
import schema from './data/schema.js';

const PORT = 4001;
const app = express();

app.use('*', cors());

const server = new ApolloServer({
    schema,
    playground: true,
})

server.applyMiddleware({app});

const httpServer = createServer(app);

server.installSubscriptionHandlers(httpServer);

httpServer.listen(PORT, () => {
  console.log(`馃殌 Server ready at http://localhost:${PORT}${server.graphqlPath}`);
  console.log(`馃殌 Subscriptions ready at ws://localhost:${PORT}${server.subscriptionsPath}`);
});
