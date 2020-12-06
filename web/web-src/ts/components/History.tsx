import React, { Component } from "react";

export default class History extends Component {
    public render() {
        return (
            <div id="history">
                <div className="title">Recent history:</div>
                <div id="history-clips"></div>
            </div>
        );
    }
}
