const DEFAULT_HOST:string = window.location.host;

export default class PyRadio {
    public readonly host: string;

    public constructor(host: string = DEFAULT_HOST) {
        this.host = host;
    }

    public get base_url(): string {
        return `http://${this.host}/api/v1.0`;
    }

    public async api_request<T extends APIBaseResponse>(
        path: string,
        method: HTTPMethod = "GET",
        data: any = null
    ): Promise<T> {
        let init: RequestInitData = {
            method: method,
            cache: "no-store",
            follow: "error",
            body: data,
        };

        if (data === null) {
            delete init.body;
        }

        let response = await fetch(this.base_url + path, init);
        let obj = (await response.json()) as APIResponse;

        return obj.status === "ok"
            ? Promise.resolve(obj as T)
            : Promise.reject(obj as APIErrorResponse);
    }

    public now(): Promise<APINowResponse> {
        return this.api_request("/now");
    }

    public async extensions() {
        const obj = await this.api_request<APIExtensionResponse>("/extensions");
        return obj.extensions;
    }

    public async search(query: string): Promise<string[]> {
        const nice_query = encodeURIComponent(query.trim());

        if (nice_query === "") {
            return Promise.resolve([]);
        }

        const response = await this.api_request<APISearchResponse>(
            "/library/search?query=" + nice_query
        );
        return response.results;
    }

    public async schedule(clip: string): Promise<void> {
        const form = new FormData();
        form.append("file", clip);
        // @ts-ignore
        await this.api_request("/schedule", "POST", new URLSearchParams(form));
    }

    public download_url(clip: string): string {
        return `${this.base_url}/library/download?file=${encodeURIComponent(clip)}`;
    }
}

type HTTPMethod = "GET" | "POST" | "PUT" | "DELETE";

type RequestInitData = RequestInit & { follow: "error" };

type APIErrorResponse = { status: "error"; message: string };

type APIBaseResponse = {
    status: "ok";
};

type APIResponse = APIBaseResponse | APIErrorResponse;

type APINowResponse = {
    status: "ok";
    current: string;
    history: string[];
    library: { hosts: number; music: number; other: number };
};

type APIExtensionResponse = {
    status: "ok";
    extensions: { name: string; command: string }[];
};

type APISearchResponse = {
    status: "ok";
    results: string[];
};
