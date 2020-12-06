import React, { Component } from "react";

type HistoryProps = {
    data: string[];
};

export default class History extends Component<HistoryProps> {
    public render() {
        const history = this.props.data.slice().reverse();
        return (
            <div id="history">
                <div className="title">Recent history:</div>
                <div id="history-clips">
                    {history.map((clip) => (
                        <div className="clip" key={clip}>
                            {clip}
                        </div>
                    ))}
                </div>
            </div>
        );
    }
}
