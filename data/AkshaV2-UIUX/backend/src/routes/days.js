import express from "express";
import fs from "fs";
const router = express.Router();

router.get(process.env.DAYS, (req, res) => {
  let workday = req.query;
  if (!req.query.workday) {
    return res.status(400).json({
      success: false,
      message: "please provide popper data",
    });
  }
  try {
    fs.writeFileSync(
      `${process.cwd()}/utils/global.json`,
      JSON.stringify(workday),
      "utf8"
    );

    res.status(200).json({
      success: true,
      message: "response has been submitted",
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
    });
  }
});

export default router;
