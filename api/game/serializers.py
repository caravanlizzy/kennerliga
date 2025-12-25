from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption, BanDecision, GameOptionAvailabilityGroup, GameOptionAvailabilityCondition
from league.models import League
from user.models import PlayerProfile
from user.service import get_profile_by_username, find_users_current_league


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class GameOptionSerializer(ModelSerializer):
    class Meta:
        model = GameOption
        fields = '__all__'


class GameOptionChoiceSerializer(ModelSerializer):
    class Meta:
        model = GameOptionChoice
        fields = '__all__'


class FactionSerializer(ModelSerializer):
    class Meta:
        model = Faction
        fields = '__all__'


class TieBreakerSerializer(ModelSerializer):
    class Meta:
        model = TieBreaker
        fields = '__all__'


class ResultConfigSerializer(ModelSerializer):
    starting_points_system = serializers.SerializerMethodField()

    class Meta:
        model = ResultConfig
        fields = '__all__'

    def get_starting_points_system(self, obj):
        return obj.starting_points_system.code if obj.starting_points_system else None



class StartingPointSystemSerializer(ModelSerializer):
    class Meta:
        model = StartingPointSystem
        fields = '__all__'


class PlatformSerializer(ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'


class SelectedOptionSerializer(serializers.ModelSerializer):
    game_option = GameOptionSerializer(read_only=True)
    choice = GameOptionChoiceSerializer(read_only=True)

    # Accept IDs for write
    game_option_id = serializers.PrimaryKeyRelatedField(
        queryset=GameOption.objects.all(), source='game_option', write_only=True
    )
    choice_id = serializers.PrimaryKeyRelatedField(
        queryset=GameOptionChoice.objects.all(), source='choice', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = SelectedOption
        fields = [
            'id',
            'game_option',
            'choice',
            'value',
            'game_option_id',
            'choice_id',
        ]


class SelectedGameSerializer(serializers.ModelSerializer):
    # game_name is read only
    game_name = serializers.SerializerMethodField()
    selected_options = SelectedOptionSerializer(many=True)

    profile = serializers.PrimaryKeyRelatedField(
        queryset=PlayerProfile.objects.all(),
        write_only=True,
        required=False,
    )
    league = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(),
        write_only=True,
        required=False,
    )

    manage_only = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = SelectedGame
        fields = ['id', 'game', 'game_name', 'selected_options', 'league', 'profile', 'manage_only']

    def get_game_name(self, obj):
        return obj.game.name if obj.game else None

    def set_player_and_league(self, validated_data):
        # Set player
        profile = validated_data.pop('profile', None)
        validated_data['profile'] = PlayerProfile.objects.get(id=profile)
        # Set league
        league = validated_data.pop('league', None)
        validated_data['league'] = League.objects.get(id=league)
        return validated_data

    def create(self, validated_data):
        # Remove write-only fields that shouldn't go to the model
        validated_data.pop('manage_only', None)
        # Create SelectedGame and SelectedOption instances
        selected_options_data = validated_data.pop('selected_options')

        # Create SelectedGame instance
        selected_game = SelectedGame.objects.create(**validated_data)

        # Create SelectedOption instances
        for option_data in selected_options_data:
            SelectedOption.objects.create(selected_game=selected_game, **option_data)

        return selected_game

    def update(self, instance, validated_data):
        # Remove write-only field
        validated_data.pop('manage_only', None)
        selected_options_data = validated_data.pop('selected_options', None)

        # Update player and league if provided
        instance.profile = validated_data.get('profile', instance.profile)
        instance.league = validated_data.get('league', instance.league)
        instance.game = validated_data.get('game', instance.game)
        instance.save()

        # Update selected options (no id in payload)
        if selected_options_data is not None:
            for option_data in selected_options_data:
                game_option = option_data.get('game_option')
                if not game_option:
                    # optionally raise ValidationError here instead of skipping
                    continue

                # assuming one SelectedOption per (selected_game, game_option)
                option_instance, _ = SelectedOption.objects.get_or_create(
                    selected_game=instance,
                    game_option=game_option,
                )

                option_instance.choice = option_data.get('choice', option_instance.choice)
                option_instance.value = option_data.get('value', option_instance.value)
                option_instance.save()

        return instance


class FullGameOptionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameOptionChoice
        fields = ['id', 'name']


class FullGameOptionSerializer(serializers.ModelSerializer):
    choices = FullGameOptionChoiceSerializer(many=True)

    class Meta:
        model = GameOption
        fields = [
            'id', 'name', 'has_choices', 'only_if_option',
            'only_if_choice', 'only_if_value', 'choices'
        ]


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

    depends_on_option_name = serializers.CharField(source="depends_on_option.name", read_only=True)
    expected_choice_name = serializers.CharField(source="expected_choice.name", allow_null=True, read_only=True)

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
    conditions = FullGameOptionAvailabilityConditionReadSerializer(many=True, read_only=True)

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


class FullGameOptionChoiceSerializer(serializers.ModelSerializer):
    # Client-only reference used for linking conditions during create/update
    ref = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = GameOptionChoice
        fields = ['id', 'ref', 'name']


class FullGameOptionSerializer(serializers.ModelSerializer):
    # Client-only reference used for linking conditions during create/update
    ref = serializers.CharField(write_only=True, required=False)

    choices = FullGameOptionChoiceSerializer(many=True, required=False)

    # IMPORTANT: same field name for read + write
    availability_groups = AvailabilityGroupsField(required=False)

    class Meta:
        model = GameOption
        fields = [
            'id',
            'ref',
            'name',
            'has_choices',
            'choices',
            'availability_groups',
        ]


class FullGameSerializer(serializers.ModelSerializer):
    options = FullGameOptionSerializer(many=True)

    class Meta:
        model = Game
        fields = ['id', 'name', 'platform', 'options']

    @transaction.atomic
    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        game = Game.objects.create(**validated_data)

        option_by_ref = {}
        choice_by_ref = {}
        deferred_groups = []  # list[(option_obj, availability_groups_data)]

        # Pass 1: create options + choices, build ref maps
        for option_payload in options_data:
            choices_data = option_payload.pop('choices', [])
            availability_groups_data = option_payload.pop('availability_groups', [])
            option_ref = option_payload.pop('ref', None)
            order = option_payload.pop('order', 0)

            option = GameOption.objects.create(game=game, order=order, **option_payload)

            if option_ref:
                if option_ref in option_by_ref:
                    raise serializers.ValidationError({"options": f"Duplicate option ref: {option_ref}"})
                option_by_ref[option_ref] = option

            for choice_payload in choices_data:
                choice_ref = choice_payload.pop('ref', None)
                ch_order = choice_payload.pop('order', 0)
                choice = GameOptionChoice.objects.create(option=option, order=ch_order, **choice_payload)

                if choice_ref:
                    if choice_ref in choice_by_ref:
                        raise serializers.ValidationError({"options": f"Duplicate choice ref: {choice_ref}"})
                    choice_by_ref[choice_ref] = choice

            deferred_groups.append((option, availability_groups_data))

        # Pass 2: create availability groups + conditions
        self._create_availability_logic(deferred_groups, option_by_ref, choice_by_ref)

        return game

    @transaction.atomic
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])

        instance.name = validated_data.get('name', instance.name)
        instance.platform = validated_data.get('platform', instance.platform)
        instance.save()

        existing_options_by_id = {opt.id: opt for opt in instance.options.all()}

        option_by_ref = {}
        choice_by_ref = {}
        seen_option_ids = set()
        seen_choice_ids_by_option_id = {}
        deferred_groups = []

        # 1) Upsert options + choices
        for option_payload in options_data:
            choices_data = option_payload.pop('choices', [])
            availability_groups_data = option_payload.pop('availability_groups', [])
            option_ref = option_payload.pop('ref', None)
            option_id = option_payload.get('id')
            order = option_payload.pop('order', 0)

            if option_id:
                option = existing_options_by_id.get(option_id)
                if option is None:
                    raise serializers.ValidationError({"options": f"Option id={option_id} unknown."})
                option.name = option_payload.get('name', option.name)
                option.has_choices = option_payload.get('has_choices', option.has_choices)
                option.order = order
                option.save()
            else:
                option = GameOption.objects.create(game=instance, order=order, **option_payload)

            seen_option_ids.add(option.id)
            if option_ref:
                option_by_ref[option_ref] = option

            existing_choices_by_id = {c.id: c for c in option.choices.all()}
            seen_choice_ids = set()

            for choice_payload in choices_data:
                choice_ref = choice_payload.pop('ref', None)
                choice_id = choice_payload.get('id')
                ch_order = choice_payload.pop('order', 0)

                if choice_id:
                    choice = existing_choices_by_id.get(choice_id)
                    if choice:
                        choice.name = choice_payload.get('name', choice.name)
                        choice.order = ch_order
                        choice.save()
                else:
                    choice = GameOptionChoice.objects.create(option=option, order=ch_order, **choice_payload)

                if choice:
                    seen_choice_ids.add(choice.id)
                    if choice_ref:
                        choice_by_ref[choice_ref] = choice

            seen_choice_ids_by_option_id[option.id] = seen_choice_ids
            deferred_groups.append((option, availability_groups_data))

        # 2) Delete options/choices missing from payload
        instance.options.exclude(id__in=seen_option_ids).delete()
        for opt_id, keep_choice_ids in seen_choice_ids_by_option_id.items():
            GameOptionChoice.objects.filter(option_id=opt_id).exclude(id__in=keep_choice_ids).delete()

        # 3) Replace availability groups
        for option, _ in deferred_groups:
            option.availability_groups.all().delete()

        self._create_availability_logic(deferred_groups, option_by_ref, choice_by_ref)

        return instance

    def _create_availability_logic(self, deferred_groups, option_by_ref, choice_by_ref):
        """Internal helper to process availability groups and conditions."""
        for option, groups_data in deferred_groups:
            for group_data in groups_data:
                group = GameOptionAvailabilityGroup.objects.create(option=option)

                for cond in group_data.get("conditions", []):
                    depends_on_ref = cond.get("depends_on_option_ref")
                    if not depends_on_ref:
                        raise serializers.ValidationError({"options": "Condition missing depends_on_option_ref."})

                    depends_on_option = option_by_ref.get(depends_on_ref)
                    if not depends_on_option:
                        raise serializers.ValidationError(
                            {"options": f"Unknown depends_on_option_ref: {depends_on_ref}"})

                    expected_value = cond.get("expected_value")
                    expected_choice_ref = cond.get("expected_choice_ref")
                    negate = bool(cond.get("negate", False))

                    expected_choice = None
                    if expected_choice_ref:
                        expected_choice = choice_by_ref.get(expected_choice_ref)
                        if not expected_choice:
                            raise serializers.ValidationError({"options": f"Unknown choice ref: {expected_choice_ref}"})

                    GameOptionAvailabilityCondition.objects.create(
                        group=group,
                        depends_on_option=depends_on_option,
                        expected_value=expected_value if expected_choice is None else None,
                        expected_choice=expected_choice,
                        negate=negate,
                    )


class BanDecisionSerializer(serializers.ModelSerializer):
    player_banning = serializers.PrimaryKeyRelatedField(
        queryset=PlayerProfile.objects.all()
    )
    player_banning_name = serializers.CharField(
        source='player_banning.profile_name', read_only=True
    )

    # Client sends/receives `selected_game_id`, but we write to model field `selected_game`
    selected_game_id = serializers.PrimaryKeyRelatedField(
        source='selected_game',
        queryset=SelectedGame.objects.all(),
        required=False,
        allow_null=True
    )
    selected_game_name = serializers.CharField(
        source='selected_game.game.name', read_only=True
    )

    league = serializers.PrimaryKeyRelatedField(queryset=League.objects.all(), required=True)

    class Meta:
        model = BanDecision
        fields = [
            'id',
            'player_banning', 'player_banning_name',
            'selected_game_id', 'selected_game_name',
            'league',
            'created_at',
        ]
        read_only_fields = [
            'id', 'created_at',
            'player_banning_name',
            'selected_game_name',
        ]

    def validate(self, attrs):
        league = attrs.get('league') or getattr(self.instance, 'league', None)
        selected_game = attrs.get('selected_game')  # populated via source='selected_game'

        if selected_game and league and selected_game.league_id != league.id:
            raise serializers.ValidationError({
                'selected_game_id': 'Selected game must belong to the same league.'
            })
        return attrs

    def create(self, validated_data):
        obj, _ = BanDecision.objects.update_or_create(
            league=validated_data['league'],
            player_banning=validated_data['player_banning'],
            defaults={'selected_game': validated_data.get('selected_game')}
        )
        return obj
