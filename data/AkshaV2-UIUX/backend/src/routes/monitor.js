import express from "express";
const router=express.Router();

router.post('/monitor', (req, res) => {
      //console.log(req.body);
      //console.log(req.body.camera_name, req.body.camera_img_url); 
      io.emit(req.body.camera_name, req.body.camera_img_url);
      res.status(200).json({
         success:true,
         message: "Successfully Published Image for Camera: " + req.body.camera_name 
         });
});

export default router;

