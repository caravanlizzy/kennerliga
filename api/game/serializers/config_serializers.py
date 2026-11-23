from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from game.models import (
    Faction,
    GameOption,
    GameOptionAvailabilityCondition,
    GameOptionAvailabilityGroup,
    GameOptionChoice,
    Platform,
    ResultConfig,
    SelectedOption,
    StartingPointSystem,
    TieBreaker,
    WinCondition,
    WinConditionOption,
)
from .faction_serializers import FactionSerializer


class GameOptionSerializer(ModelSerializer):
    """
    Serializer for the GameOption model.
    """
    class Meta:
        model = GameOption
        fields = "__all__"


class GameOptionChoiceSerializer(ModelSerializer):
    """
    Serializer for the GameOptionChoice model.
    """
    class Meta:
        model = GameOptionChoice
        fields = "__all__"


class TieBreakerSerializer(ModelSerializer):
    """
    Serializer for the TieBreaker model.
    """
    class Meta:
        model = TieBreaker
        fields = "__all__"


class WinConditionOptionSerializer(ModelSerializer):
    """
    Serializer for the WinConditionOption model.
    """
    class Meta:
        model = WinConditionOption
        fields = "__all__"


class WinConditionSerializer(ModelSerializer):
    """
    Serializer for the WinCondition model, including its options and tie-breakers.
    """
    options = WinConditionOptionSerializer(many=True, read_only=True)
    tie_breakers = TieBreakerSerializer(many=True, read_only=True)

    class Meta:
        model = WinCondition
        fields = "__all__"


class StartingPointSystemSerializer(ModelSerializer):
    """
    Serializer for the StartingPointSystem model.
    """
    class Meta:
        model = StartingPointSystem
        fields = "__all__"


class PlatformSerializer(ModelSerializer):
    """
    Serializer for the Platform model.
    """
    class Meta:
        model = Platform
        fields = "__all__"


class ResultConfigSerializer(ModelSerializer):
    """
    Serializer for the ResultConfig model, including win conditions, factions, and starting point system info.
    Supports atomic nested creation and update of factions, win conditions, options, and tie-breakers.
    """
    starting_points_system_code = serializers.SerializerMethodField(read_only=True)
    starting_points_system_description = serializers.SerializerMethodField(
        read_only=True
    )
    starting_points_system = serializers.PrimaryKeyRelatedField(
        queryset=StartingPointSystem.objects.all(), required=False, allow_null=True
    )
    win_conditions = WinConditionSerializer(many=True, read_only=True)
    factions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ResultConfig
        fields = "__all__"

    def get_starting_points_system_code(self, obj):
        return obj.starting_points_system.code if obj.starting_points_system else None

    def get_starting_points_system_description(self, obj):
        return (
            obj.starting_points_system.description
            if obj.starting_points_system
            else None
        )

    def get_factions(self, obj):
        if not obj.game:
            return []
        factions = Faction.objects.filter(game=obj.game).order_by("level", "name", "id")
        return FactionSerializer(factions, many=True).data

    def _sync_factions(self, game, factions_data):
        if not factions_data:
            Faction.objects.filter(game=game).delete()
            return

        existing_factions = {f.id: f for f in Faction.objects.filter(game=game)}
        retained_ids = set()

        for item in factions_data:
            if isinstance(item, str):
                name = item.strip()
                level = 0
                faction_id = None
            elif isinstance(item, dict):
                faction_id = item.get("id")
                name = item.get("name", "").strip()
                try:
                    level = int(item.get("level", 0))
                except (ValueError, TypeError):
                    level = 0
            else:
                continue

            if not name:
                continue

            if (
                faction_id
                and faction_id in existing_factions
                and faction_id not in retained_ids
            ):
                faction = existing_factions[faction_id]
                update_fields = []
                if faction.name != name:
                    faction.name = name
                    update_fields.append("name")
                if faction.level != level:
                    faction.level = level
                    update_fields.append("level")
                if update_fields:
                    faction.save(update_fields=update_fields)
                retained_ids.add(faction.id)
            else:
                matched_existing = next(
                    (
                        f
                        for fid, f in existing_factions.items()
                        if fid not in retained_ids and f.name == name
                    ),
                    None,
                )
                if matched_existing:
                    if matched_existing.level != level:
                        matched_existing.level = level
                        matched_existing.save(update_fields=["level"])
                    retained_ids.add(matched_existing.id)
                else:
                    faction = Faction.objects.create(
                        name=name, game=game, level=level
                    )
                    retained_ids.add(faction.id)

        for fid, fobj in existing_factions.items():
            if fid not in retained_ids:
                fobj.delete()

    def _sync_win_conditions(self, result_config, win_conditions_data):
        if not win_conditions_data:
            result_config.win_conditions.all().delete()
            return

        existing_wcs = {wc.id: wc for wc in result_config.win_conditions.all()}
        retained_wc_ids = set()

        for wc_index, wc_data in enumerate(win_conditions_data):
            wc_id = wc_data.get("id")
            name = wc_data.get("name", "").strip()
            cond_type = wc_data.get(
                "condition_type",
                wc_data.get("conditionType", WinCondition.WinConditionType.POINTS),
            )
            order = wc_data.get("order", wc_index)

            if wc_id and wc_id in existing_wcs:
                wc = existing_wcs[wc_id]
                wc.name = name
                wc.condition_type = cond_type
                wc.order = order
                wc.save(update_fields=["name", "condition_type", "order"])
                retained_wc_ids.add(wc.id)
            else:
                wc = WinCondition.objects.create(
                    result_config=result_config,
                    name=name,
                    condition_type=cond_type,
                    order=order,
                )
                retained_wc_ids.add(wc.id)

            # Sync WinConditionOptions
            options_data = wc_data.get("options", [])
            existing_opts = {opt.id: opt for opt in wc.options.all()}
            retained_opt_ids = set()

            for opt_index, opt_data in enumerate(options_data):
                if isinstance(opt_data, str):
                    opt_data = {"name": opt_data}
                opt_id = opt_data.get("id")
                opt_name = opt_data.get("name", "").strip()
                opt_order = opt_data.get("order", opt_index)
                if not opt_name:
                    continue

                if opt_id and opt_id in existing_opts:
                    opt = existing_opts[opt_id]
                    opt.name = opt_name
                    opt.order = opt_order
                    opt.save(update_fields=["name", "order"])
                    retained_opt_ids.add(opt.id)
                else:
                    opt = WinConditionOption.objects.create(
                        win_condition=wc, name=opt_name, order=opt_order
                    )
                    retained_opt_ids.add(opt.id)

            for oid, oobj in existing_opts.items():
                if oid not in retained_opt_ids:
                    oobj.delete()

            # Sync TieBreakers
            tb_data_list = wc_data.get(
                "tie_breakers", wc_data.get("tieBreakers", [])
            )
            existing_tbs = {tb.id: tb for tb in wc.tie_breakers.all()}
            retained_tb_ids = set()

            for tb_index, tb_data in enumerate(tb_data_list):
                if isinstance(tb_data, str):
                    tb_data = {"name": tb_data}
                tb_id = tb_data.get("id")
                tb_name = tb_data.get("name", "").strip()
                tb_order = tb_data.get("order", tb_index)
                if not tb_name:
                    continue

                if tb_id and tb_id in existing_tbs:
                    tb = existing_tbs[tb_id]
                    tb.name = tb_name
                    tb.order = tb_order
                    tb.save(update_fields=["name", "order"])
                    retained_tb_ids.add(tb.id)
                else:
                    tb = TieBreaker.objects.create(
                        win_condition=wc, name=tb_name, order=tb_order
                    )
                    retained_tb_ids.add(tb.id)

            for tbid, tbobj in existing_tbs.items():
                if tbid not in retained_tb_ids:
                    tbobj.delete()

        for wcid, wcobj in existing_wcs.items():
            if wcid not in retained_wc_ids:
                wcobj.delete()

    @transaction.atomic
    def create(self, validated_data):
        factions_data = self.initial_data.get("factions", None)
        win_conditions_data = self.initial_data.get(
            "win_conditions", self.initial_data.get("winConditions", None)
        )

        result_config = ResultConfig.objects.create(**validated_data)

        if factions_data is not None:
            self._sync_factions(result_config.game, factions_data)
        if win_conditions_data is not None:
            self._sync_win_conditions(result_config, win_conditions_data)
        elif not result_config.win_conditions.exists():
            WinCondition.objects.create(
                result_config=result_config,
                name="Win" if not result_config.has_points else "Points",
                condition_type=WinCondition.WinConditionType.POINTS,
                order=0,
            )

        return result_config

    @transaction.atomic
    def update(self, instance, validated_data):
        factions_data = self.initial_data.get("factions", None)
        win_conditions_data = self.initial_data.get(
            "win_conditions", self.initial_data.get("winConditions", None)
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if factions_data is not None:
            self._sync_factions(instance.game, factions_data)
        if win_conditions_data is not None:
            self._sync_win_conditions(instance, win_conditions_data)
        if not instance.win_conditions.exists():
            WinCondition.objects.create(
                result_config=instance,
                name="Win" if not instance.has_points else "Points",
                condition_type=WinCondition.WinConditionType.POINTS,
                order=0,
            )

        return instance


class SelectedOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the SelectedOption model.
    Includes validation to ensure choices belong to the correct options.
    """
    game_option = GameOptionSerializer(read_only=True)
    choice = GameOptionChoiceSerializer(read_only=True)

    # Accept IDs for write
    game_option_id = serializers.PrimaryKeyRelatedField(
        queryset=GameOption.objects.all(), source="game_option", write_only=True
    )
    choice_id = serializers.PrimaryKeyRelatedField(
        queryset=GameOptionChoice.objects.all(),
        source="choice",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = SelectedOption
        fields = [
            "id",
            "game_option",
            "choice",
            "value",
            "game_option_id",
            "choice_id",
        ]

    def validate(self, attrs):
        game_option = attrs.get("game_option")
        choice = attrs.get("choice")

        if choice and game_option and choice.option_id != game_option.id:
            raise serializers.ValidationError(
                {"choice_id": "Choice must belong to the selected game option."}
            )

        return attrs


class FullGameOptionChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    ref = serializers.CharField(write_only=True, required=False)
    order = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = GameOptionChoice
        fields = ["id", "ref", "name", "order"]


class FullGameOptionAvailabilityConditionWriteSerializer(serializers.Serializer):
    depends_on_option_ref = serializers.CharField()
    expected_value = serializers.BooleanField(required=False, allow_null=True)
    expected_choice_ref = serializers.CharField(required=False, allow_null=True)
    negate = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        expected_value = attrs.get("expected_value", None)
        expected_choice_ref = attrs.get("expected_choice_ref", None)

        # Exactly one of expected_value / expected_choice_ref must be provided
        if (expected_value is None) == (expected_choice_ref is None):
            raise serializers.ValidationError(
                "Provide exactly one of expected_value or expected_choice_ref."
            )
        return attrs


class FullGameOptionAvailabilityGroupWriteSerializer(serializers.Serializer):
    conditions = FullGameOptionAvailabilityConditionWriteSerializer(many=True)


class FullGameOptionAvailabilityConditionReadSerializer(serializers.ModelSerializer):
    """
    Read format uses real DB ids (because refs are not stored).
    """

    depends_on_option_id = serializers.IntegerField()
    expected_choice_id = serializers.IntegerField(allow_null=True)

    depends_on_option_name = serializers.CharField(
        source="depends_on_option.name", read_only=True
    )
    expected_choice_name = serializers.CharField(
        source="expected_choice.name", allow_null=True, read_only=True
    )

    class Meta:
        model = GameOptionAvailabilityCondition
        fields = [
            "id",
            "depends_on_option_id",
            "depends_on_option_name",
            "expected_value",
            "expected_choice_id",
            "expected_choice_name",
            "negate",
        ]


class FullGameOptionAvailabilityGroupReadSerializer(serializers.ModelSerializer):
    conditions = FullGameOptionAvailabilityConditionReadSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = GameOptionAvailabilityGroup
        fields = ["id", "conditions"]


class AvailabilityGroupsField(serializers.Field):
    """
    Single JSON key `availability_groups` that supports:
      - write: ref-based format (validated by *Write* serializers)
      - read: DB-backed format (serialized by *Read* serializers)
    """

    def to_internal_value(self, data):
        s = FullGameOptionAvailabilityGroupWriteSerializer(data=data, many=True)
        s.is_valid(raise_exception=True)
        return s.validated_data

    def to_representation(self, value):
        # `value` will be a RelatedManager (option.availability_groups) or iterable
        qs = value.all() if hasattr(value, "all") else value
        return FullGameOptionAvailabilityGroupReadSerializer(qs, many=True).data


class FullGameOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    # Client-only reference used for linking conditions during create/update
    ref = serializers.CharField(write_only=True, required=False)

    order = serializers.IntegerField(required=False, default=0)
    choices = FullGameOptionChoiceSerializer(many=True, required=False)

    # IMPORTANT: same field name for read + write
    availability_groups = AvailabilityGroupsField(required=False)

    class Meta:
        model = GameOption
        fields = [
            "id",
            "ref",
            "name",
            "has_choices",
            "choices",
            "availability_groups",
            "order",
        ]
