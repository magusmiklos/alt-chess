from django.urls import re_path
from .consumers import matchmaking_consumer, game_consumer

websocket_urlpatterns = [
    re_path(r'^ws/matchmaking/$', matchmaking_consumer.MatchmakingConsumer.as_asgi()),
    re_path(r'^ws/game/(?P<game_group>[a-zA-Z0-9_-]+)$', game_consumer.GameConsumer.as_asgi()),
]
