import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from custom_privacy_app.models import AccessLevel, DataFile, Team


class Command(BaseCommand):
    help = "Benchmark queries for retrieving DataFiles with different access levels"

    def handle(self, *args, **kwargs):
        # Get test users.
        user1 = User.objects.get(username="testuser1")
        user2 = User.objects.get(username="testuser2")

        # Get teams.
        team1 = Team.objects.get(name="Custom Team Alpha")
        team2 = Team.objects.get(name="Custom Team Beta")

        self.stdout.write("\nStarting benchmark...\n")

        # Repeated runs to warm up caches and get average times.
        repeat = 3

        # Full fetch of different queries.
        self._benchmark_query_fetch(
            "Public Data (full fetch)",
            DataFile.objects.filter(access_level=AccessLevel.PUBLIC),
            repeat=repeat,
        )
        self._benchmark_query_fetch(
            "Team Data (Team1, full fetch)",
            DataFile.objects.filter(access_level=AccessLevel.TEAM, teams=team1),
            repeat=repeat,
        )

        # Partial fetch (only id/name).
        self._benchmark_query_fetch(
            "Public Data (partial fetch)",
            DataFile.objects.filter(access_level=AccessLevel.PUBLIC).only("id", "name"),
            repeat=repeat,
        )
        self._benchmark_query_fetch(
            "Team Data (Team1, partial fetch)",
            DataFile.objects.filter(access_level=AccessLevel.TEAM, teams=team1).only(
                "id", "name"
            ),
            repeat=repeat,
        )

        # Limited fetch.
        self._benchmark_query_fetch(
            "Public Data (limit 1000)",
            DataFile.objects.filter(access_level=AccessLevel.PUBLIC).order_by("id")[
                :1000
            ],
            repeat=repeat,
        )
        self._benchmark_query_fetch(
            "Team Data (Team1, limit 1000)",
            DataFile.objects.filter(
                access_level=AccessLevel.TEAM, teams=team1
            ).order_by("id")[:1000],
            repeat=repeat,
        )

        # 4) Private data checks for user1.
        self._benchmark_query_fetch(
            "Private Data (User1, full fetch)",
            DataFile.objects.filter(access_level=AccessLevel.PRIVATE, owner=user1),
            repeat=repeat,
        )

        self._benchmark_query_fetch(
            "Team Data (Team2, limit 1000)",
            DataFile.objects.filter(
                access_level=AccessLevel.TEAM, teams=team2
            ).order_by("id")[:1000],
            repeat=repeat,
        )

        # 4) Private data checks for user1.
        self._benchmark_query_fetch(
            "Private Data (User2, full fetch)",
            DataFile.objects.filter(access_level=AccessLevel.PRIVATE, owner=user2),
            repeat=repeat,
        )

        self.stdout.write("\nBenchmark completed.")

    def _benchmark_query_fetch(self, label, queryset, repeat=1):
        durations = []
        fetched_count = 0

        for _ in range(repeat):
            start_time = time.perf_counter()

            # Actually fetch data by converting queryset to a list.
            data = list(queryset)

            duration = time.perf_counter() - start_time
            durations.append(duration)

            fetched_count = len(data)

        avg_duration = sum(durations) / repeat
        self.stdout.write(
            f"{label}: {fetched_count} records fetched. "
            f"Average time {avg_duration:.6f} seconds over {repeat} runs"
        )
