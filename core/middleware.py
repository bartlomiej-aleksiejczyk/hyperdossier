class SimpleCORSMiddleware:
    """
    Minimal CORS middleware without third-party deps.
    Allows all origins for demo \u2014 tighten in prod.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "http://192.168.0.25:8081"
        response["Vary"] = "Origin"
        origin = request.headers.get("Origin")
        if origin:
            # allow the requesting origin (or use a whitelist check here)
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
            response["Access-Control-Allow-Headers"] = (
                "Origin, Content-Type, Accept, Authorization, X-Requested-With"
            )
            response["Access-Control-Allow-Credentials"] = "true"

        # respond immediately to preflight OPTIONS requests
        if request.method == "OPTIONS":
            response.status_code = 200

        return response
