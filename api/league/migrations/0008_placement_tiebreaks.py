from collections import defaultdict

from django.db import migrations, models


def backfill_placements(apps, schema_editor):
    Standing = apps.get_model("league", "LeagueStanding")
    Result = apps.get_model("result", "Result")
    Resolution = apps.get_model("league", "LeagueTieResolution")
    Entry = apps.get_model("league", "LeagueTieResolutionEntry")
    db = schema_editor.connection.alias

    for league_id in Standing.objects.using(db).values_list("league_id", flat=True).distinct():
        games = defaultdict(list)
        for game_id, player_id, position in Result.objects.using(db).filter(
            league_id=league_id
        ).values_list("selected_game_id", "player_profile_id", "position"):
            games[game_id].append((player_id, position))

        counts = defaultdict(lambda: [0, 0])
        for rows in games.values():
            for player_id, position in rows:
                rank = 1 + sum(
                    (other if other is not None else 999) < (position if position is not None else 999)
                    for _, other in rows
                )
                if rank in (2, 3):
                    counts[player_id][rank - 2] += 1

        standings = list(Standing.objects.using(db).filter(league_id=league_id))
        groups = defaultdict(list)
        for standing in standings:
            standing.second_places, standing.third_places = counts[standing.player_profile_id]
            key = (f"lp:{standing.league_points:.2f}|w:{standing.wins:.2f}"
                   f"|s:{standing.second_places}|t:{standing.third_places}")
            groups[key].append(standing)
            standing.tie_break_priority = 0
            standing.unresolved_tie_group = None

        for key, members in groups.items():
            if len(members) < 2:
                continue
            member_ids = {member.player_profile_id for member in members}
            for member in members:
                member.unresolved_tie_group = key
            for resolution in Resolution.objects.using(db).filter(league_id=league_id):
                entries = list(Entry.objects.using(db).filter(resolution_id=resolution.id).order_by("order_index"))
                if {entry.player_profile_id for entry in entries} != member_ids:
                    continue
                if resolution.group_key != key and not Resolution.objects.using(db).filter(league_id=league_id, group_key=key).exists():
                    resolution.group_key = key
                    resolution.save(using=db, update_fields=["group_key"])
                if resolution.group_key == key and resolution.is_resolved:
                    priorities = {entry.player_profile_id: len(entries) - i for i, entry in enumerate(entries)}
                    for member in members:
                        member.tie_break_priority = priorities[member.player_profile_id]
                break

        Standing.objects.using(db).bulk_update(
            standings, ["second_places", "third_places", "unresolved_tie_group", "tie_break_priority"]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("league", "0007_leaguetieresolution_leaguetieresolutionentry_and_more"),
        ("result", "0011_elochange"),
    ]

    operations = [
        migrations.AddField(model_name="leaguestanding", name="second_places", field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name="leaguestanding", name="third_places", field=models.PositiveIntegerField(default=0)),
        migrations.RunPython(backfill_placements, migrations.RunPython.noop),
    ]