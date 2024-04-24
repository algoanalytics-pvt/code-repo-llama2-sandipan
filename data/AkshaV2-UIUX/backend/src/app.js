import express from "express";
import cors from "cors";
const bodyParser = require('body-parser');
import "./db/connection";
import path from "path";
import alerts from "./routes/alerts";
import investigation from "./routes/investigation";
import cameras from "./routes/cameras";
import myAlerts from "./routes/myAlerts";
import insight from "./routes/insight";
import insightReport from "./routes/insightReport";
import days from "./routes/days";
import monitor from "./routes/monitor";
import notification from "./routes/notification";
import fs from "fs";
// const compression = require("compression");
// const helmet = require("helmet");

const app = express();
// app.use(compression()); // Compress all routes
// app.use(helmet({
//   crossOriginResourcePolicy: false,
// })); 

// Try Again
app.use(cors());
app.use(bodyParser.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(`${process.cwd()}/Aksha`)));
// app.disable('x-powered-by')

function apiTimeOut(req, res, next) {
  res.setTimeout(30000);
  next();
}

app.use("/api", alerts, apiTimeOut);
app.use("/api", investigation, apiTimeOut);
app.use("/api", cameras, apiTimeOut);
app.use("/api", myAlerts, apiTimeOut);
app.use("/api", insight, apiTimeOut);
app.use("/api", insightReport, apiTimeOut);
app.use("/api", days, apiTimeOut);
app.use("/api", notification, apiTimeOut);
app.use("/api", monitor, apiTimeOut);

export default app;
