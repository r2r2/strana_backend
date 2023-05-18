from .classes import Favorite


class FavoriteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.favorite = Favorite(request.session)
        response = self.get_response(request)
        return response
