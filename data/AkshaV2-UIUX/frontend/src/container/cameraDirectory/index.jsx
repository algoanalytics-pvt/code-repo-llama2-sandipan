import React from "react";
import Tabs from "../../component/Tabs";
import List from "./List";  //runs List/index.js

//component show a tab Camera Directory on top with its respective component  <List /> below it

// camera directory tabs
const CameraDirectory = () => {
  return (
    <div style={{ marginTop: 58 }}>
      <Tabs
        tabName={[
          {
            value: "one",
            label:"Camera Directory"
          },
        ]}
        pages={[
          {
            value: "one",
            component: <List />,
          },
        ]}
      />
    </div>
  );
};

export default CameraDirectory;
