/**
 * Formatters for Tabulatoru columns.
 */
const Formatters = {
    // List of author, formats array of author objects to string
    authors: function(cell) {
        const authors = cell.getValue();
        if (authors && authors.length > 0) {
            return authors.map(a => a.name).join(", ");
        }
        return "<em style='color: #999;'>No author</em>";
    },

    // Create link to book detail
    bookLink: function(cell) {
        const data = cell.getData();
        const title = cell.getValue();
        return `<a href="/book/${data.id}" class="fw-bold text-decoration-none">${title}</a>`;
    }
};

window.Formatters = Formatters;