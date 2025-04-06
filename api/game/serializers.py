from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from game.models import Game, GameOption, GameOptionChoice, Faction, TieBreaker, ResultConfig, StartingPointSystem, \
    Platform, SelectedGame, SelectedOption
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
    class Meta:
        model = SelectedOption
        fields = ['id', 'game_option', 'choice', 'value']


class SelectedGameSerializer(serializers.ModelSerializer):
    selected_options = SelectedOptionSerializer(many=True)

    # Optional write-only fields that aren't part of the model
    leagueId = serializers.IntegerField(write_only=True, required=False)
    playerProfileId = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = SelectedGame
        fields = ['id', 'game', 'selected_options', 'leagueId', 'playerProfileId']

    def set_player_and_league(self, validated_data):
        # Set player
        profile_id = validated_data.pop('playerProfileId', None)
        validated_data['player'] = (PlayerProfile.objects.get(id=profile_id)
                                    if profile_id
                                    else get_profile_by_username(self.context.get('request').user.username))

        # Set league if provided
        league_id = validated_data.pop('leagueId', None)
        if league_id:
            validated_data['league'] =  League.objects.get(id=league_id)
        else:
            validated_data['league'] = find_users_current_league(validated_data['player'])
        return validated_data

    def create(self, validated_data):
        validated_data = self.set_player_and_league(validated_data)
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


# Approach to have a single response for game only instaed of batching down the properties

class FullGameOptionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameOptionChoice
        fields = ['id', 'name']

class FullGameOptionSerializer(serializers.ModelSerializer):
    choices = GameOptionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = GameOption
        fields = [
            'id', 'name', 'has_choices', 'only_if_option',
            'only_if_choice', 'only_if_value', 'choices'
        ]

class FullGameSerializer(serializers.ModelSerializer):
    options = FullGameOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'name', 'platform', 'options']