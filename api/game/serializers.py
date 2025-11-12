from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption, BanDecision
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
    class Meta:
        model = ResultConfig
        fields = '__all__'


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
            'game_option',  # nested, read-only
            'choice',  # nested, read-only
            'value',
            'game_option_id',  # ID, write-only
            'choice_id',  # ID, write-only
        ]


class SelectedGameSerializer(serializers.ModelSerializer):
    game_name = serializers.SerializerMethodField()
    selected_options = SelectedOptionSerializer(many=True)

    profile_id = serializers.PrimaryKeyRelatedField(
        source='player',
        queryset=PlayerProfile.objects.all(),
        write_only=True,
        required=False,
    )
    league_id = serializers.PrimaryKeyRelatedField(
        source='league',
        queryset=League.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = SelectedGame
        fields = ['id', 'game', 'game_name', 'selected_options', 'league_id', 'profile_id']

    def get_game_name(self, obj):
        return obj.game.name if obj.game else None

    def set_player_and_league(self, validated_data):
        # Set player
        profile_id = validated_data.pop('profile_id', None)
        validated_data['player'] = PlayerProfile.objects.get(id=profile_id)
        # Set league
        league_id = validated_data.pop('league_id', None)
        validated_data['league'] = League.objects.get(id=league_id)
        return validated_data

    def create(self, validated_data):
        # Create SelectedGame and SelectedOption instances
        selected_options_data = validated_data.pop('selected_options')
        selected_game = SelectedGame.objects.create(**validated_data)
        for option_data in selected_options_data:
            SelectedOption.objects.create(selected_game=selected_game, **option_data)
        return selected_game

    def update(self, instance, validated_data):
        validated_data = self.set_player_and_league(validated_data)

        # Update other fields and selected options
        instance.game = validated_data.get('game', instance.game)
        instance.save()

        selected_options_data = validated_data.pop('selected_options', None)
        if selected_options_data:
            for option_data in selected_options_data:
                option_id = option_data.get('id')
                if option_id:
                    option_instance = SelectedOption.objects.get(id=option_id, selected_game=instance)
                    option_instance.choice = option_data.get('choice', option_instance.choice)
                    option_instance.value = option_data.get('value', option_instance.value)
                    option_instance.save()
                else:
                    SelectedOption.objects.create(selected_game=instance, **option_data)

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


class FullGameSerializer(serializers.ModelSerializer):
    options = FullGameOptionSerializer(many=True)

    class Meta:
        model = Game
        fields = ['id', 'name', 'platform', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        game = Game.objects.create(**validated_data)

        for option_data in options_data:
            choices_data = option_data.pop('choices', [])
            option = GameOption.objects.create(game=game, **option_data)
            for choice_data in choices_data:
                GameOptionChoice.objects.create(option=option, **choice_data)

        return game

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])

        instance.name = validated_data.get('name', instance.name)
        instance.platform = validated_data.get('platform', instance.platform)
        instance.save()

        # Replace all existing options and choices (naive approach)
        instance.options.all().delete()

        for option_data in options_data:
            choices_data = option_data.pop('choices', [])
            option = GameOption.objects.create(game=instance, **option_data)
            for choice_data in choices_data:
                GameOptionChoice.objects.create(option=option, **choice_data)

        return instance


class BanDecisionSerializer(serializers.ModelSerializer):
    player_banning = serializers.PrimaryKeyRelatedField(read_only=True)
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
    username = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = BanDecision
        fields = [
            'id',
            'player_banning', 'player_banning_name',
            'selected_game_id', 'selected_game_name',  # <-- use _id here
            'league',
            'created_at',
            'username',
        ]
        read_only_fields = [
            'id', 'created_at',
            'player_banning', 'player_banning_name',
            'selected_game_name',
        ]

    def validate(self, attrs):
        print("Raw client data:", self.initial_data)
        print("Validated so far:", attrs)
        league = attrs.get('league') or getattr(self.instance, 'league', None)
        selected_game = attrs.get('selected_game')  # populated via source='selected_game'

        if selected_game and league and selected_game.league_id != league.id:
            raise serializers.ValidationError({
                'selected_game_id': 'Selected game must belong to the same league.'
            })
        return attrs

    def create(self, validated_data):
        print("Final validated_data in create:", validated_data)
        username = validated_data.pop('username')
        validated_data['player_banning'] = get_profile_by_username(username)
        obj, _ = BanDecision.objects.update_or_create(
            league=validated_data['league'],
            player_banning=validated_data['player_banning'],
            defaults={'selected_game': validated_data.get('selected_game')}
        )
        return obj
