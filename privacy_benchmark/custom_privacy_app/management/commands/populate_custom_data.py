import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from custom_privacy_app.models import AccessLevel, DataFile, Team

# Number of entries to create
N_PUBLIC_DATA = 1_000_000
N_AUTHENTICATED_DATA = 1_000_000
N_PRIVATE_USER1_DATA = 1_000
N_PRIVATE_USER2_DATA = 2_000
N_PRIVATE_TEAM1_DATA = 500
N_PRIVATE_TEAM2_DATA = 600

CHUNK_SIZE = 100_000


class Command(BaseCommand):
    help = "Populate database with test data for the Custom Privacy App in batches."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting test data generation...")

        user1, _ = User.objects.get_or_create(username="testuser1")
        user2, _ = User.objects.get_or_create(username="testuser2")
        self.stdout.write("Created test users.")

        team1, _ = Team.objects.get_or_create(name="Custom Team Alpha")
        team2, _ = Team.objects.get_or_create(name="Custom Team Beta")
        self.stdout.write("Created teams.")

        team1.members.add(user1)
        team2.members.add(user2)
        self.stdout.write("Assigned users to teams.")

        # Create Public Data in Chunks
        self._create_data_in_chunks(
            "Public Data",
            N_PUBLIC_DATA,
            lambda idx: DataFile(
                name=f"Public Data {idx}", access_level=AccessLevel.PUBLIC, owner=user1
            ),
        )

        # Create Authenticated Data in Chunks
        self._create_data_in_chunks(
            "Authenticated Data",
            N_AUTHENTICATED_DATA,
            lambda idx: DataFile(
                name=f"Authenticated Data {idx}",
                access_level=AccessLevel.AUTHENTICATED,
                owner=user1,
            ),
        )

        # Create Private Data for User1 (small, can also chunk but not huge)
        self.stdout.write(f"Creating {N_PRIVATE_USER1_DATA} private files for User1...")
        private_data_user1 = [
            DataFile(
                name=f"Private Data User1 - {i}",
                access_level=AccessLevel.PRIVATE,
                owner=user1,
            )
            for i in range(N_PRIVATE_USER1_DATA)
        ]
        DataFile.objects.bulk_create(private_data_user1)
        self.stdout.write(f"Created {N_PRIVATE_USER1_DATA} private files for User1.")

        # Create Private Data for User2
        self.stdout.write(f"Creating {N_PRIVATE_USER2_DATA} private files for User2...")
        private_data_user2 = [
            DataFile(
                name=f"Private Data User2 - {i}",
                access_level=AccessLevel.PRIVATE,
                owner=user2,
            )
            for i in range(N_PRIVATE_USER2_DATA)
        ]
        DataFile.objects.bulk_create(private_data_user2)
        self.stdout.write(f"Created {N_PRIVATE_USER2_DATA} private files for User2.")

        # Create Team Data for Team1
        self.stdout.write(f"Creating {N_PRIVATE_TEAM1_DATA} team files for Team1...")
        team_data_team1 = [
            DataFile(
                name=f"Team Data Team1 - {i}",
                access_level=AccessLevel.TEAM,
                owner=user1,
            )
            for i in range(N_PRIVATE_TEAM1_DATA)
        ]
        DataFile.objects.bulk_create(team_data_team1)
        self.stdout.write(f"Created {N_PRIVATE_TEAM1_DATA} team files for Team1.")

        # Create Team Data for Team2
        self.stdout.write(f"Creating {N_PRIVATE_TEAM2_DATA} team files for Team2...")
        team_data_team2 = [
            DataFile(
                name=f"Team Data Team2 - {i}",
                access_level=AccessLevel.TEAM,
                owner=user2,
            )
            for i in range(N_PRIVATE_TEAM2_DATA)
        ]
        DataFile.objects.bulk_create(team_data_team2)
        self.stdout.write(f"Created {N_PRIVATE_TEAM2_DATA} team files for Team2.")

        # 7) Assign team-based access
        self.stdout.write("Assigning team-based access to team data...")
        # Refresh from DB so we can .add() them
        team_data_team1 = DataFile.objects.filter(name__startswith="Team Data Team1")
        for data in team_data_team1:
            data.teams.add(team1)
        self.stdout.write(f"Assigned {N_PRIVATE_TEAM1_DATA} files to Team1.")

        team_data_team2 = DataFile.objects.filter(name__startswith="Team Data Team2")
        for data in team_data_team2:
            data.teams.add(team2)
        self.stdout.write(f"Assigned {N_PRIVATE_TEAM2_DATA} files to Team2.")

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully completed test data generation with correct access levels."
            )
        )

    def _create_data_in_chunks(self, label, total_count, build_obj_func):
        self.stdout.write(
            f"Creating {total_count} {label} in chunks of {CHUNK_SIZE}..."
        )

        start_time = time.perf_counter()
        created_so_far = 0

        for start in range(0, total_count, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, total_count)

            # Build the chunk
            batch = []
            for idx in range(start, end):
                batch.append(build_obj_func(idx))

            # Bulk create this chunk
            DataFile.objects.bulk_create(batch)

            created_so_far += len(batch)
            self.stdout.write(
                f"{label}: Created {created_so_far}/{total_count} so far..."
            )

        duration = time.perf_counter() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished creating {total_count} {label} in {duration:.2f} seconds."
            )
        )
