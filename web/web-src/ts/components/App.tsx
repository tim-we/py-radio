import React, { Component } from "react";
import PyRadio from "../pyradio";
import About from "./About";
import Controls from "./Controls";
import Header from "./Header";
import History from "./History";
import NowPlaying from "./NowPlaying";

type AppProps = {
    radio: PyRadio;
};

type AppState = {
    now?: { current: string; history: string[] };
    extensions: { name: string; command: string }[];
};

export default class App extends Component<AppProps, AppState> {
    public constructor(props: AppProps) {
        super(props);
        this.state = { extensions: [] };

        props.radio
            .extensions()
            .then((extensions) => this.setState({ extensions }));
    }

    public componentDidMount() {
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "visible") {
                this.update();
            }
        });

        this.update();

        window.setInterval(this.update.bind(this), 3141);
    }

    public render() {
        const props = this.props;
        const state = this.state;

        return (
            <React.Fragment>
                <Header />
                <div id="content">
                    <NowPlaying clip={this.state.now?.current} />
                    <Controls radio={props.radio} extensions={state.extensions}/>
                    <History />
                    <div id="stats"></div>
                </div>
                <About />
            </React.Fragment>
        );
    }

    private async update() {
        if (document.visibilityState !== "visible") {
            return;
        }

        const info = await this.props.radio.now();

        this.setState({
            now: {
                current: info.current,
                history: info.history,
            },
        });
    }
}
