import { MongoClient } from 'mongodb';
import { env } from '$env/dynamic/private';
import * as v from 'valibot';

if (!env.MONGODB_URI) throw new Error('MONGODB_URI is not set');

const client = new MongoClient(env.MONGODB_URI);

export const db = client.db('wikimedia');