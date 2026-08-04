from django.db import migrations


def map_tiebreakers_to_points(apps, schema_editor):
    """
    Ensure all existing TieBreaker objects are linked to a POINTS WinCondition
    for their respective game.
    """
    ResultConfig = apps.get_model("game", "ResultConfig")
    WinCondition = apps.get_model("game", "WinCondition")
    TieBreaker = apps.get_model("game", "TieBreaker")

    for rc in ResultConfig.objects.all():
        # Find or create a default POINTS WinCondition for this game
        points_wc = WinCondition.objects.filter(
            result_config=rc,
            condition_type="POINTS"
        ).first()

        if not points_wc:
            points_wc = WinCondition.objects.create(
                result_config=rc,
                name="Punkte",
                condition_type="POINTS",
                order=0,
            )

        # Move all tie breakers belonging to this game (via any of its WinConditions)
        # to the POINTS WinCondition.
        all_game_wcs = WinCondition.objects.filter(result_config=rc)
        tbs_to_move = TieBreaker.objects.filter(win_condition__in=all_game_wcs)

        for tb in tbs_to_move:
            if tb.win_condition_id != points_wc.id:
                tb.win_condition = points_wc
                tb.save(update_fields=["win_condition"])


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0020_alter_wincondition_id_alter_winconditionoption_id"),
    ]

    operations = [
        migrations.RunPython(map_tiebreakers_to_points, migrations.RunPython.noop),
    ]
