var express = require('express');
var { graphqlHTTP } = require('express-graphql');
var { buildSchema } = require('graphql');
var mysql = require('mysql');
var con = mysql.createConnection({
    host: "192.168.10.2",
    port: "3307",
    user: "graphql",
    password: "jE4-Wl5oln",
    database: "graphQL"
});

con.connect(function(err){
    if (err) throw err;
    con.query("SELECT * FROM customers", function (err, result, fields) {
    if (err) throw err;
    console.log(result);
  });
})


/**
 * Copyright (c) 2015, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 */

 import {
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLEnumType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString
  } from 'graphql';
  
  import { makeExecutableSchema } from 'graphql-tools';
  
  import { PubSub, SubscriptionManager, withFilter } from 'graphql-subscriptions';
  
  const pubsub = new PubSub();
  const ADDED_REVIEW_TOPIC = 'new_review';
  
  const schemaString = `
  schema {
    query: Query
    mutation: Mutation
    subscription: Subscription
  }

  # The query type, represents all of the entry points into our object graph
  type Query {
    messages: [Message]
    authors: [Author]
    getMessage(id: ID!): Message
    getAuthor(id: ID!): Author
  }

  # The mutation type, represents all updates we can make to our data
  type Mutation {
    createMessage(input: MessageInput): Message
    createAuthor(input: AuthorInput): Author
    updateMessage(id: ID!, input: MessageInput): Message
    updateAuthor(id: ID!, input: AuthorInput): Author
    deleteMessage(id: ID!): Message
    deleteAuthor(id: ID!): Author
  }

  # The subscription type, represents all subscriptions we can make to our data
  type Subscription {
  }



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
  `;
  
  /**
   * This defines a basic set of data for our Star Wars Schema.
   *
   * This data is hard coded for the sake of the demo, but you could imagine
   * fetching this data from a backend service rather than from hardcoded
   * JSON objects in a more complex demo.
   */
  
  const messages = [
    {
        m_id: '1',
        content: 'Test Message',
        author: '1',
    },
    {
        m_id: '2',
        content: 'Test Message 2',
        author: '1',
    },
    {
        m_id: '3',
        content: 'This is another test Message',
        author: '2',
    },
    {
        m_id: '4',
        content: 'Test Message',
        author: '1',
    },
  ];
  
  const messageData = {};
  messages.forEach((message) => {
    messageData[message.m_id] = message;
  });
  
  const authors = [
    {
        a_id: '1',
        firstName: 'Neo',
        lastName: 'Cheung',
    },
    {
        a_id: '2',
        firstName: 'Jianing',
        lastName: 'Li',
    },
    {
        a_id: '3',
        firstName: 'Lejing',
        lastName: 'Huang',
    },
  ];
  
  const authorData = {};
  authors.forEach((author) => {
    authorData[author.a_id] = author;
  });




  function getMessages() {

    return messageData;
  }
  
  function getAuthors() {
    return authorData;
  }
  
  function getMessage(m_id) {
    return messageData.map((msg) => {
        return {
            ...msg, author: getAuthor(msg.author)
        }    
    })
  }

  function getAuthor(a_id) {
    return authorData[a_id];
  }
  
  function createMessage(input) {
    if (authorData.find(Author => Author.a_id === input.authorId) == null) {
        throw new Error('no author exists with id ' + id);
      }
      // Create a random id for our "database".
      var id = require('crypto').randomBytes(10).toString('hex');
      var data = {};
      data.content = input.content;
      data.authorId = input.authorId;
      messageData[id] = data;
      return new Message(id, input);
  }

  function createAuthor(input) {
    // Create a random id for our "database".
    var id = require('crypto').randomBytes(10).toString('hex');

    var data = {};
    data.firstName = input.firstName;
    data.lastName = input.lastName;
    authorData[id] = data;
    return new Author(id, input);
  }

  function updateMessage (id, input) {
    if (!messageData[id]) {
        throw new Error('no message exists with id ' + id);
      }
      // This replaces all old data, but some apps might want partial update.
      messageData[id] = input;
      return new Message(id, input);
  }

  function updateAuthor (id, input) {
    if (!authorData[id]) {
        throw new Error('no author exists with id ' + id);
      }
      // This replaces all old data, but some apps might want partial update.
      authorData[id] = input;
      return new Author(id, input);
  }

  function deleteMessage (id) {
    if (!messageData[id]) {
        throw new Error('no message exists with id ' + id);
      }
      // This replaces all old data, but some apps might want partial update.
      delete messageData[id];
      return null;
  }

  function deleteAuthor (id) {
    if (!authorData[id]) {
        throw new Error('no author exists with id ' + id);
      }
      // This replaces all old data, but some apps might want partial update.
      delete authorData[id];
      return null;
  }



  
  function toCursor(str) {
    return Buffer("cursor" + str).toString('base64');
  }
  
  function fromCursor(str) {
    return Buffer.from(str, 'base64').toString().slice(6);
  }
  
  const resolvers = {
    Query: {
      messages: (root) => getMessages(),
      authors: (root) => getAuthors(),
      getMessage: (root, { m_id }) => getMessage(m_id),
      getAuthor: (root, { a_id }) => getAuthor(a_id),
    },
    Mutation: {
      createMessage: (root, { messageInput }) => createMessage(messageInput),
      createAuthor: (root, { authorInput }) => createAuthor(authorInput),
      updateMessage: (root, { id, messageInput }) => updateMessage(id, messageInput),
      updateAuthor: (root, { id, authorInput }) => updateAuthor(id, authorInput),
      deleteMessage: (root, { id }) => deleteMessage(id),
      deleteAuthor: (root, { id }) => deleteAuthor(id),
    },
    Subscription: {
      
    },



  }
  
  /**
   * Finally, we construct our schema (whose starting query type is the query
   * type we defined above) and export it.
   */
  export const StarWarsSchema = makeExecutableSchema({
    typeDefs: [schemaString],
    resolvers
  });
  



