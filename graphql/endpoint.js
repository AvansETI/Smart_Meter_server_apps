import graphserver from 'graphql-yoga';
const { GraphQLServer } = graphserver;
import graphqlscalar from 'graphql';
const {GraphQLScalarType, Kind} = graphqlscalar;
import mongoose from 'mongoose';
import jwt from "jsonwebtoken";
import graphshield from "graphql-shield";
const { rule, shield, and, or, not } = graphshield;


mongoose.connect("mongodb://192.168.5.20:27017/SmartMeterData",{useNewUrlParser: true, useUnifiedTopology: true});

var Measurement = mongoose.Schema({
        _id: mongoose.Schema.ObjectId,
        signature: String,
        p1_decoded: {
                manufacturer: String,
                version: String,
                equipment_id: String,
                tariff: Number,
                power: {
                        delivered: {
                                value: Number,
                                unit: String
                        },
                        received: {
                                value: Number,
                                unit: String
                        }
                },
                energy: [{
                        tariff: Number,
                        delivered: {
                                value: Number,
                                unit: String
                        },
                        received: {
                                value: Number,
                                unit: String
                        }
                }],
                phases: {
                        failures: mongoose.Mixed,
                        long_failures: mongoose.Mixed,
                        phases: [{
                                phase: String,
                                sags: mongoose.Mixed,
                                swells: mongoose.Mixed,
                                instantaneous_voltage: {
                                        value: mongoose.Mixed,
                                        unit: mongoose.Mixed
                                },
                                instantaneous_current: {
                                        value: mongoose.Mixed,
                                        unit: mongoose.Mixed
                                },
                                instantaneous_power_positive: {
                                        value: mongoose.Mixed,
                                        unit: mongoose.Mixed
                                },
                                instantaneous_power_negative: {
                                        value: mongoose.Mixed,
                                        unit: mongoose.Mixed
                                }
                        }]
                }

        },
        s0: {
                unit: String,
                label: String,
                value: Number
        },
        s1: {
                unit: String,
                label: String,
                value: Number
        }
}, {collection: "smart_meter_data_decoded", timestamps: true});

const mongooseschema = mongoose.model('Measurement', Measurement);

const MAX_INT = 2147483647
const MIN_INT = -2147483648
const coerceIntString = (value) => {
  if (Array.isArray(value)) {
    throw new TypeError(`IntString cannot represent an array value: [${String(value)}]`)
  }
  if (Number.isInteger(value)) {
    if (value < MIN_INT || value > MAX_INT) {
      throw new TypeError(`Value is integer but outside of valid range for 32-bit signed integer: ${String(value)}`)
    }
    return value
  }
  return String(value)
}
function checkNumberIfFloat(value) {
        return Number(value) === value && value % 1 !== 0;
 }
const coerceFloatString = (value) => {
        if (Array.isArray(value)) {
          throw new TypeError(`IntString cannot represent an array value: [${String(value)}]`)
        }
        if (checkNumberIfFloat(value)) {
          return value
        }
        return String(value)
  }

const resolvers = {
        IntString: new GraphQLScalarType({
                name: 'IntString',
                serialize: coerceIntString,
                parseValue: coerceIntString,
                parseLiteral(ast) {
                  if (ast.kind === Kind.INT) {
                        return coerceIntString(parseInt(ast.value, 10))
                  }
                  if (ast.kind === Kind.STRING) {
                        return ast.value
                  }
                  return undefined
                }
          }),
          FloatString: new GraphQLScalarType({
                name: 'FloatString',
                serialize: coerceFloatString,
                parseValue: coerceFloatString,
                parseLiteral(ast) {
                  if (ast.kind === Kind.FLOAT) {
                        return coerceFloatString(parseFloat(ast.value))
                  }
                  if (ast.kind === Kind.STRING) {
                        return ast.value
                  }
                  return undefined
                }
          }),
        Measurement: {
                createdAt(obj, args, context, info) {
                        return new Date(obj.createdAt).toISOString()
                }
        },
        Delivered: {
                value(obj, args, context, info){
                        return parseFloat(obj.value.toString())
                }
        },
        Received: {
                value(obj, args, context, info){
                        return parseFloat(obj.value.toString())
                }
        },
    Query: {
                getMeasurement: async (_,{id}) => {
                        return await mongooseschema.findById(id);
                },

                getAvailableMeters: async() => {
                        return await mongooseschema.find().distinct('signature', function(error, signatures) {});
                },

                getMeasurmentsLatest: async (_,{page}) => {
                        if(page === null || page < 1){ page = 1 }
                        var documents = 100
                        return await mongooseschema.find({"createdAt":{$gte:new Date((new Date().getTime() - (24 * 60 * 60 * 1000)))}}).skip((page-1)*documents).limit(documents)
                },

                getRecentRecordsBySignature: async (_,{signature,amount}) => {
                        if(amount <= 0|| amount === null){return null}
                        let result = await mongooseschema.find({"signature":signature}).sort({ _id: -1}).limit(amount)

                        result = result.reverse();
                        //if(result.length <= 200) return result;

                        /*var interval = Math.round(result.length / 200);
                        console.log("interval: " + interval);

                        var aggList = [];
                        var i;
                        for(i = 0; i < result.length; i = i + interval){
                            aggList.push(result[i]);
                            console.log(i)
                        }*/
                        return result;
                },

                getMeasurementFromDates: async(_,{from, till, page}) => {
                        return  await mongooseschema.find({"createdAt":{$gt:new Date(from + 'Z').toISOString(), $lt:new Date(till+ 'Z').toISOString()}})
                },

                getMeasurementFromDatesBySignature: async(_,{from, till, id, page}) => {
                        return await mongooseschema.find({"signature":id,"createdAt":{$gt:new Date(from + 'Z').toISOString(), $lt:new Date(till+ 'Z').toISOString()}})

                },

                getEnergyFromDatesBySignature: async(_,{from, till, id}) => {
                        var total = [];
                        var start = await mongooseschema.find({"signature":id,"createdAt":{$gt:new Date(from + 'Z').toISOString(), $lt:new Date(till+ 'Z').toISOString()}}).limit(1);
                        var stop = await mongooseschema.find({"signature":id,"createdAt":{$gt:new Date(from + 'Z').toISOString(), $lt:new Date(till+ 'Z').toISOString()}}).sort({ _id: -1}).limit(1);
                        total[0] = start[0];
                        total[1] = stop[0];
                        return total;
                },


                getJWT: async() => {
                        const token = jwt.sign({ claims: 'read-post', exp: Math.floor(Date.now() / 1000) + (60 * 60 * 24 * 30)}, 'URaiLP26Vq', {
                                algorithm: 'HS256',
                        });
                        return token;
                }
        }
}

function getClaims(req) {
    let token;
    try {
        token = jwt.verify(req.request.get("Authorization"), "URaiLP26Vq");
    } catch (e) {
        return null;
        }
    return token.claims;
}



// Rules
const canReadposts = rule()(async (parent, args, ctx, info) => {
    return ctx.claims === "read-post";
});

// Permissions
const permissions = shield({
    Query: {
                getMeasurement: canReadposts,
                getAvailableMeters: canReadposts,
                getRecentRecordsBySignature: canReadposts,
                getMeasurementFromDates: canReadposts,
                getMeasurementFromDatesBySignature: canReadposts,
                getMeasurmentsLatest: canReadposts,
                getEnergyFromDatesBySignature: canReadposts
    },
});

const server = new GraphQLServer({
    typeDefs: 'schema.graphql',
    resolvers,
    mongooseschema,
    tracing: true,
    playground: true,
    introspection: true,
    middlewares: [permissions],
    context: req => ({
        ...req,
        claims: getClaims(req)
    })
});
server.start(() => console.log('Server is running on localhost:4000'))


