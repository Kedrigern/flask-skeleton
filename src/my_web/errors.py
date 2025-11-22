from http import HTTPStatus
from flask import Flask, jsonify, request, render_template
from pydantic import ValidationError


class ResourceNotFound(Exception):
    """
    Raised when a requested resource (e.g., database record) is not found.
    Results in a 404 HTTP response.
    """

    pass


class BusinessError(ValueError):
    """
    Raised when a business rule is violated (e.g., duplicate entry, invalid state).
    Results in a 409 Conflict HTTP response.
    """

    pass


def register_error_handlers(app: Flask):
    """
    Registers global error handlers for the Flask application.
    This allows controllers/views to focus on the 'happy path' logic.
    """

    @app.errorhandler(404)
    def not_found_error(error):
        # Distinguish between API (JSON) and Browser (HTML) requests
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), HTTPStatus.NOT_FOUND
        return render_template("errors/404.html"), HTTPStatus.NOT_FOUND

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith("/api/"):
            return jsonify(
                {"error": "Internal server error"}
            ), HTTPStatus.INTERNAL_SERVER_ERROR
        return render_template("errors/500.html"), HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(ValidationError)
    def handle_pydantic_validation_error(e):
        """
        Handles Pydantic validation errors (input data validation).
        Returns 400 Bad Request with details.
        """
        return jsonify(
            {"error": "Validation error", "details": e.errors()}
        ), HTTPStatus.BAD_REQUEST

    @app.errorhandler(ResourceNotFound)
    def handle_resource_not_found(e):
        """
        Handles explicit ResourceNotFound exceptions from services.
        Returns 404 Not Found.
        """
        return jsonify({"error": str(e) or "Not Found"}), HTTPStatus.NOT_FOUND

    @app.errorhandler(ValueError)
    @app.errorhandler(BusinessError)
    def handle_business_error(e):
        """
        Handles general business logic errors (e.g., integrity errors).
        Returns 409 Conflict.
        """
        return jsonify({"error": str(e)}), HTTPStatus.CONFLICT
