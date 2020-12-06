import React, { Component } from "react";

export default class Header extends Component {
    public render() {
        return (<div id="header">
            <img alt="logo" src="/static/img/icon.svg"/>
            <span>py-radio</span>
        </div>);
    }
}
