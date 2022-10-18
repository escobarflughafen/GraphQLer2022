var express = require('express');
var { graphqlHTTP } = require('express-graphql');
var { buildSchema } = require('graphql');

// Construct a schema, using GraphQL schema language
var schema = buildSchema(`
  input MessageInput {
    content: String
    authorId: String
  }

  input AuthorInput {
    firstName: String
    lastName: String
  }

  type Message {
    id: ID!
    content: String
    author: Author
  }

  type Author {
    id: ID!
    firstName: String
    lastName: String
  }

  type Query {
    messages: [Message]
    authors: [Author]
    getMessage(id: ID!): Message
    getAuthor(id: ID!): Author
  }

  type Mutation {
    createMessage(input: MessageInput): Message
    createAuthor(input: AuthorInput): Author
    updateMessage(id: ID!, input: MessageInput): Message
    updateAuthor(id: ID!, input: AuthorInput): Author
    deleteMessage(id: ID!): Message
    deleteAuthor(id: ID!): Author
  }
`);

// If Message had any complex fields, we'd put them on this object.
class Message {
  constructor(id, {content, authorId}) {
    this.id = id;
    this.content = content;
    this.author = authorId
  }
}

class Author {
  constructor(id, {firstName, lastName}) {
    this.id = id;
    this.firstName = firstName;
    this.lastName = lastName;
  }
}

// Maps username to content
var fakeDatabase = [];
var fakeAuthor = [];

var root = {
  messages: () => {
    return fakeDatabase;
  },
  authors: () => {
    return fakeAuthor;
  },
  getMessage: ({id}) => {
    if (fakeDatabase.find(Message => Message.id === id) == null) {
      throw new Error('no message exists with id ' + id);
    }
    var data = fakeDatabase.find(Message => Message.id === id);
    return {
      id,
      ...data,
      author: {id: data.authorId, ...fakeAuthor.find(Author => Author.id === data.authorId),
      }
    }
  },
  getAuthor: ({id}) => {
    if (fakeAuthor.find(Author => Author.id === id) == null) {
      throw new Error('no author exists with id ' + id);
    }
    return fakeAuthor.find(Author => Author.id === id);
  },
  createMessage: ({input}) => {
    if (fakeAuthor.find(Author => Author.id === input.authorId) == null) {
      throw new Error('no author exists with id ' + id);
    }
    // Create a random id for our "database".
    var id = require('crypto').randomBytes(10).toString('hex');
    var data = {};
    data.id = id;
    data.content = input.content;
    data.authorId
    fakeDatabase.push(data);
    return new Message(id, input);
  },
  createAuthor: ({input}) => {
    // Create a random id for our "database".
    var id = require('crypto').randomBytes(10).toString('hex');

    var data = {};
    data.id = id;
    data.firstName = input.firstName;
    data.lastName = input.lastName;
    fakeAuthor.push(data);
    return new Author(id, input);
  },
  updateMessage: ({id, input}) => {
    if (!fakeDatabase[id]) {
      throw new Error('no message exists with id ' + id);
    }
    // This replaces all old data, but some apps might want partial update.
    fakeDatabase[id] = input;
    return new Message(id, input);
  },
  updateAuthor: ({id, input}) => {
    if (!fakeAuthor[id]) {
      throw new Error('no author exists with id ' + id);
    }
    // This replaces all old data, but some apps might want partial update.
    fakeAuthor[id] = input;
    return new Author(id, input);
  },
  deleteMessage: ({id}) => {
    if (!fakeDatabase[id]) {
      throw new Error('no message exists with id ' + id);
    }
    // This replaces all old data, but some apps might want partial update.
    delete fakeDatabase[id];
    return null;
  },
  deleteAuthor: ({id}) => {
    if (!fakeAuthor[id]) {
      throw new Error('no author exists with id ' + id);
    }
    // This replaces all old data, but some apps might want partial update.
    delete fakeAuthor[id];
    return null;
  },

};

var app = express();
app.use('/graphql', graphqlHTTP({
  schema: schema,
  rootValue: root,
  graphiql: true,
}));
app.listen(4000, () => {
  console.log('Running a GraphQL API server at localhost:4000/graphql');
});