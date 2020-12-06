import React from "react";
import ReactDOM from "react-dom";
import App from "./components/App";
import PyRadio from "./pyradio";

const root = document.getElementById("root");
const radio = new PyRadio();

ReactDOM.render(React.createElement(App, { radio }), root);
