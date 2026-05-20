from django.db import migrations


def create_winconditions_and_remap(apps, schema_editor):
    """
    For each ResultConfig create a default WinCondition ("Punkte", POINTS),
    then point every existing TieBreaker.result_config at that new WinCondition
    via the new win_condition FK.
    """
    ResultConfig = apps.get_model("game", "ResultConfig")
    WinCondition = apps.get_model("game", "WinCondition")
    TieBreaker = apps.get_model("game", "TieBreaker")

    rc_to_wc = {}
    for rc in ResultConfig.objects.all():
        wc = WinCondition.objects.create(
            result_config=rc,
            name="Punkte",
            condition_type="POINTS",
            order=0,
        )
        rc_to_wc[rc.pk] = wc.pk

    for tb in TieBreaker.objects.all():
        wc_pk = rc_to_wc.get(tb.result_config_id)
        if wc_pk is None:
            # Safety net: create a WinCondition on demand for the orphan ResultConfig.
            wc = WinCondition.objects.create(
                result_config_id=tb.result_config_id,
                name="Punkte",
                condition_type="POINTS",
                order=0,
            )
            wc_pk = wc.pk
            rc_to_wc[tb.result_config_id] = wc_pk
        tb.win_condition_id = wc_pk
        tb.save(update_fields=["win_condition"])


def reverse_remap(apps, schema_editor):
    """
    Reverse: clear the win_condition FK on TieBreaker and delete all WinConditions.
    result_config is still present at this migration stage so TieBreakers remain valid.
    """
    TieBreaker = apps.get_model("game", "TieBreaker")
    WinCondition = apps.get_model("game", "WinCondition")

    TieBreaker.objects.update(win_condition=None)
    WinCondition.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0017_wincondition_winconditionoption_and_more"),
    ]

    operations = [
        migrations.RunPython(create_winconditions_and_remap, reverse_remap),
    ]
