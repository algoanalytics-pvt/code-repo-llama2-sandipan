import "dotenv/config";
import app from "./app";
import http from "http";
const debug = require("debug")("author");
const PORT = process.env.PORT;
const server = http.createServer(app);
const {Server } = require("socket.io");
global.io = new Server(server, {cors: {origin: "*"}});

import observer from "../utils/observer";



observer(server, app).listen(PORT, () => {
  debug(`server is running on ${PORT}`);
});
