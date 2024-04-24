import express from "express";
import fs from "fs";
import path from "path";
const router = express.Router();

router.post(process.env.INSIGHT, (req, res) => {
  const { Start_Date, Start_Time, End_Date, End_Time, Camer_Name } = req.body;

  if (!Start_Date || !Start_Time || !End_Date || !End_Time || !Camer_Name) {
    return res.status(400).json({
      success: false,
      message: "please provide all detail",
      insight: {},
    });
  }

  try {
    let filePath = path.join(
      `${process.cwd()}/Aksha/${Camer_Name}/insight/heatmap_video_${Camer_Name}.mp4`
    );
    fs.stat(filePath, (err, stats) => {
      if (err) {
        // File not found or other error
        return res.status(404).json({
          success: false,
          message: 'Video not found.',
          insight: {},
        });
      }

      if (stats.isFile() && stats.size === 0) {
        // File exists, but it's still empty (being written or incomplete)
        
        return res.status(200).json({
          success: true,
          message: 'Video is still being formed. Please wait',
          insight: {},
        });
      };
      let imageUrl = `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${Camer_Name}/insight/heatmap_video_${Camer_Name}.mp4`  
    return res.status(200).json({
        success: true,
        message: "fetch insight successful",
        insight: {
          camera_Name: Camer_Name,
          image: imageUrl,
        },
      });
  
    

    // res.status(200).json({
    //   success: true,
    //   message: "fetch insight successful",
    //   insight: {},
    // });
  });
} catch (error) {
    res.status(400).json({
      success: false,
      message: error,
      insight: {},
    });
  }
});

export default router;
