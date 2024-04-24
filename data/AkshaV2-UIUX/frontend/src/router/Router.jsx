// This component uses the Routes and Route components from the react-router-dom library to define routes for different pages in the application.
// The component defines a constant called Router that renders a header and sets up the routes for the application using the Routes component. 
// The routes are defined using the Route component, which takes a path prop and an element prop that specifies the component to render when the route is matched. 
// The Protected component is used to wrap routes that require authentication, and takes a isLoggedIn prop that determines whether the user is authenticated or not.

// The component also checks if the user is authenticated by reading a boolean value from the localStorage object, and converts it to a Boolean using JSON.parse.


import React from "react";
import Header from "../header/Header";
import { Routes, Route, Navigate } from "react-router-dom";
import Protected from "../component/common/protected";
import Monitor from "../container/monitor";
import Investigation from "../container/investigation";
import Insights from "../container/insights";
import CameraDirectory from "../container/cameraDirectory";
import EditCameraDirectory from "../container/cameraDirectory/List/Edit";
// import AddAlert from "../component/video_menu/AlertModal";
import Login from "../container/login";
import ForgotPassword from "../container/forgotPassword";
import { useEffect } from "react";
import Alerts from "../component/common/customAlertModal/Alerts";

// router functional component for protected routes
const Router = () => {

  // check if user is logged in
  let isLoggedIn = window.localStorage.getItem("isLoggedIn");
  // setting protected routes
  return (
    <div>
      <Header />
      <Routes>
        <Route 
          path="/" 
          element={
            // <Protected isLoggedIn={JSON.parse(isLoggedIn)}>
              <Monitor />
            // </Protected>
          } 
        />
        <Route path="/forgotPassword" element={<ForgotPassword />} />
        <Route
          path="/monitor"
          element={
            // <Protected isLoggedIn={JSON.parse(isLoggedIn)}>
              <Monitor />
            // </Protected>
          }
        />
        <Route
          path="/investigation"
          element={
            // <Protected isLoggedIn={JSON.parse(isLoggedIn)}>
              <Investigation />
            // </Protected>
          }
        />
        <Route
          path="/insights"
          element={
            // <Protected isLoggedIn={JSON.parse(isLoggedIn)}>
              <Insights />
            // </Protected>
          }
        />
        <Route
          path="/cameraDirectory"
          element={
            <Protected isLoggedIn={JSON.parse(isLoggedIn)}>
              <CameraDirectory />
            </Protected>
          }
        />
        <Route
          path="/cameraDirectory/edit"
          element={
            <Protected isLoggedIn={JSON.parse(isLoggedIn)}>
              <EditCameraDirectory />
            </Protected>
          }
        />
        <Route
          path="/alert"
          element={
            <Protected isLoggedIn={JSON.parse(isLoggedIn)}>
              {/* <AddAlert /> */}
              <Alerts
                calledInsideMenu={true}
              />
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
};

export default Router;
