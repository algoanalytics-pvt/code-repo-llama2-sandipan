import React from "react";
// tab property
export type TabProps = {
  tabName: {
    value: string;
    label: string;
  }[];
  pages: {
    value: string;
    component: any;
  }[];
};
