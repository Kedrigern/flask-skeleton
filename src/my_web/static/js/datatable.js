/**
 * Wrapper over Tabulator for easy use across the whole application.
 * It handles:
 * - Loading data from the API (Remote Pagination/Sorting/Filtering)
 * - Automatic theme switching (Dark/Light)
 * - Default settings (Layout, Height)
 **/
class DataTable {
    constructor(selector, options) {
        this.selector = selector;
        this.apiUrl = options.apiUrl;

        const defaults = {
            height: "500px",
            layout: "fitColumns",
            placeholder: "No Data Available",

            pagination: true,
            paginationMode: "remote",
            sortMode: "remote",
            filterMode: "remote",
            paginationSize: 10,
            paginationSizeSelector: [5, 10, 25, 50],

            ajaxURL: this.apiUrl,
            ajaxURLGenerator: this._ajaxUrlGenerator.bind(this),
        };

        this.config = { ...defaults, ...options };

        // Vytvoření instance (žádné theme handlery!)
        this.table = new Tabulator(this.selector, this.config);
    }

    _ajaxUrlGenerator(url, config, params) {
        const queryParts = [];
        if (params.page) queryParts.push("page=" + params.page);
        if (params.size) queryParts.push("size=" + params.size);
        if (params.sort && params.sort.length > 0) {
            queryParts.push("sort=" + encodeURIComponent(JSON.stringify(params.sort)));
        }
        if (params.filter && params.filter.length > 0) {
            queryParts.push("filter=" + encodeURIComponent(JSON.stringify(params.filter)));
        }
        return url + (url.includes("?") ? "&" : "?") + queryParts.join("&");
    }

    static getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }
}

window.DataTable = DataTable;